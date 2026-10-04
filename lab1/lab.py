# Завдання 1
# Обраний заклад: Закарпатський угорський інститут імені Ференца Ракоці II
# Головний сайт: https://kme.org.ua/uk/
# =====================================================================
# Завдання 2
import requests
url = "https://kme.org.ua/uk/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
# завантажуємо сторінку
response = requests.get(url, headers=headers)
response.encoding = "utf-8"
# виводимо HTML у консоль 
print(response.text)