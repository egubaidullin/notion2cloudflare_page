import os
import logging
from notion_client import Client
from notion_client.errors import APIResponseError
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

notion = Client(auth=NOTION_API_TOKEN)

def get_notion_page():
    try:
        logging.info(f"Attempting to retrieve the page with ID: {NOTION_DATABASE_ID}")
        page = notion.pages.retrieve(page_id=NOTION_DATABASE_ID)
        logging.info("Successfully retrieved the page")
        return page
    except APIResponseError as e:
        logging.error(f"Error retrieving the Notion page: {e}")
        if e.code == "object_not_found":
            logging.error("The page ID may be incorrect or the integration may not have access to it.")
        raise

def convert_to_html(page):
    try:
        page_id = page['id']
        blocks = notion.blocks.children.list(block_id=page_id).get('results')

        soup = BeautifulSoup('<html><head></head><body></body></html>', 'html.parser')
        body = soup.body

        # Извлекаем заголовок страницы
        title = page['properties'].get('Name', {}).get('title', [{}])[0].get('plain_text', 'Untitled')
        h1 = soup.new_tag('h1')
        h1.string = title
        body.append(h1)

        # Преобразуем блоки страницы в HTML
        for block in blocks:
            if block['type'] == 'paragraph':
                p = soup.new_tag('p')
                p.string = block['paragraph']['rich_text'][0]['plain_text'] if block['paragraph']['rich_text'] else ''
                body.append(p)
            elif block['type'] == 'heading_1':
                h1 = soup.new_tag('h1')
                h1.string = block['heading_1']['rich_text'][0]['plain_text']
                body.append(h1)

        return str(soup)
    except Exception as e:
        logging.error(f"Error converting page {page['id']} to HTML: {e}")
        raise

def save_html(html, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        logging.info(f"Successfully saved HTML to {filename}")
    except Exception as e:
        logging.error(f"Error saving HTML to {filename}: {e}")
        raise

def main():
    try:
        # Получаем страницу по ID
        page = get_notion_page()

        # Преобразуем страницу в HTML
        html = convert_to_html(page)

        # Сохраняем как index.html
        save_html(html, 'index.html')

        logging.info("Sync completed successfully")
    except Exception as e:
        logging.error(f"Sync failed: {e}")

if __name__ == "__main__":
    main()
