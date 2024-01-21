INSERT = "INSERT INTO economy VALUES (%s, %s, %s, %s)"
GET_ECONOMY = "SELECT * FROM economy WHERE id = %s AND guild_id = %s"
UPDATE_ECONOMY = "UPDATE economy SET copium = %s, transactions = %s WHERE id = %s AND guild_id = %s"