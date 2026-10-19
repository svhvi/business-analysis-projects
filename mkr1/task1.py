import json
import requests
from bs4 import BeautifulSoup

# Повний набір заголовків справжнього браузера (щоб сайт не давав помилку 403)
headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
        ' like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ),
    'Accept': (
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
    ),
    'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://ek.ua/',
    'Connection': 'keep-alive',
}

all_data = []

print('Починаємо збір даних про мікрохвильові печі...')

# Збираємо з перших 5 сторінок (сторінки на EK.ua для цього розділу)
for page in range(1, 6):
  # Якщо перша сторінка, то без параметра page, для наступних додаємо &p=
  url = (
      'https://ek.ua/ua/list/86/'
      if page == 1
      else f'https://ek.ua/ua/list/86/?p={page}'
  )
  print(f'Збираємо сторінку {page}: {url}')

  response = requests.get(url, headers=headers)
  if response.status_code != 200:
    print(
        f'Помилка доступу на сторінці {page}, код статусу: {response.status_code}'
    )
    continue

  soup = BeautifulSoup(response.text, 'html.parser')

  # На EK.ua товари в списках знаходяться в блоках з певними класами
  items = soup.find_all('div', class_='model-short-block')
  if not items:
    # Шукаємо альтернативний клас, якщо структура відрізняється
    items = soup.find_all('table', class_='model-cheapest')

  print(f'Знайдено товарів на сторінці {page}: {len(items)}')

  for item in items:
    try:
      # 1. Назва моделі
      title_tag = item.find('a', class_='m-ed-l') or item.find('span', class_='u-l1')
      model = title_tag.get_text(strip=True) if title_tag else 'Мікрохвильова піч'

      # 2. Опис / характеристики
      desc_tag = item.find('div', class_='m-desc')
      params = desc_tag.get_text(strip=True) if desc_tag else 'Характеристики відсутні'

      # 3. Магазин
      shop_tag = item.find('span', class_='shop-card-name') or item.find('a', class_='ib-m')
      shop = shop_tag.get_text(strip=True) if shop_tag else 'Інтернет-магазин'

      # 4. Місто
      city_tag = item.find('span', class_='shop-city')
      city = city_tag.get_text(strip=True) if city_tag else 'Ужгород'

      # 5. Ціна (переводимо у числовий формат без зайвих символів)
      price_tag = item.find('span', class_='price-val') or item.find('div', class_='u-price')
      if price_tag:
        raw_price = price_tag.get_text(strip=True)
        digits = ''.join(c for c in raw_price if c.isdigit() or c == '.')
        price = float(digits) if digits else 0.0
      else:
        price = 0.0

      all_data.append({
          'model': model,
          'params': params,
          'city': city,
          'shop': shop,
          'price': price,  # Числовий формат для Excel
      })
    except Exception as e:
      continue

# Зберігаємо у JSON-файл
with open('microwaves.json', 'w', encoding='utf-8') as f:
  json.dump(all_data, f, ensure_ascii=False, indent=4)

print(
    f'Готово! Успішно зібрано та збережено {len(all_data)} записів у файл'
    ' microwaves.json'
)