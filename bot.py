import os
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
import threading
import datetime
from dotenv import load_dotenv
import importlib
import links  # import links module

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

PLATFORM_EMOJIS = {
    "win": "🪟",
    "linux": "🐧",
    "mac": "🍎",
    "android": "🤖",
    "ios": "📱"
}

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
keep_alive_app = Flask("KeepAlive")

# -------------------------
# Keep-alive server
# -------------------------
@keep_alive_app.route("/")
def home():
    return "I am alive!", 200

def run_keep_alive():
    keep_alive_app.run(host="0.0.0.0", port=8000)

threading.Thread(target=run_keep_alive, daemon=True).start()

# -------------------------
# Autocomplete
# -------------------------
async def app_autocomplete(interaction: discord.Interaction, current: str):
    importlib.reload(links)  # reload links dynamically
    APPS = links.APPS

    apps = sorted([a for a in APPS if current.lower() in a])[:25]
    choices = [app_commands.Choice(name=a, value=a) for a in apps]
    try:
        await interaction.response.autocomplete(choices)
    except discord.errors.NotFound:
        pass

# -------------------------
# Thumbnail helper
# -------------------------
def get_app_thumbnail(appname: str):
    importlib.reload(links)
    ICON_BASE_URL = links.ICON_BASE_URL
    return f"{ICON_BASE_URL}{appname.lower()}.png"

# -------------------------
# /get command
# -------------------------
@bot.tree.command(name="get", description="Get a download link for an app")
@app_commands.describe(appname="Name of the app")
@app_commands.autocomplete(appname=app_autocomplete)
async def get(interaction: discord.Interaction, appname: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {interaction.user} typed: /get {appname}")

    await interaction.response.defer(ephemeral=True)

    importlib.reload(links)
    APPS = links.APPS

    app_assets = APPS.get(appname.lower())
    if not app_assets:
        await interaction.followup.send(f"❌ No files found for **{appname}**.")
        return

    view = discord.ui.View()
    for asset in app_assets:
        emoji = PLATFORM_EMOJIS.get(asset['platform'], "")
        label = f"{emoji} {asset['platform']} ({asset['version']})"
        view.add_item(discord.ui.Button(label=label, style=discord.ButtonStyle.link, url=asset["url"]))

    embed = discord.Embed(
        title=f"💾 Downloads for {appname.capitalize()}",
        description="Select your platform below to start the download:",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=get_app_thumbnail(appname))
    embed.set_footer(text="Direct downloads")
    builds_text = "\n".join(f"{a['version']} — {a['platform']}" for a in app_assets)
    embed.add_field(name="Available Builds", value=builds_text, inline=False)

    await interaction.followup.send(embed=embed, view=view)

# -------------------------
# Bot ready
# -------------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    print("Bot is ready!")
    activity = discord.Activity(type=discord.ActivityType.playing, name="crack.exe")
    await bot.change_presence(activity=activity)

bot.run(TOKEN)
