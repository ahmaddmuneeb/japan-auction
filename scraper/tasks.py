# scraper/tasks.py
import re
import requests
from bs4 import BeautifulSoup
from celery import shared_task
from lxml import html
import time
from .models import Car, CarImage
from django.db import transaction
from car_scraper.celery import app
from deep_translator import GoogleTranslator  # Import from deep-translator
import logging

# Configure logging
logger = logging.getLogger(__name__)

@app.task()
def scrape_cars():
    def fetch_links(offset):
        url = f"https://www.goo-net.com/php/search/summary.php?maker_cd=1010&integration_car_cd=10101040%7C&lite_top=true&offset={offset}"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            tree = html.fromstring(response.content)
            hrefs = tree.xpath("//div[@class='data-wrapper']//div[@class='heading_inner browse_heading']/h3/a/@href")
            logger.info(f"Fetched {len(hrefs)} links at offset {offset}")
            return hrefs
        except requests.RequestException as e:
            logger.error(f"Failed to fetch links at offset {offset}: {e}")
            return []

    def translate_text(text, source_lang='auto', target_lang='en'):
        try:
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
            return translated
        except Exception as e:
            logger.error(f"Deep-Translator error: {e}")
            return text

    def fetch_car_data(href):
        url = f"https://www.goo-net.com{href}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract JavaScript content
            script_content = soup.find("script", text=re.compile("var STOCK_ID"))
            if not script_content or not script_content.string:
                logger.warning(f"No valid script content found for {href}")
                return None

            script_content = script_content.string
            patterns = {
                "stock_id": r'var STOCK_ID\s*=\s*"(.+?)";',
                "car_brand_name": r'var CAR_BRAND_NAME\s*=\s*"(.+?)";',
                "car_name": r'var CAR_NAME\s*=\s*"(.+?)";',
                "car_year": r'var CAR_SYEAR\s*=\s*"(.+?)";',
                "price": r'var CAR_PRICE\s*=\s*"(.+?)";',
                "total_price": r'var CAR_TOTAL_PRICE\s*=\s*"(.+?)";',
                "distance": r'var CAR_DISTANCE\s*=\s*"(.+?)";',
                "fuel": r'var CAR_FUEL\s*=\s*"(.+?)";',
                "body_color": r'var CAR_BODY_COLOR\s*=\s*"(.+?)";',
                "location": r'var CLIENT_PREFECTURE\s*=\s*"(.+?)";',
            }

            car_data = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, script_content)
                car_data[key] = match.group(1) if match else "N/A"

            # Translate specific fields
            try:
                car_data["car_name"] = translate_text(car_data["car_name"], target_lang='en')
                print(car_data['car_name'])
            except Exception as e:
                logger.error(f"Translation error for 'car_name': {e}")
                car_data["car_name"] = car_data.get("car_name", "N/A")

            try:
                car_data["fuel"] = translate_text(car_data["fuel"], target_lang='en')
            except Exception as e:
                logger.error(f"Translation error for 'fuel': {e}")
                car_data["fuel"] = car_data.get("fuel", "N/A")

            try:
                car_data["body_color"] = translate_text(car_data["body_color"], target_lang='en')
            except Exception as e:
                logger.error(f"Translation error for 'body_color': {e}")
                car_data["body_color"] = car_data.get("body_color", "N/A")

            try:
                car_data["location"] = translate_text(car_data["location"], target_lang='en')
            except Exception as e:
                logger.error(f"Translation error for 'location': {e}")
                car_data["location"] = car_data.get("location", "N/A")


            try:
                car_data["car_brand_name"] = translate_text(car_data["car_brand_name"], target_lang='en')
            except Exception as e:
                logger.error(f"Translation error for 'car_brand_name': {e}")
                car_data["car_brand_name"] = car_data.get("car_brand_name", "N/A")

            # Extract image URLs
            image_tags = soup.select("div.item.image img[data-lazy]")
            car_data["image_urls"] = [img['data-lazy'] for img in image_tags if 'data-lazy' in img.attrs]

            return car_data
        except requests.RequestException as e:
            logger.error(f"Failed to fetch car data from {href}: {e}")
            return None

    offset = 0
    while True:
        hrefs = fetch_links(offset)
        if not hrefs:
            logger.info("No more links to process, terminating.")
            break

        for href in hrefs:
            car_data = fetch_car_data(href)
            if car_data:
                logger.info(f"Fetched car data: {car_data['stock_id']}")
                with transaction.atomic():
                    # Update or create car
                    car, created = Car.objects.update_or_create(
                        stock_id=car_data['stock_id'],
                        defaults={
                            'car_brand_name': car_data['car_brand_name'],
                            'car_name': car_data['car_name'],
                            'car_year': car_data['car_year'],
                            'price': car_data['price'],
                            'total_price': car_data['total_price'],
                            'distance': car_data['distance'],
                            'fuel': car_data['fuel'],
                            'body_color': car_data['body_color'],
                            'location': car_data['location'],
                        }
                    )

                    # Delete existing images and create new ones
                    CarImage.objects.filter(car=car).delete()
                    for image_url in car_data['image_urls']:
                        CarImage.objects.create(car=car, image_url=image_url)

            time.sleep(1)  # Throttle requests to avoid bans
        offset += 50
