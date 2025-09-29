import os
import requests
import discord
import threading
from discord import app_commands
from discord.ext import commands
from flask import Flask
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GITHUB_USER = "angel2rider"
GITHUB_REPO = "FETCHER"
RELEASE_TAG = "v1.0"

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
assets_cache = []
keep_alive_app = Flask("KeepAlive")
# Platform emojis for buttons
PLATFORM_EMOJIS = {
    "win": "🪟",
    "linux": "🐧",
    "mac": "🍎",
    "android": "🤖",
    "ios": "📱"
}

# Base URL for raw GitHub files (icons stored in repo root)
ICON_BASE_URL = "https://raw.githubusercontent.com/angel2rider/FETCHER/main/icons/"

# -------------------------
# GitHub release fetching
# -------------------------
def refresh_assets():
    global assets_cache
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/tags/{RELEASE_TAG}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        assets_cache = []
        for asset in data["assets"]:
            filename = asset["name"]  # e.g., "capcut-14.6.0-android.apk"
            name_part, ext = os.path.splitext(filename)
            first_dash = name_part.find("-")
            last_dash = name_part.rfind("-")

            if first_dash == -1 or last_dash == -1 or first_dash == last_dash:
                continue  # skip invalid files

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

@keep_alive_app.route("/")
def home():
    return "I am alive!", 200
def run_keep_alive():
    keep_alive_app.run(host="0.0.0.0", port=8000)
# -------------------------
# Autocomplete
# -------------------------
async def app_autocomplete(interaction: discord.Interaction, current: str):
    refresh_assets()
    apps = sorted({a["app"] for a in assets_cache if current.lower() in a["app"]})
    return [app_commands.Choice(name=a, value=a) for a in apps[:25]]

# -------------------------
# Helper for thumbnails
# -------------------------
def get_app_thumbnail(appname: str):
    # Construct GitHub raw URL for the icon
    return ICON_BASE_URL + f"{appname.lower()}.png"

# -------------------------
# /get command
# -------------------------
@bot.tree.command(name="get", description="Get a download link for an app")
@app_commands.describe(appname="Name of the app")
@app_commands.autocomplete(appname=app_autocomplete)
async def get(interaction: discord.Interaction, appname: str):
    
    user = interaction.user
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {user} typed: /get {appname}")
    
    await interaction.response.defer(ephemeral=True)
    refresh_assets()
    matching_assets = [a for a in assets_cache if a["app"] == appname.lower()]
    if not matching_assets:
        await interaction.followup.send(f"❌ No files found for **{appname}**.")
        return

    # Create buttons
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
    refresh_assets()
    await bot.tree.sync()
    print("Bot is ready!")
    activity = discord.Activity(
    type=discord.ActivityType.playing,
    name="crack.exe"
    )
    await bot.change_presence(activity=activity)
threading.Thread(target=run_keep_alive, daemon=True).start()
bot.run(TOKEN)
