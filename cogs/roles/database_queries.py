GET_GUILD_ROLES = "SELECT * FROM roles WHERE guild_id = %s and `group` = %s"
ADD_GUILD_ROLE = "INSERT INTO roles VALUES (%s, %s, %s, %s, %s)"
DELETE_GUILD_ROLE = "DELETE FROM roles WHERE guild_id = %s AND name = %s"