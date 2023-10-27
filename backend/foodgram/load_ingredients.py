import psycopg2
import csv

conn = psycopg2.connect(
    #host="172.20.0.3",  # IP-адрес вашего контейнера PostgreSQL
    port=5432,
    database="foodgramlocal",
    user="postgres",
    password="19216812",
    options="-c search_path=public",
    client_encoding="UTF8"
)
cur = conn.cursor()
# ИМПОРТ ИНГРЕДИЕНТОВ
with open("C:/Dev/diplom/foodgram-project-react/backend/foodgram/ingredients.csv", "r", encoding="utf-8") as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    for row in csv_reader:
        name, measurement_unit = row
        cur.execute("INSERT INTO ingredients_ingredient (name, measurement_unit) VALUES (%s, %s)", (name, measurement_unit))
# ДЛЯ ИМПОРТА ТЕГОВ 
with open("C:/Dev/diplom/foodgram-project-react/backend/foodgram/tags.csv", "r", encoding="utf-8") as file:
    csv_reader = csv.reader(file)
    next(csv_reader)

    for row in csv_reader:
        name, color,slug = row
        cur.execute("INSERT INTO tags_tag (name, color,slug) VALUES (%s, %s,%s)", (name, color,slug))
conn.commit()
cur.close()
conn.close()