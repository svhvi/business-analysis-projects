import csv
import json
import sqlite3

# підключаємося до бази даних (файл university.db)
conn = sqlite3.connect("university.db")
cursor = conn.cursor()

# створюємо таблиці
cursor.execute("""
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    url TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    url TEXT
)
""")

# переносимо дані кафедр з файлу departments.txt
with open("departments.txt", "r", encoding="utf-8") as f:
  for line in f:
    if " - " in line:
      parts = line.strip().split(" - ")
      cursor.execute(
          "INSERT INTO departments (name, url) VALUES (?, ?)",
          (parts[0], parts[1]),
      )

# переносимо дані викладачів з файлу staff.json
with open("staff.json", "r", encoding="utf-8") as f:
  staff_data = json.load(f)
  for dept_name, teachers in staff_data.items():
    for teacher in teachers:
      cursor.execute(
          "INSERT INTO staff (department_name, name) VALUES (?, ?)",
          (dept_name, teacher),
      )

# переносимо дані картинок з файлу images.csv
with open("images.csv", "r", encoding="utf-8") as f:
  reader = csv.reader(f)
  next(reader, None)  # пропускаємо заголовок (Filename, URL)
  for row in reader:
    if len(row) >= 2:
      cursor.execute(
          "INSERT INTO images (filename, url) VALUES (?, ?)", (row[0], row[1])
      )

conn.commit()
conn.close()

print(
    "Готово. Всі дані успішно перенесено в базу даних (файл university.db)."
)