# DC-Torrent Bot

### Current Version
DC-Torrent V1.0.1

## Description

This is a Discord bot that integrates with qBittorrent to enable users to search for and download torrents directly from Discord using the YTS.mx API.

## Features

- Search for movies and download torrents using the YTS.mx API
- Remove, pause, and unpause torrents from qBittorrent directly in Discord
- Status rotator: Rotates through a list of statuses every 10 minutes

## Images
All Commands:

![image](https://github.com/Stijnxyz/dc-torrent/assets/84400230/ac2bfd91-d44b-4c07-96eb-d7a9c86d1295)




## Installation

### Youtube Tutorial:
[![Youtube](https://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg)](https://www.youtube.com/watch?v=YOUTUBE_VIDEO_ID_HERE)

### You need Python and qBittorrent already installed!

1. Download or clone this repository:
Download: Click on the green Code button > Download ZIP
Clone: git clone https://github.com/stijnxyz/dc-torrent.git

2. Install the required dependencies:
pip install -r requirements.txt

3. Configure the bot by editing the `config.json` file.

4. Run the bot:
python main.py

## Configuration

Edit the `config.json` file to configure the bot:

```json
{
"bot_token": "YOUR_BOT_TOKEN",
"qbittorrent_url": "http://YOUR_QBITTORRENT_IP:PORT/",
"qbittorrent_username": "YOUR_QBITTORRENT_USERNAME",
"qbittorrent_password": "YOUR_QBITTORRENT_PASSWORD",
"allowed_role_id": "ALLOWED_ROLE_ID",
"cmd_print": false,
"statuses": [
 "Status 1",
 "Status 2",
 "Status 3"
]
}

