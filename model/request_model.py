from datetime import datetime
from cursor import cur
from song_model import insert_song
from discord_user_model import insert_user

def insert_request(user, song) -> bool:
    insert_song(song)
    insert_user(user)
    try:
        cur.execute('INSERT INTO Request VALUES(?, ?, ?)', (song.id, user.id, datetime.now()))
        cur.commit()
        return True
    except Exception as e:
        print('Error while inserting request: ', e)
        return False