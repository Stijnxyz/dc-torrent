import discord
from discord.ext import commands, tasks
import requests
from qbittorrent import Client
import json
import asyncio
import os

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

statuses = config.get('statuses', [])
status_index = 0

bot = commands.Bot(command_prefix='-', intents=discord.Intents.all())

# Connect to qBittorrent Web UI
qbittorrent = Client(config['qbittorrent_url'])
qbittorrent.login(config['qbittorrent_username'], config['qbittorrent_password'])

@tasks.loop(minutes=5)
async def rotate_status():
    global status_index
    status = statuses[status_index % len(statuses)]
    await bot.change_presence(activity=discord.Game(name=status))
    status_index += 1

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear console
    print("\033[34m")  # Blue color
    print(r"""
  _____   _____   _______                        _   
 |  __ \ / ____| |__   __|                      | |  
 | |  | | |   ______| | ___  _ __ _ __ ___ _ __ | |_ 
 | |  | | |  |______| |/ _ \| '__| '__/ _ \ '_ \| __|
 | |__| | |____     | | (_) | |  | | |  __/ | | | |_ 
 |_____/ \_____|    |_|\___/|_|  |_|  \___|_| |_|\__|
                                                     
                                                     
    """)
    print(f'{bot.user} has connected to Discord! And client connected to QBitTorrent Web.')
    await bot.tree.sync()
    rotate_status.start()

@bot.hybrid_command(name="pause", description="Pause a torrent by name or index")
async def pause(ctx, *, torrent_info):
    if config.get('cmd_print', True):
        print("Pausing torrent...")

    try:
        torrents = qbittorrent.torrents()
        matching_torrents = [torrent for torrent in torrents if torrent_info.lower() in torrent['name'].lower()]
        if not matching_torrents:
            await ctx.send("No matching torrents found.")
            return
        for torrent in matching_torrents:
            qbittorrent.pause(torrent['hash'])
        await ctx.send("Torrents paused successfully.")
    except Exception as e:
        if config.get('cmd_print', True):
            print(f"Error occurred while pausing torrent: {e}")
        await ctx.send("An error occurred while pausing the torrent. Please try again later.")

@bot.hybrid_command(name="unpause", description="Unpause a torrent by name or index")
async def unpause(ctx, *, torrent_info):
    if config.get('cmd_print', True):
        print("Unpausing torrent...")

    try:
        torrents = qbittorrent.torrents()
        matching_torrents = [torrent for torrent in torrents if torrent_info.lower() in torrent['name'].lower()]
        if not matching_torrents:
            await ctx.send("No matching torrents found.")
            return
        for torrent in matching_torrents:
            qbittorrent.resume(torrent['hash'])
        await ctx.send("Torrents unpaused successfully.")
    except Exception as e:
        if config.get('cmd_print', True):
            print(f"Error occurred while unpausing torrent: {e}")
        await ctx.send("An error occurred while unpausing the torrent. Please try again later.")

@bot.hybrid_command(name="remove", description="Remove a torrent by name or index")
async def remove(ctx, *, torrent_info):
    if config.get('cmd_print', True):
        print("Removing torrent...")

    try:
        torrents = qbittorrent.torrents()
        matching_torrents = [torrent for torrent in torrents if torrent_info.lower() in torrent['name'].lower()]
        if not matching_torrents:
            await ctx.send("No matching torrents found.")
            return
        
        confirmation_message = await ctx.send("Are you sure you want to remove the following torrents?\n\n" + "\n".join([torrent['name'] for torrent in matching_torrents]) + "\n\nReact with ✅ to confirm or ❌ to cancel.")

        await confirmation_message.add_reaction("✅")  # Confirm
        await confirmation_message.add_reaction("❌")  # Cancel

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == confirmation_message.id and str(reaction.emoji) in ["✅", "❌"]

        reaction, _ = await bot.wait_for("reaction_add", timeout=60, check=check)
        if str(reaction.emoji) == "❌":
            await ctx.send("Operation cancelled.")
            return

        for torrent in matching_torrents:
            qbittorrent.delete(torrent['hash'])
        await ctx.send("Torrents removed successfully.")
    except Exception as e:
        if config.get('cmd_print', True):
            print(f"Error occurred while removing torrent: {e}")
        await ctx.send("An error occurred while removing the torrent. Please try again later.")




