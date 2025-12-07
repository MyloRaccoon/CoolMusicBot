import yt_dlp
import asyncio

YDL_OPTIONS = {
    "format": "bestaudio[abr<=96]/bestaudio",
    "noplaylist": True,
    "youtube_include_dash_manifest": False,
    "youtube_include_hls_manifest": False,
}

class Song:

    def __init__(self, title: str, url: str):
        self.title: str = title
        self.url: str = url
        self.requester: str = None

    def __str__(self):
        return f"**{self.title}** requested by *{self.requester}*"

async def search_song(query: str) -> Song:
    query = "ytsearch1: " + query
    return await search_ytdlp_async(query)


async def search_ytdlp_async(query):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, lambda: _extract(query, YDL_OPTIONS))
    tracks = result.get("entries", [])
    if tracks is None: return None
    else:
        song_data = tracks[0]
        return Song(song_data.get("title", "Untitled"), song_data['url'])

def _extract(query, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(query, download=False)

class SongQueue:

    def __init__(self):
        self.songs: dict[list[Song]] = {}
        self.playing: dict[Song] = {}
    
    def add_to_queue(self, guild_id: str, song: Song):
        if not guild_id in self.songs:
            self.songs[guild_id] = []
        self.songs[guild_id].append(song)
    
    def pop(self, guild_id: str) -> Song:
        if not guild_id in self.songs: return None
        if not self.songs[guild_id]: return None
        song = self.songs[guild_id].pop(0)
        self.playing[guild_id] = song
        return song
    
    def del_guild_queue(self, guild_id: str):
        if not guild_id in self.songs: return
        del self.songs[guild_id]
        if not guild_id in self.playing: return
        del self.playing[guild_id]
    
    def get_guild_queue(self, guild_id: str) -> list[Song]:
        return self.songs.get(guild_id)
    
    def get_guild_playing(self, guild_id: str) -> Song:
        return self.playing.get(guild_id)
