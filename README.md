Fetcher – Your Discord Download Bot 🚀💾

Fetcher is a Discord bot that makes downloading apps and files from your GitHub releases a breeze. With dynamic buttons, auto-generated thumbnails, and autocomplete support, fetching the right version for the right platform has never been this easy.

Features ✨

Dynamic /get command – fetch any app stored in your GitHub release.

Autocomplete – type a few letters and the bot will suggest apps.

Platform buttons – download links for Windows, Mac, Linux, Android, iOS with clear emojis.

GitHub-hosted thumbnails – each app has its own clean icon in the embed.

Rich presence – bot displays a “Playing/Watching” status for a more alive experience.

Keep-alive server – minimal Flask server to ping for hosting uptime on Render or similar platforms.

No hardcoding required – just upload your files and icons to GitHub.

Setup 🛠️

Clone the repo

git clone https://github.com/angel2rider/<your-repo-name>.git
cd <your-repo-name>


Install dependencies

pip install -r requirements.txt


Make sure you have:

discord.py

requests

flask

Configure environment

Replace YOUR_TOKEN_HERE in bot.py with your Discord bot token.

Set GITHUB_USER, GITHUB_REPO, and RELEASE_TAG to match your GitHub releases.

Upload app icons

Store icons in your GitHub repo root as appname.png (lowercase).

The bot automatically picks the right thumbnail for each app.

Run the bot

python bot.py

Usage 💡

Fetch an app

/get <appname>


Autocomplete will suggest apps as you type.

The bot sends an embed with download buttons for all available platforms.

Enjoy dynamic thumbnails – each app has a custom icon fetched from GitHub.

Bot status updates – shows the last requested app in “Playing” or “Watching” mode.

File Naming Convention 📂

To ensure everything works perfectly:

appname-version-platform.ext


Example:

capcut-14.6.0-android.apk
crossover-25.1.1-mac.dmg


appname → matches your icon file appname.png

version → displayed in embed and buttons

platform → used for emoji-labeled download buttons

Contributing 🤝

Fork the repo.

Add new features, fixes, or apps.

Submit a pull request.

License 📝

MIT License – free to use and modify.