@bot.hybrid_command(name = "movie", description = "Download a movie using QBitTorrent and YTS.mx API")
async def movie(ctx, *, movie_name):
    if config.get('cmd_print', True):
        print(f"Received movie command with movie name: {movie_name}")
    
        # Check if the user has the allowed role
    allowed_role_id = int(config.get('allowed_role_id', 0))  # Convert to integer
    if allowed_role_id:
        allowed_role = ctx.guild.get_role(allowed_role_id)
        if allowed_role and allowed_role not in ctx.author.roles:
            await ctx.send("You don't have permission to use this command.")
            return
    
    movie_name = movie_name.replace(' ', '-')
    if config.get('cmd_print', True):
        print(f"Formatted movie name: {movie_name}")
    
    search_url = f"https://yts.mx/api/v2/list_movies.json?query_term={movie_name}"
    if config.get('cmd_print', True):
        print(f"Sending request to: {search_url}")

    try:
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        if config.get('cmd_print', True):
            print(f"Error occurred while fetching data: {e}")
        await ctx.send("An error occurred while searching for the movie. Please try again later.")
        return

    if data.get('status') == 'ok' and data.get('data', {}).get('movie_count', 0) > 0:
        if config.get('cmd_print', True):
            print("Movie found!")
        movie_data = data['data']['movies'][0]
        title = movie_data['title']
        year = movie_data['year']
        imdb_url = movie_data['url']
        torrents = movie_data['torrents']

        embed = discord.Embed(
            title=f"Search results for '{movie_name.replace('-', ' ')}':",
            description=f"**Title:** {title}\n**Year:** {year}\n[IMDb]({imdb_url})",
            color=0x00ff00
        )

        reactions = {}
        for i, torrent in enumerate(torrents, start=1):
            quality = torrent['quality']
            magnet_link = torrent['url']
            try:
                embed.add_field(name=f"{i}. Resolution: {quality}", value=f"Magnet: [link]({magnet_link})", inline=False)
                reaction = f"{i}\u20E3"
                reactions[reaction] = torrent
            except Exception as e:
                if config.get('cmd_print', True):
                    print(f"Error occurred while adding field to embed: {e}")
        
        if config.get('cmd_print', True):
            print("Sending embed to Discord...")
        try:
            message = await ctx.send(embed=embed)
        except discord.HTTPException as e:
            if config.get('cmd_print', True):
                print(f"Error occurred while sending embed: {e}")
            await ctx.send("An error occurred while sending the embed. Please try again later.")
            return

        for reaction in reactions:
            await message.add_reaction(reaction)

        if config.get('cmd_print', True):
            print("Waiting for user reaction...")
        def check(reaction, user):
            return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in reactions

        try:
            reaction, _ = await bot.wait_for('reaction_add', timeout=60, check=check)  # Timeout after 60 seconds
        except asyncio.TimeoutError:
            await ctx.send("You took too long to react. Please try again.")
            return

        selected_torrent = reactions.get(str(reaction.emoji))
        
        if selected_torrent:
            if config.get('cmd_print', True):
                print("Downloading torrent...")
            try:
                qbittorrent.download_from_link(selected_torrent['url'])
                await ctx.send(f"Downloading '{title}' in {selected_torrent['quality']} resolution. Please wait until the download is complete.")
            except Exception as e:
                if config.get('cmd_print', True):
                    print(f"Error occurred while downloading torrent: {e}")
                await ctx.send("An error occurred while downloading the torrent. Please try again later.")
        else:
            await ctx.send("Invalid reaction. Please try again.")
    else:
        if config.get('cmd_print', True):
            print("Movie not found.")
        await ctx.send(f"No movie found for '{movie_name.replace('-', ' ')}'.")

@bot.hybrid_command(name = "progress", description = "View the progress of active torrents using QBitTorrent")
async def progress(ctx):
    if config.get('cmd_print', True):
        print("Checking download progress...")

    try:
        torrents = qbittorrent.torrents()
    except Exception as e:
        if config.get('cmd_print', True):
            print(f"Error occurred while fetching torrent list: {e}")
        await ctx.send("An error occurred while fetching the list of torrents.")
        return

    if not torrents:
        await ctx.send("No torrents are currently being downloaded.")
        return

    embed = discord.Embed(
        title="Download Progress",
        color=0x00ff00
    )

    for torrent in torrents:
        name = torrent['name']
        progress = int(torrent['progress'] * 100)  # Convert progress to percentage
        download_speed = torrent['dlspeed'] / 1024  # Convert bytes/s to KB/s
        upload_speed = torrent['upspeed'] / 1024  # Convert bytes/s to KB/s
        download_speed_mb = download_speed / 1024  # Convert KB/s to MB/s
        upload_speed_mb = upload_speed / 1024  # Convert KB/s to MB/s
        status = torrent['state']

        embed.add_field(
            name=name,
            value=f"Progress: {progress}%\nDownload Speed: {download_speed:.2f} KB/s ({download_speed_mb:.2f} MB/s)\nUpload Speed: {upload_speed:.2f} KB/s ({upload_speed_mb:.2f} MB/s)\nStatus: {status}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide the movie name.")
    else:
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred while processing the command: {error}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

bot.run(config['bot_token'])