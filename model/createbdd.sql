CREATE TABLE Song(  
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    title TEXT
);

CREATE Table DiscordUser(
    id TEXT NOT NULL PRIMARY KEY,
    username TEXT NOT NULL,
    guild_id TEXT NOT NULL
)

CREATE Table Request(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    song_id INTEGER,
    discord_user_id TEXT,
    request_date DATE NOT NULL,
    Foreign Key (song_id) REFERENCES Song(id),
    Foreign Key (discord_user_id) REFERENCES DiscordUser(id)
)