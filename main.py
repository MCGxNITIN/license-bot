import os
import requests
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread

# ── Render Dummy Web Server ──
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# TerminalX999 - License Key Discord Bot
# ==========================================
# Variables ko Render Environment Variables se read karein
# Variables ko Render Environment Variables se read karein
TOKEN    = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "1525181999147388958"))

API_URL  = "https://auth.terminalx999.online/api_admin.php"
API_KEY  = os.getenv("API_KEY")
APP_ID   = os.getenv("APP_ID")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot Online ho gaya hai: {bot.user.name}")
    try:
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"{len(synced)} Slash commands sync ho gaye hain.")
        else:
            synced = await bot.tree.sync()
            print(f"Global commands sync ho gaye hain: {len(synced)}")
    except Exception as e:
        print(f"Sync error: {e}")

# Button Interactions (HWID Reset, Ban, Unban, Pause, Unpause, Delete)
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id", "")
        if ":" in custom_id:
            action, key = custom_id.split(":", 1)
            await interaction.response.defer(ephemeral=True)
            try:
                resp = requests.post(API_URL, json={"api_key": API_KEY, "action": action, "key": key}, timeout=10)
                res_data = resp.json()
                if res_data.get("success"):
                    await interaction.followup.send(f"✓ Action **{action}** complete for key: `{key}`", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Failed: {res_data.get('message')}", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# 1. GENERATE KEY COMMAND
@bot.tree.command(name="genkey", description="Generate a license key remotely.")
@app_commands.choices(package=[
    app_commands.Choice(name="BASIC PANEL", value="e52c1515c53453b85d0d4e87"),
    app_commands.Choice(name="AIMSILENT EXE", value="affc8da8fd5ace99981ab877"),
    app_commands.Choice(name="UID BYPASS", value="cb921031dc43197e8ccb6828"),
    app_commands.Choice(name="EXTERNAL PANEL", value="3d1c6c948b4715fbd2fada2d"),
    app_commands.Choice(name="PVT AIMKILL", value="d4f0ce93349f236711344cb5"),
    app_commands.Choice(name="VAULT PANEL", value="154d1edaddd7203fbfd847f4")
])
@app_commands.describe(
    package="Select package",
    days="Validity in days (0 = lifetime)",
    count="Number of keys (max 100)",
    note="Add a note/description for the key"
)
async def genkey(interaction: discord.Interaction, package: app_commands.Choice[str], days: int = 30, count: int = 1, note: str = "No note"):
    await interaction.response.defer(ephemeral=False)
    payload = {
        "api_key": API_KEY, 
        "action": "generate_key", 
        "app_id": APP_ID, 
        "package_id": package.value, 
        "days": days, 
        "count": count,
        "note": note
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
        data = resp.json()
        if data.get("success"):
            keys = data.get("data", {}).get("keys", [])
            dur = "Lifetime" if days == 0 else f"{days} Days"
            embed = discord.Embed(
                title="🔑 Keys Generated", 
                description=f"**Package:** {package.name}\n**Count:** {len(keys)}\n**Duration:** {dur}\n**Note:** {note}", 
                color=0x22c55e
            )
            embed.add_field(name="Keys", value="\n".join([f"`{k}`" for k in keys]), inline=False)
            
            view = discord.ui.View()
            if len(keys) == 1:
                view.add_item(discord.ui.Button(label="Reset HWID", custom_id=f"reset_hwid:{keys[0]}", style=discord.ButtonStyle.primary))
                view.add_item(discord.ui.Button(label="Ban", custom_id=f"ban_key:{keys[0]}", style=discord.ButtonStyle.danger))
                view.add_item(discord.ui.Button(label="Unban", custom_id=f"unban_key:{keys[0]}", style=discord.ButtonStyle.success))
                view.add_item(discord.ui.Button(label="Pause", custom_id=f"pause_key:{keys[0]}", style=discord.ButtonStyle.secondary))
                view.add_item(discord.ui.Button(label="Unpause", custom_id=f"unpause_key:{keys[0]}", style=discord.ButtonStyle.success))
            
            await interaction.followup.send(embed=embed, view=view if len(keys) == 1 else None)
        else:
            await interaction.followup.send(f"❌ {data.get('message')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ {str(e)}", ephemeral=True)

# Helper Function API Actions ke liye
async def execute_key_action(interaction: discord.Interaction, action: str, key: str):
    await interaction.response.defer(ephemeral=True)
    try:
        resp = requests.post(API_URL, json={"api_key": API_KEY, "action": action, "key": key}, timeout=10)
        data = resp.json()
        if data.get("success"):
            await interaction.followup.send(f"✅ Success: Key `{key}` executed **{action}** successfully.", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {data.get('message')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# 2. HWID RESET COMMAND
@bot.tree.command(name="resetkey", description="Reset HWID for a specific key.")
async def resetkey(interaction: discord.Interaction, key: str):
    await execute_key_action(interaction, "reset_hwid", key)

# 3. BAN KEY COMMAND
@bot.tree.command(name="bankey", description="Ban a specific key.")
async def bankey(interaction: discord.Interaction, key: str):
    await execute_key_action(interaction, "ban_key", key)

# 4. UNBAN KEY COMMAND
@bot.tree.command(name="unbankey", description="Unban a specific key.")
async def unbankey(interaction: discord.Interaction, key: str):
    await execute_key_action(interaction, "unban_key", key)

# 5. PAUSE KEY COMMAND
@bot.tree.command(name="pausekey", description="Pause a specific key.")
async def pausekey(interaction: discord.Interaction, key: str):
    await execute_key_action(interaction, "pause_key", key)

# 6. UNPAUSE KEY COMMAND
@bot.tree.command(name="unpausekey", description="Unpause a specific key.")
async def unpausekey(interaction: discord.Interaction, key: str):
    await execute_key_action(interaction, "unpause_key", key)

# Web server start aur bot run
keep_alive()
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_TOKEN Environment Variable nahi mila! Environment setup check karein.")
