import pymysql
from utils.secrets_util import DB_PASSWORD

# Database configuration
db_config = {
    "host": "kokomo-yacht-club.cr2y46qk654i.ap-southeast-2.rds.amazonaws.com",
    "user": "admin",
    "password": DB_PASSWORD,
    "database": "kokomo-yacht-club",
    "port": 3306,
}

def get_db_connection():
    return pymysql.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        port=db_config["port"],
        cursorclass=pymysql.cursors.DictCursor,  # Use DictCursor for dictionary-like results
    )
