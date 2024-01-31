GET_USER_PLAYLISTS = "SELECT * FROM music_playlists WHERE id = %s"
INSERT_USER_PLAYLISTS = "INSERT INTO music_playlists VALUES(%s, %s)"
UPDATE_USER_PLAYLISTS = "UPDATE music_playlists SET playlists = %s WHERE id = %s"