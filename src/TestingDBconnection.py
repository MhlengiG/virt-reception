import mysql.connector

try:
    # Replace with your actual DB credentials
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Dortmund11!.",
        database="ukzn"
    )
    cursor = conn.cursor()

    # Basic SELECT to test connection
    cursor.execute("SELECT * FROM staff LIMIT 5;")
    rows = cursor.fetchall()

    print("✅ Connected to DB — sample output:")
    for row in rows:
        print(row)

    # Clean up
    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    print("❌ Failed to connect to MySQL:", err)
