import os
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
import threading
import datetime
import aiohttp
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GITHUB_USER = "angel2rider"
GITHUB_REPO = "FETCHER"
RELEASE_TAG = "v1.0"

ICON_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/icons/"

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
assets_cache = []
keep_alive_app = Flask("KeepAlive")

# Platform emojis
PLATFORM_EMOJIS = {
    "win": "🪟",
    "linux": "🐧",
    "mac": "🍎",
    "android": "🤖",
    "ios": "📱"
}

# -------------------------
# GitHub release fetching
# -------------------------
async def refresh_assets():
    global assets_cache
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/tags/{RELEASE_TAG}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                data = await r.json()
                assets_cache = []
                for asset in data["assets"]:
                    filename = asset["name"]
                    name_part, ext = os.path.splitext(filename)
                    first_dash = name_part.find("-")
                    last_dash = name_part.rfind("-")
                    if first_dash == -1 or last_dash == -1 or first_dash == last_dash:
                        continue
                    app_name = name_part[:first_dash].lower()
                    version = name_part[first_dash+1:last_dash]
                    platform_ext = name_part[last_dash+1:].lower()
                    assets_cache.append({
                        "app": app_name,
                        "version": version,
                        "platform_ext": platform_ext,
                        "download_url": asset["browser_download_url"]
                    })
            else:
                assets_cache = []

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
    await refresh_assets()
    apps = sorted({a["app"] for a in assets_cache if current.lower() in a["app"]})[:25]
    choices = [app_commands.Choice(name=a, value=a) for a in apps]
    try:
        await interaction.response.autocomplete(choices)
    except discord.errors.NotFound:
        pass

# -------------------------
# Thumbnail helper
# -------------------------
def get_app_thumbnail(appname: str):
    return f"{ICON_BASE_URL}{appname.lower()}.png"

# -------------------------
# /get command
# -------------------------
@bot.tree.command(name="get", description="Get a download link for an app")
@app_commands.describe(appname="Name of the app")
@app_commands.autocomplete(appname=app_autocomplete)
async def get(interaction: discord.Interaction, appname: str):
    # Log user + input
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {interaction.user} typed: /get {appname}")

    # Safe defer
    try:
        await interaction.response.defer(ephemeral=True)
    except discord.errors.NotFound:
        pass

    await refresh_assets()
    matching_assets = [a for a in assets_cache if a["app"] == appname.lower()]
    if not matching_assets:
        await interaction.followup.send(f"❌ No files found for **{appname}**.")
        return

    # Buttons for each platform
    view = discord.ui.View()
    for asset in matching_assets:
        emoji = PLATFORM_EMOJIS.get(asset['platform_ext'], "")
        label = f"{emoji} {asset['platform_ext']} ({asset['version']})"
        view.add_item(discord.ui.Button(label=label, style=discord.ButtonStyle.link, url=asset["download_url"]))

    # Embed
    embed = discord.Embed(
        title=f"💾 Downloads for {appname.capitalize()}",
        description="Select your platform below to start the download:",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=get_app_thumbnail(appname))
    embed.set_footer(text="Direct downloads")
    builds_text = "\n".join(f"{a['version']} — {a['platform_ext']}" for a in matching_assets)
    embed.add_field(name="Available Builds", value=builds_text, inline=False)

    await interaction.followup.send(embed=embed, view=view)

# -------------------------
# Bot ready
# -------------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await refresh_assets()
    await bot.tree.sync()
    print("Bot is ready!")
    activity = discord.Activity(type=discord.ActivityType.playing, name="crack.exe")
    await bot.change_presence(activity=activity)

bot.run(TOKEN)
