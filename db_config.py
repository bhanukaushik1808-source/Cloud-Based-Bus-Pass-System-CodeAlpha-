import os
import mysql.connector


def get_db_connection():
    password = os.environ.get("MYSQL_PASSWORD")

    if not password:
        raise RuntimeError(
            "MYSQL_PASSWORD environment variable set nahi hai."
        )

    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password=password,
        database="buspass_db"
    )