import discord
from discord.ext import commands
import requests
from flask import Flask
from threading import Thread

# ── Render Ke Liye Dummy Web Server ──
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
TOKEN    = "MTU0NTM4MTc1NzgyNDc5ODc4MQ.GKpawi._DETjEXpyr8D0lV2_ySzBFiSMmVvFvCjrd8TwI"
GUILD_ID = 1525181999147388958  # यहाँ अपना Server ID डालें

API_URL  = "https://auth.terminalx999.online/api_admin.php"
API_KEY  = "TX999_406e27c982b44901dc3d615d1a64b056d569273fc1ba45cbeca94fee0e880a84"
APP_ID   = "9f087d585fbd666572fc24b7"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot Online ho gaya hai: {bot.user.name}")
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"{len(synced)} Slash commands sync ho gaye hain.")
    except Exception as e:
        print(f"Sync error: {e}")

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
                    await interaction.followup.send(f"✓ Action **{action}** complete for key: `{key}`", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Failed: {resp.json().get('message')}", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="genkey", description="Generate a license key remotely.")
@discord.app_commands.choices(package=[
        discord.app_commands.Choice(name="BASIC PANEL", value="e52c1515c53453b85d0d4e87"),
        discord.app_commands.Choice(name="AIMSILENT EXE", value="affc8da8fd5ace99981ab877"),
        discord.app_commands.Choice(name="UID BYPASS", value="cb921031dc43197e8ccb6828"),
        discord.app_commands.Choice(name="EXTERNAL PANEL", value="3d1c6c948b4715fbd2fada2d"),
        discord.app_commands.Choice(name="PVT AIMKILL", value="d4f0ce93349f236711344cb5"),
        discord.app_commands.Choice(name="VAULT PANEL", value="154d1edaddd7203fbfd847f4")
    ])
@discord.app_commands.describe(
    package="Select package",
    days="Validity in days (0 = lifetime)",
    count="Number of keys (max 100)"
)
async def genkey(interaction: discord.Interaction, package: discord.app_commands.Choice[str], days: int = 30, count: int = 1):
    await interaction.response.defer(ephemeral=False)
    payload = {
        "api_key": API_KEY, 
        "action": "generate_key", 
        "app_id": APP_ID, 
        "package_id": package.value, 
        "days": days, 
        "count": count
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
        data = resp.json()
        if data.get("success"):
            keys = data.get("data", {}).get("keys", [])
            dur = "Lifetime" if days == 0 else f"{days} Days"
            embed = discord.Embed(
                title="🔑 Keys Generated", 
                description=f"**Package:** {package.name}\n**Count:** {len(keys)}\n**Duration:** {dur}", 
                color=0xdc2626
            )
            embed.add_field(name="Keys", value="\n".join([f"`{k}`" for k in keys]), inline=False)
            
            view = discord.ui.View()
            if len(keys) == 1:
                view.add_item(discord.ui.Button(label="Reset HWID", custom_id=f"reset_hwid:{keys[0]}", style=discord.ButtonStyle.primary))
                view.add_item(discord.ui.Button(label="Delete", custom_id=f"delete_key:{keys[0]}", style=discord.ButtonStyle.danger))
            
            await interaction.followup.send(embed=embed, view=view if len(keys) == 1 else None)
        else:
            await interaction.followup.send(f"❌ {data.get('message')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ {str(e)}", ephemeral=True)

# Web server start aur bot run
keep_alive()
bot.run(TOKEN)
