import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from dotenv import load_dotenv
import undetected_chromedriver as uc
from time import sleep
import random
import datetime
import pytz

# Cargar variables de entorno
load_dotenv()


TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

SCRAPING_TIME = 3  #! Time in hours to execute the script again
BASE_URL = 'https://www.walmart.com.mx'
TIMEZONE = pytz.timezone('America/Mexico_City')


def scrap_products(urls: list) -> list:
    """
    Scrapes product data from Walmart's website.

    Parameters:
        urls (list): A list of URLs to scrape.

    Returns:
        list: A list of dictionaries containing product details.
    """
    products = []
    driver = uc.Chrome(log_level=0)  # Launch undetected Chrome browser
    for url in urls:
        page = 1
        while True:
            try:
                # Navigate to the URL with pagination
                driver.get(f"{url[0]}&page={page}&affinityOverride=default")
            except Exception as e:
                print(f"Error loading page: {e}")
                driver.quit()
                return products
            sleep(2)  # Wait for the page to load
            source = driver.page_source
            soup = BeautifulSoup(source, 'html.parser')

            # Check if there are no more items
            noItems = soup.find('div', class_='tc fw7 f-subheadline-m mb5 f1')
            if noItems:
                break

            # Extract product details
            items = soup.find_all('div', {'role': 'group'})
            for item in items:
                try:
                    name = item.find('span', {'data-automation-id': "product-title"}).get_text().strip()
                    sku = item.find('a').get('link-identifier')
                    divs_price = item.find('div', {'data-automation-id': "product-price"}).find_all('div', class_='mr1')
                    price = divs_price[0].get_text().strip()
                    old_price = divs_price[1].get_text().strip()
                    if '$' not in old_price:
                        old_price = divs_price[2].get_text().strip()

                    # Convert prices to float
                    price = float(price.replace('$', '').replace(',', ''))
                    old_price = float(old_price.replace('$', '').replace(',', ''))

                    # Calculate discount
                    discount = price / old_price
                    if discount > 0.6:  # Skip products with less than 40% discount
                        continue

                    product_url = BASE_URL + item.find('a').get('href')
                    products.append({
                        'name': name,
                        'id': sku,
                        'price': price,
                        'old price': old_price,
                        'descuento': 100 - round(discount * 100, 2),
                        'url': product_url
                    })
                except Exception as e:
                    print(f"Error processing item: {e}")
                    continue

            page += 1
            time.sleep(1)  # Pause to avoid overwhelming the server
            print(f'Products collected: {len(products)}')

    driver.quit()
    return products


def load_webs():
    global webs
    webs = []
    with open('url.csv', 'r') as file:
        reader = csv.reader(file, delimiter="|")
        for row in reader:
            webs.append(row)
    return webs

def send_telegram_message(message):
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'  # Format the message to get it shown right
    }

    response = requests.post(TELEGRAM_URL, data=payload)
    if response.status_code == 200:
        print(f"Productos enviados con éxito!")
    else:
        print(f"Error al enviar el producto: {response.text}")

def monitor_prices(products, info):
    """
    Monitors product prices and sends updates to Telegram.

    Parameters:
        products (list): A list of products to monitor.
        info (str): Additional information to include in the message.

    Returns:
        list: An empty list after processing.
    """
    random.shuffle(products)  # Shuffle the product list to randomize processing
    if len(products) == 0:
        return []

    for i in range(0, len(products), 8):  # Process in batches of 8 products
        if i in [200, 400, 600, 800, 1000]:
            sleep(40)  # Pause to avoid overwhelming the Telegram API
        message = ''
        for p in products[i:i + 8]:
            try:
                # Format the message for Telegram
                message += (
                    f"{info}{p['name']}\n"
                    f"ID: {p['id']}\n"
                    f"Previous Price: {p['old price']}\n"
                    f"Current Price: {p['price']}\n"
                    f"Discount: {p['descuento']}%\n\n"
                    f"{p['url']}\n\n"
                    "--------------------------\n"
                )
            except Exception as e:
                print(f"Error formatting product message: {e}")
                continue
        send_telegram_message(message)
        time.sleep(1)  # Pause between batches

    return []

def main():
    lastExecution = datetime.datetime(2024, 1, 1)
    DlastExecution = datetime.datetime(2000, 1, 1, 1, 1, 1)
    hora_inicio = datetime.time(13, 0) 
    hora_fin = datetime.time(23, 59)
    urls = load_webs()
    while True:
        timeNow = datetime.datetime.now(TIMEZONE) + datetime.timedelta(minutes=10) 
        if timeNow.strftime('%d-%m-%y') != DlastExecution.strftime('%d-%m-%y'):
            print("Recopilando productos de Walmart...")
            all_products = scrap_products(urls)
            products = all_products.copy()
            DlastExecution = datetime.datetime.now(TIMEZONE)
            print('Productos restantes:', len(all_products))
            info = ''
            
        elif (datetime.datetime.now() - lastExecution).total_seconds() >= SCRAPING_TIME * 60 and len(all_products) == 0:
            print("Recopilando nuevos productos de Walmart...")
            Tproducts = scrap_products(urls)
            Tproducts_set = {frozenset(product.items()) for product in Tproducts}
            products_set = {frozenset(product.items()) for product in products}

            Newproducts_set = Tproducts_set - products_set
            all_products = [dict(product) for product in Newproducts_set]
            lastExecution = datetime.datetime.now()
            print('Productos restantes:', len(all_products))
            if len(all_products) != 0:
                for i in all_products:
                    products.append(i)
                info = 'Nuevo Producto Añadido!\n'
            else:
                send_telegram_message('No hay nuevos productos')
            
        

        if len(all_products) == 0:
            print('Esperando al siguiente escaneo...')
        else:
            print("Iniciando monitoreo de precios...")
            all_products = monitor_prices(all_products, info)
            print('\nEsperando 1 minutos para volver a monitorear...')
            print('Productos restantes:', len(all_products))
        sleep(60)
        

if __name__ == "__main__":
    main()