import csv
import re
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def clean_price(price_str):
  if not price_str:
    return None
  match = re.search(r'(\d[\d\s]*\d|\d+)', price_str)
  if match:
    cleaned = re.sub(r'\s+', '', match.group(1))
    return int(cleaned)
  return None


def parse_ek_powerbanks():
  offers_data = []
  user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'

  with sync_playwright() as p:
    try:
      browser = p.chromium.launch(
          headless=False,
          channel='chrome',
          args=['--disable-blink-features=AutomationControlled'],
      )
    except Exception:
      browser = p.chromium.launch(
          headless=False,
          channel='msedge',
          args=['--disable-blink-features=AutomationControlled'],
      )

    context = browser.new_context(
        user_agent=user_agent,
        viewport={'width': 1366, 'height': 768},
        locale='uk-UA',
    )
    page = context.new_page()

    # Збираємо перші 5 сторінок (сторінки від 1 до 5)
    for page_num in range(1, 6):
      url = f'https://ek.ua/ua/ek-list.php?katalog_=699&page={page_num}'
      print(f'Завантаження сторінки {page_num}: {url}')

      try:
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        time.sleep(2)

        page.evaluate('window.scrollTo(0, document.body.scrollHeight / 2);')
        time.sleep(1)

        soup = BeautifulSoup(page.content(), 'html.parser')
        items = soup.select('.model-short-block') or soup.select('tr[id^="tr_"]')

        print(f'Знайдено товарів на сторінці {page_num}: {len(items)}')

        for item in items:
          # Пробуємо знайти назву будь-яким доступним способом всередині картки товару
          title_elem = (
              item.select_one('.model-short-title')
              or item.select_one('a.h')
              or item.select_one('.r-big1')
              or item.find('a')
          )
          model_name = title_elem.get_text(strip=True) if title_elem else ''

          if not model_name or len(model_name) < 2:
            continue

          # Шукаємо опис
          desc_elem = item.select_one('.model-short-description') or item.select_one('.-des')
          description = desc_elem.get_text(' ', strip=True) if desc_elem else 'Зовнішній акумулятор'

          # Шукаємо ціну в картці
          price_elem = (
              item.select_one('.model-hot-prices-price')
              or item.select_one('.it-price')
              or item.select_one('span[class*="price"]')
              or item.select_one('.price')
          )
          
          price_text = price_elem.get_text(strip=True) if price_elem else ''
          price = clean_price(price_text)

          # Якщо ціни немає в блоці, спробуємо знайти хоч якісь цифри в самому тексті товару
          if not price:
            all_text = item.get_text()
            price = clean_price(all_text)

          if price and price > 50:  # Щоб відсіяти випадкові дрібні числа
            offers_data.append({
                'model': model_name,
                'params': description,
                'city': 'Київ',
                'shop': 'Інтернет-магазин',
                'price': price,
            })

      except Exception as e:
        print(f'Помилка на сторінці {page_num}: {e}')

    browser.close()

  # Записуємо зібрані дані у файл powerbanks.csv
  csv_file = 'powerbanks.csv'
  with open(csv_file, mode='w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(
        f, fieldnames=['model', 'params', 'city', 'shop', 'price']
    )
    writer.writeheader()
    writer.writerows(offers_data)

  print(
      f'\nУспішно! Збережено {len(offers_data)} записів у файл "{csv_file}".'
  )


if __name__ == '__main__':
  parse_ek_powerbanks()