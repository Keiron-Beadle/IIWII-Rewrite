import os
import mariadb
from typing import *
from dotenv import load_dotenv

load_dotenv()

connection_params ={
    "user" : os.getenv('DB_USER'),
    "password" : os.getenv('DB_PASSWORD'),
    "host" : os.getenv('DB_HOST'),
    "port" : int(os.getenv('DB_PORT')),
    "database" : os.getenv('DB_DATABASE')
}

pool = mariadb.ConnectionPool(pool_name="pool", pool_size=5, **connection_params)

def execute(operation, params=None) -> bool:
    conn : mariadb.Connection = pool.get_connection()
    cursor : mariadb.Cursor = conn.cursor(buffered=True)
    try:
        cursor.execute(statement=operation, data=params)
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        cursor.close()
        conn.close()

def select_one(operation, params=None) -> Optional[Tuple]:
    conn : mariadb.Connection = pool.get_connection()
    cursor : mariadb.Cursor = conn.cursor(buffered=True)
    try:
        cursor.execute(statement=operation, data=params)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        conn.close()

def select_many(operation, count=1, params=None) -> List[Tuple]:
    conn : mariadb.Connection = pool.get_connection()
    cursor : mariadb.Cursor = conn.cursor(buffered=True)
    try:
        cursor.execute(statement=operation, data=params)
        result = cursor.fetchmany(count)
        return result
    except Exception as e:
        print(e)
        return []
    finally:
        cursor.close()
        conn.close()

def select_all(operation, params=None) -> List[Tuple]:
    conn : mariadb.Connection = pool.get_connection()
    cursor : mariadb.Cursor = conn.cursor(buffered=True)
    try:
        cursor.execute(statement=operation, data=params)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(e)
        return []
    finally:
        cursor.close()
        conn.close()

