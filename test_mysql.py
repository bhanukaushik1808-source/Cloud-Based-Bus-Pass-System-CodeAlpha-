import getpass
import mysql.connector

password = getpass.getpass("MySQL root password enter karo: ")

try:
    connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password=password,
        database="buspass_db"
    )

    print("SUCCESS: Python se MySQL connection ho gaya!")
    connection.close()

except mysql.connector.Error as error:
    print("Connection failed:", error)