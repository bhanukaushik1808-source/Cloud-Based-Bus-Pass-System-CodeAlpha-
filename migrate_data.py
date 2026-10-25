import sqlite3
import mysql.connector
from datetime import date, datetime

SQLITE_DB = "buspass.db"


def main():
    password = input("MySQL root password enter karo: ")

    # Original SQLite database se records read karo
    with sqlite3.connect(SQLITE_DB) as sqlite_conn:
        sqlite_conn.row_factory = sqlite3.Row
        records = sqlite_conn.execute(
            "SELECT * FROM applications ORDER BY id"
        ).fetchall()

    print(f"SQLite mein {len(records)} applications mili.")

    if not records:
        print("Transfer karne ke liye koi records nahi hain.")
        return

    mysql_conn = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password=password,
        database="buspass_db"
    )

    try:
        cursor = mysql_conn.cursor()

        # Existing MySQL records ko overwrite nahi karna.
        # Sirf missing application IDs insert honge.
        insert_sql = """
            INSERT INTO applications (
                id, full_name, phone, email, category, address,
                route, pass_type, start_date, status, created_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
        """

        inserted = 0
        skipped = 0

        for row in records:
            data = dict(row)

            cursor.execute(
                "SELECT id FROM applications WHERE id = %s",
                (data["id"],)
            )

            if cursor.fetchone():
                skipped += 1
                continue

            start_date = data["start_date"]
            if isinstance(start_date, str) and start_date.strip():
                try:
                    start_date = date.fromisoformat(start_date.strip())
                except ValueError:
                    # Invalid/unexpected date ko NULL rakho.
                    start_date = None

            created_at = data["created_at"]
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    created_at = None

            values = (
                data["id"],
                data["full_name"],
                data["phone"],
                data["email"],
                data["category"],
                data["address"],
                data["route"],
                data["pass_type"],
                start_date,
                data["status"],
                created_at
            )

            cursor.execute(insert_sql, values)
            inserted += 1

        mysql_conn.commit()

        print(f"Transfer complete! {inserted} applications insert hui.")
        print(f"{skipped} applications pehle se maujood thi, skip hui.")

        cursor.execute("SELECT COUNT(*) FROM applications")
        print("MySQL mein total applications:", cursor.fetchone()[0])

    except Exception:
        mysql_conn.rollback()
        raise
    finally:
        cursor.close()
        mysql_conn.close()


if __name__ == "__main__":
    main()