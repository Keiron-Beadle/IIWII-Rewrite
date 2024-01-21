INSERT = "INSERT INTO economy VALUES (%s, %s, %s, %s)"
GET_ECONOMY = "SELECT * FROM economy WHERE id = %s AND guild_id = %s"
INC_BALANCE = "UPDATE economy SET copium = copium + %s WHERE id = %s AND guild_id = %s"
DEC_BALANCE = "UPDATE economy SET copium = copium - %s WHERE id = %s AND guild_id = %s"