#Will try to connect the database here. and send the connection instance.
import MySQLdb
from utils.config import Settings

settings = Settings()

def connection():
    db_config = {
        'host': settings.database_host,
        'user': settings.database_user,
        'passwd': settings.database_pass,
        'db': settings.database_name,
    }

    try:
        conn = MySQLdb.connect(**db_config)
        return conn
    except Exception as e:
        return e
