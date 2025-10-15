import sqlite3

# --------------------------------------
# 1. Show all tables in the database
# --------------------------------------
conn = sqlite3.connect('databasewithcustomer.db')  # Replace with your DB path
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("📄 Tables in the database:")
for table in tables:
    print(" -", table[0])

conn.close()


# --------------------------------------
# 2. View contents of the 'users' table
# --------------------------------------
conn = sqlite3.connect('databasewithcustomer.db')
cursor = conn.cursor()

table_name = 'users'  # Replace if needed
cursor.execute(f"SELECT * FROM {table_name}")
rows = cursor.fetchall()
column_names = [description[0] for description in cursor.description]

print("\n📋 Table Contents:")
print(" | ".join(column_names))
print("-" * 50)
for row in rows:
    print(" | ".join(str(item) for item in row))


# --------------------------------------
# 3. Delete a specific row (by email)
# --------------------------------------
# Uncomment this block if you want to delete a single user
# cursor.execute("DELETE FROM users WHERE email = 'shanjay1.ssj@gmail.com'")
# conn.commit()
# print("\n✅ Deleted user with email 'shanjay1.ssj@gmail.com'")


# --------------------------------------
# 4. Delete all rows from the table
# --------------------------------------
# Uncomment this block to remove all data (keep table structure)
# cursor.execute("DELETE FROM users")
# conn.commit()
# print("\n✅ All records deleted from 'users' table.")


# # --------------------------------------
# # 5. Reset auto-increment ID to 1
# # --------------------------------------
# # Use only after deleting all rows from the table
# cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
# conn.commit()
# print("✅ Auto-increment ID reset to 1.")


# --------------------------------------
# 6. Drop the entire 'users' table
# --------------------------------------
# Uncomment to delete table entirely (structure + data)
# cursor.execute("DROP TABLE IF EXISTS users")
# conn.commit()
# print("\n⚠️ 'users' table dropped from the database.")

conn.close()
