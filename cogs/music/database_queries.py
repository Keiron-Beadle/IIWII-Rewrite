GET_USER_PLAYLISTS = "SELECT * FROM music_playlists WHERE id = %s"
INSERT_USER_PLAYLISTS = "INSERT INTO music_playlists VALUES(%s, %s)"
UPDATE_USER_PLAYLISTS = "UPDATE music_playlists SET playlists = %s WHERE id = %s"

GET_MUSIC_CHANNEL = "SELECT music_channel FROM guild_config WHERE id = %s"
UPDATE_MUSIC_CHANNEL = "UPDATE guild_config SET music_channel = %s WHERE id = %s"