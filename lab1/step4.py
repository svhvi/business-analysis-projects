import json
import requests
from bs4 import BeautifulSoup

# посилання на кафедри
urls = [
    "https://kme.org.ua/uk/strukturni-pidrozdily/kafedri/kafedra-obliku-i-audytu/",
    "https://kme.org.ua/uk/strukturni-pidrozdily/kafedri/kafedra-matematiki-ta-informatiki/"
]

headers = {"User-Agent": "Mozilla/5.0"}
all_staff = {}

f_txt = open("staff.txt", "w", encoding="utf-8")

for url in urls:
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    
    # безпечно беремо назву: якщо є h1 або h2, беремо його, якщо ні — заголовок сторінки title
    header_tag = soup.find(["h1", "h2", "title"])
    dept_name = header_tag.get_text(strip=True) if header_tag else url
    
    f_txt.write(dept_name + ":\n")
    
    # шукаємо викладачів у списках і параграфах
    teachers = []
    for item in soup.find_all(["li", "p"]):
        name = item.get_text(strip=True)
        # фільтр: довжина рядка схожа на ім'я людини (від 10 до 35 символів)
        if 10 < len(name) < 35 and "\n" not in name:
            if name not in teachers:
                teachers.append(name)
                f_txt.write("  - " + name + "\n")
                
    all_staff[dept_name] = teachers
    f_txt.write("\n")

f_txt.close()

# зберігаємо у JSON
with open("staff.json", "w", encoding="utf-8") as f_json:
    json.dump(all_staff, f_json, ensure_ascii=False, indent=2)

print("Успішно! Файли staff.txt та staff.json створено без помилок.")