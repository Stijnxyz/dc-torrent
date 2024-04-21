# DC-Torrent Bot

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

### Current Version
DC-Torrent V1.0.1

## Description

This is a Discord bot that integrates with qBittorrent to enable users to search for and download torrents directly from Discord using the YTS.mx API.

## Features

- Search for movies and download torrents using the YTS.mx API
- Remove, pause, and unpause torrents from qBittorrent directly in Discord
- Status rotator: Rotates through a list of statuses every 10 minutes

## Installation

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

