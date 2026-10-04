import requests
from bs4 import BeautifulSoup

# завантажуємо сторінку
url = "https://kme.org.ua/uk/kafedry/"
page = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(page.text, "html.parser")

# відкриваємо 2 файли для запису
f_txt = open("departments.txt", "w", encoding="utf-8")
f_xml = open("departments.xml", "w", encoding="utf-8")

# початок XML файлу
f_xml.write("<departments>\n")

# знаходимо всі кафедри і записуємо в обидва файли
for a in soup.find_all("a", href=True):
  if "kafedry/" in a["href"] and len(a.text.strip()) > 5:
    name = a.text.strip()
    link = a["href"]

    # запис у TXT
    f_txt.write(name + " - " + link + "\n")

    # запис у XML
    f_xml.write(
        f"  <department>\n    <name>{name}</name>\n    <url>{link}</url>\n "
        " </department>\n"
    )

# закриваємо тег XML та зберігаємо файли
f_xml.write("</departments>")
f_txt.close()
f_xml.close()

print("Готово! Файли departments.txt та departments.xml створені.")