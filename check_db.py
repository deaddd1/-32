import sqlite3

conn = sqlite3.connect("shop.dСb")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Таблиці в базі даних:")
print(cursor.fetchall())

conn.close()
