import discord
from discord.ext import commands
import requests
import os
from flask import Flask
from threading import Thread

# ── Render Web Service Port Binding Fix ──
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# TerminalX999 - Standard License Key Discord Bot (Python)
# ==========================================
# NOTE: Security ke liye Discord Developer Portal par jaakar TOKEN Reset kar lein!
TOKEN    = "MTU0NjkwNjMwMjQ0ODY3Mjc5OA.Grvgdc.q2RGqk_wFPtk62yN1hxXOuOFTa8kChtq_qHIKA"
GUILD_ID = 1525181999147388958

API_URL  = "https://auth.terminalx999.online/api_admin.php"
API_KEY  = "TX999_1fc0134c4c418cf9f0817f355ac10cf7e5f73cf899a83bbf4731e4eec3929870"
APP_ID   = "9f087d585fbd666572fc24b7"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id", "")
        if ":" in custom_id:
            action, key = custom_id.split(":", 1)
            await interaction.response.defer(ephemeral=True)
            try:
                resp = requests.post(API_URL, json={"api_key": API_KEY, "action": action, "key": key}, timeout=10)
                if resp.json().get("success"):
                    await interaction.followup.send(f"✓ Action **{action}** completed for key: `{key}`", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Failed: {resp.json().get('message')}", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="genkey", description="Generate a license key remotely.")
@discord.app_commands.choices(package=[
        discord.app_commands.Choice(name="LIB BYPASS", value="db3b90e8134ec738b94a9b05")
    ])
@discord.app_commands.describe(
    package="Select the target package",
    days="Number of validity days (0 = lifetime)",
    count="Number of keys to generate (max 100)"
)
async def genkey(interaction: discord.Interaction, package: str, days: int = 30, count: int = 1):
    await interaction.response.defer(ephemeral=False)
    payload = {"api_key": API_KEY, "action": "generate_key", "app_id": APP_ID, "package_id": package, "days": days, "count": count}
    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
        data = resp.json()
        if data.get("success"):
            keys = data.get("data", {}).get("keys", [])
            dur = "Lifetime" if days == 0 else f"{days} Days"
            embed = discord.Embed(title="🔑 Keys Generated", description=f"Generated {len(keys)} key(s)\nDuration: {dur}", color=0xdc2626)
            embed.add_field(name="Keys", value="\n".join([f"`{k}`" for k in keys]))
            
            if len(keys) == 1:
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label="Reset", custom_id=f"reset_hwid:{keys[0]}"))
                view.add_item(discord.ui.Button(label="Delete", custom_id=f"delete_key:{keys[0]}", style=discord.ButtonStyle.danger))
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ {data.get('message')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

keep_alive()
bot.run(TOKEN)
