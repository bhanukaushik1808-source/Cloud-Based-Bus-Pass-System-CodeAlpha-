from db_config import get_db_connection

try:
    connection = get_db_connection()
    print("SUCCESS: MySQL connection ho gaya!")
    
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]
    
    print(f"MySQL mein total applications: {total}")
    
    cursor.close()
    connection.close()

except Exception as error:
    print("Connection failed:", error)