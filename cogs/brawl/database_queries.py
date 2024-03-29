GET_USER_ACTIVE_BRAWL = f'''SELECT * FROM brawls WHERE (host_id = %s OR opponent_id = %s) AND status != "inactive" AND guild_id = %s'''
ADD_BRAWL = f'''INSERT INTO brawls VALUES (%s, %s, 0, %s, %s,0, 0, "open", %s, "{{}}", 0, %s)'''
#               guild_id, host, opp, title, terms, start, length, status, brawl_pot, voters, winner, image
GET_USER_BRAWLS = f'''SELECT * FROM brawls WHERE (host_id = %s OR opponent_id = %s) AND guild_id = %s'''
GET_USER_BRAWLS_HOST = f'''SELECT * FROM brawls WHERE host_id = %s AND guild_id = %s'''
GET_USER_BRAWLS_OPPONENT = f'''SELECT * FROM brawls WHERE opponent_id = %s AND guild_id = %s'''

SET_BRAWL_STATUS = f'''UPDATE brawls SET status = %s WHERE host_id = %s AND status = %s'''
SET_BRAWL_OPPONENT = f'''UPDATE brawls SET opponent_id = %s WHERE host_id = %s AND status != "inactive" AND guild_id = %s'''
SET_BRAWL_POT = f'''UPDATE brawls SET brawl_pot = %s WHERE host_id = %s AND status != "inactive"'''
SET_BRAWL_VOTERS = f'''UPDATE brawls SET voters = %s WHERE host_id = %s AND status != "inactive"'''
SET_BRAWL_WINNER = f'''UPDATE brawls SET winner = %s WHERE host_id = %s AND status != "inactive"'''
SET_BRAWL_LENGTH = f'''UPDATE brawls SET length = %s WHERE host_id = %s AND status != "inactive"'''
SET_BRAWL_TERMS = f'''UPDATE brawls SET terms = %s WHERE host_id = %s AND status != "inactive"'''
UPDATE_BRAWL_FOR_START = f'''UPDATE brawls SET brawl_pot = %s, voters = %s, start_time = %s WHERE host_id = %s AND status != "inactive" AND guild_id = %s'''
UPDATE_BRAWL_FOR_END = f'''UPDATE brawls SET winner = %s, length = %s, status = "inactive" WHERE host_id = %s AND status != "inactive" AND guild_id = %s'''
DELETE_BRAWL = f'''DELETE FROM brawls WHERE host_id = %s AND status != "inactive" AND guild_id = %s'''
SET_BRAWL_CHANNEL = f'''UPDATE guild_config SET brawl_channel = %s WHERE id = %s'''
GET_BRAWL_CHANNEL = f'''SELECT brawl_channel FROM guild_config WHERE id = %s'''