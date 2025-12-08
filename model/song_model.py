from model.cursor import cur

class Song:

    def __init__(self, title: str, url: str):
        self.title: str = title
        self.url: str = url
        self.requester: str = None

    def __str__(self) -> str:
        return f"**{self.title}** requested by *{self.requester}*"

def song_exists(song: Song) -> bool | None:
    try:
        cur.execute('SELECT title FROM Song')
        res = False
        titles = cur.fetchall()
        i = 0
        while (not res) and i != len(titles):
            title = titles[i][0]
            if title == song.title:
                res = True
            i += 1
        return res
    except Exception as e:
        print('Error while selecting songs: ', e)
        return None

def insert_song(song: Song) -> bool:
    try:
        exists = song_exists(song)
        if exists or exists is None : return False
        cur.execute('INSERT INTO Song VALUES(?)', (song.title))
        cur.commit()
        return True
    except Exception as e:
        print('Error while inserting song: ', e)
        return False