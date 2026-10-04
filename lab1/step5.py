import csv
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

# cторінки кафедр, з яких завантажуємо фото
urls = [
    "https://kme.org.ua/uk/strukturni-pidrozdily/kafedri/kafedra-obliku-i-audytu/",
    "https://kme.org.ua/uk/strukturni-pidrozdily/kafedri/kafedra-matematiki-ta-informatiki/"
]

headers = {"User-Agent": "Mozilla/5.0"}

# cтворюємо окрему папку для картинок
os.makedirs("images", exist_ok=True)

# відкриваємо текстовий файл і CSV-файл для списку адрес
f_txt = open("images.txt", "w", encoding="utf-8")
f_csv = open("images.csv", "w", newline="", encoding="utf-8")
csv_writer = csv.writer(f_csv)
csv_writer.writerow(["Filename", "URL"])  # заголовки стовпчиків у таблиці

count = 0

for page_url in urls:
  res = requests.get(page_url, headers=headers)
  soup = BeautifulSoup(res.text, "html.parser")

  for img in soup.find_all("img"):
    src = img.get("src")
    if not src:
      continue

    # робимо повне посилання на картинку
    img_url = urljoin(page_url, src)

    # отримуємо назву файлу (наприклад, photo.jpg)
    img_name = img_url.split("/")[-1].split("?")[0]

    # беремо лише справжні файли зображень (пропускаємо зайві системні іконки)
    if img_name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
      local_path = os.path.join("images", img_name)

      # завантажуємо сам файл картинки в папку
      if not os.path.exists(local_path):
        try:
          data = requests.get(img_url, headers=headers, timeout=5).content
          with open(local_path, "wb") as f_img:
            f_img.write(data)
        except Exception:
          continue

      # записуємо в images.txt
      f_txt.write(f"{img_name} - {img_url}\n")

      # записуємо в images.csv
      csv_writer.writerow([img_name, img_url])
      count += 1

f_txt.close()
f_csv.close()

print(f"Готово. Завантажено зображень: {count}")
print("Файли images.txt, images.csv та папка images/ створені.")