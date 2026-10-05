import json
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

urls = [
    "https://kme.org.ua/uk/strukturni-pidrozdily/kafedri/kafedra-obliku-i-audytu/",
    "https://kme.org.ua/uk/strukturni-pidrozdily/kafedri/kafedra-matematiki-ta-informatiki/"
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
all_staff = {}

f_txt = open("staff.txt", "w", encoding="utf-8")

# Посади та системні слова, які треба ігнорувати
stop_words = [
    "завідувач", "доцент", "професор", "лаборант", "асистент", "викладач",
    "кафедра", "університет", "факультет", "наук", "репозитарій", "бібліотек",
    "вступ", "зсу", "структурні", "керівництво", "склад", "програм", "період",
    "роботи", "міжнародн", "інформац", "адреса", "телефон", "пошта"
]

for url in urls:
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    
    # 1. Назва кафедри
    header_tag = soup.find(["h1", "h2", "title"])
    dept_name = header_tag.get_text(strip=True) if header_tag else url
    f_txt.write(dept_name + ":\n")
    
    teachers = []
    
    # 2. Шукаємо елементи тексту по сторінці
    for tag in soup.find_all(["b", "strong", "h3", "h4", "h5", "p", "div"]):
        # Пропускаємо елементи в навігації або підвалі сайту
        if tag.find_parent(["nav", "header", "footer"]):
            continue
            
        text = tag.get_text(strip=True)
        words = text.split()
        
        # Перевірки на справжнє ПІБ:
        # 1. Складається з 2 або 3 слів (Бачо Роберт Йосипович)
        # 2. Адекватна довжина
        # 3. Не містить двокрапки ':' (щоб не брати 'Адреса для листування:', 'Номер телефону:')
        # 4. Не містить цифр
        if 2 <= len(words) <= 3 and 10 < len(text) < 40:
            if ":" not in text and not any(ch.isdigit() for ch in text):
                lower_text = text.lower()
                # Перевірка на відсутність службових та посадових слів
                if not any(sw in lower_text for sw in stop_words):
                    if text not in teachers:
                        teachers.append(text)
                        f_txt.write("  - " + text + "\n")
                        
    all_staff[dept_name] = teachers
    f_txt.write("\n")

f_txt.close()

# 3. Збереження у JSON
with open("staff.json", "w", encoding="utf-8") as f_json:
    json.dump(all_staff, f_json, ensure_ascii=False, indent=2)

# 4. Збереження у XML з маніфестом
root = ET.Element("staff")
for dept_name, teachers in all_staff.items():
    dept_tag = ET.SubElement(root, "department")
    ET.SubElement(dept_tag, "name").text = dept_name
    
    teachers_tag = ET.SubElement(dept_tag, "teachers")
    for teacher in teachers:
        ET.SubElement(teachers_tag, "teacher").text = teacher

tree = ET.ElementTree(root)
ET.indent(tree, space="  ")
tree.write("staff.xml", encoding="utf-8", xml_declaration=True)

print("Успішно! Зібрано викладачів у staff.txt, staff.json та staff.xml без помилок.")