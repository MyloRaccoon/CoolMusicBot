from model.cursor import cur

class DiscordUser:

    def __init__(self, id, username, guild_id):
        self.id = id
        self.username = username
        self.guild_id = guild_id

    def __str__(self) -> str:
        return f"user {self.username} from guild {self.guild_id}"

def user_exists(user: DiscordUser) -> bool | None:
    try:
        cur.execute('SELECT id FROM DiscordUser')
        res = False
        users = cur.fetchall()
        i = 0
        while (not res) and i != len(users):
            user_id = users[i][0]
            guild_id = users[i][2]
            if user_id == user.id and guild_id == user.guild_id:
                res = True
            i += 1
        return res
    except Exception as e:
        print('Error while selecting users: ', e)
        return None

def insert_user(user: DiscordUser) -> bool:
    try:
        exists = user_exists(user)
        if exists or exists is None: return False
        cur.execute('INSERT INTO DiscordUser VALUES(?, ?)', (user.username, user.guild_id))
        cur.commit()
        return True
    except Exception as e:
        print('Error while inserting discord user: ', e)
        return False