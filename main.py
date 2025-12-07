import os
import dotenv
import asyncio
import discord
from discord.ext import commands
from discord import app_commands, VoiceProtocol
from song import search_song, SongQueue


dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

FFMPEG_OPTIONS = {
	"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
	"options": "-vn -c:a libopus -b:a 96k",
}

song_queue = SongQueue()

intents = discord.Intents.default() 
intents.message_content = True

bot = commands.Bot(command_prefix="&", intents=intents)

@bot.event
async def on_ready():
	synced = await bot.tree.sync()
	print(f"synced {len(synced)} commands")
	print(f"{bot.user} is ready!")


@bot.tree.command(name="pause", description="Pause/resume the current playing song")
async def pause(interaction: discord.Interaction):
	voice_client = interaction.guild.voice_client

	if not voice_client:
		embed = discord.Embed(title="Nothing to pause right now...")
		return await interaction.response.send_message(embed=embed, ephemeral=True)
	
	if not voice_client.is_paused():
		voice_client.pause()
		embed = discord.Embed(title="Playback paused!")
	else:
		voice_client.resume()
		embed = discord.Embed(title="Playback resumed!")

	await interaction.response.send_message(embed=embed)


@bot.tree.command(name="skip", description="Skip to the next song in queue")
async def skip(interaction: discord.Interaction):

	if interaction.guild.voice_client and (interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused()):
		interaction.guild.voice_client.stop()
		embed = discord.Embed(title="Skipped.")
		ephemeral = False
	else:
		embed = discord.Embed(title="No song currently playing, nothing to skip.")
		ephemeral = True

	await interaction.response.send_message(embed=embed, ephemeral=ephemeral)


@bot.tree.command(name="queue", description="See the song queue")
async def queue(interaction: discord.Interaction):
	await interaction.response.defer()
	guild_id = str(interaction.guild_id)

	playing = song_queue.get_guild_playing(guild_id)
	if not playing:
		embed = discord.Embed(title="No song playing or in queue! Use the `play` command.")
		await interaction.followup.send(embed=embed, ephemeral=True)
		return

	queue = song_queue.get_guild_queue(guild_id)
	if not queue:
		embed = discord.Embed(title=f"Now playing", description=f"{playing}")
		await interaction.followup.send(embed=embed)
		return

	embed = discord.Embed()
	embed.title = f"Now playing"
	embed.description = f"{playing}"
	for song in queue:
		embed = embed.add_field(name=song.title, value=f"requested by *{song.requester}*", inline=False)
	
	await interaction.followup.send(embed=embed)
	

@bot.tree.command(name="play", description="Play a song from youtube")
@app_commands.describe(song_query="Search query")
async def play(interaction: discord.Interaction, song_query: str):
	await interaction.response.defer()

	voice_channel = interaction.user.voice.channel if not interaction.user.voice is None else None 

	if voice_channel is None:
		await interaction.followup.send(embed=discord.Embed(title="You must be in a voice channel."), ephemeral=True)
		return

	voice_client = interaction.guild.voice_client

	if voice_client is None:
		voice_client = await voice_channel.connect()
	elif voice_channel != voice_client.channel:
		await voice_channel.move_to(voice_channel)

	song = await search_song(song_query)
	if song is None:
		await interaction.followup.send(embed=discord.Embed(title=f"No result found D:"))
		return
	
	song.requester = interaction.user.display_name

	guild_id = str(interaction.guild_id)
	song_queue.add_to_queue(guild_id, song)

	await interaction.followup.send(embed=discord.Embed(title=f"Added to queue", description=f"{song.title}"))

	if not voice_client.is_playing() or voice_client.is_paused():
		channel = interaction.channel
		await play_next(voice_client, guild_id, channel)

async def play_next(voice_client: VoiceProtocol, guild_id: str, channel):
	song = song_queue.pop(guild_id)

	if not song:
		asyncio.create_task(channel.send("Queue empty, disconnecting."))
		await voice_client.disconnect()
		song_queue.del_guild_queue(guild_id)
		return

	source = discord.FFmpegOpusAudio(song.url, **FFMPEG_OPTIONS, executable="bin\\ffmpeg\\ffmpeg.exe")

	def after(error):
		if error:
			print(f"Error playing {song.title}: {error}")
		asyncio.run_coroutine_threadsafe(play_next(voice_client, guild_id, channel), bot.loop)

	voice_client.play(source, after=after)
	asyncio.create_task(channel.send(f"Now playing: {song}"))


bot.run(TOKEN)