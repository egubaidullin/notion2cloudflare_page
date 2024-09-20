import os
import logging
from notion_client import Client
from notion_client.errors import APIResponseError
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение токенов из переменных окружения
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_RESOURCE_ID = os.getenv('NOTION_RESOURCE_ID')  # Переименовано для большей гибкости

logging.debug(f"Initial NOTION_RESOURCE_ID: {NOTION_RESOURCE_ID}")

# Удаление дефисов из ID ресурса
if NOTION_RESOURCE_ID:
    NOTION_RESOURCE_ID_NO_HYPHENS = NOTION_RESOURCE_ID.replace('-', '')
    logging.debug(f"NOTION_RESOURCE_ID after removing hyphens: {NOTION_RESOURCE_ID_NO_HYPHENS}")

# Проверка, что переменные окружения загружены
if not NOTION_API_TOKEN or not NOTION_RESOURCE_ID:
    logging.error("Missing NOTION_API_TOKEN or NOTION_RESOURCE_ID. Please check your environment variables.")
    exit(1)

# Инициализация клиента Notion
notion = Client(auth=NOTION_API_TOKEN)

def get_notion_content():
    try:
        logging.info(f"Attempting to query Notion resource with ID: {NOTION_RESOURCE_ID}")
        
        # Пробуем сначала как базу данных
        try:
            response = notion.databases.query(database_id=NOTION_RESOURCE_ID_NO_HYPHENS)
            logging.debug("Successfully queried as database")
            return response.get('results')[0] if response.get('results') else None
        except APIResponseError as e:
            if e.code == "object_not_found":
                logging.debug("Not a database, trying as a page")
                # Если не база данных, пробуем как страницу
                response = notion.pages.retrieve(page_id=NOTION_RESOURCE_ID)
                logging.debug("Successfully retrieved as page")
                return response
            else:
                raise

    except APIResponseError as e:
        logging.error(f"Error querying Notion resource: {e}")
        logging.error(f"Error details: {e.code} - {e.body}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

def convert_to_html(page):
    try:
        page_id = page['id']
        blocks = notion.blocks.children.list(block_id=page_id).get('results')
        logging.info(f"Retrieved {len(blocks)} blocks from page {page_id}")

        soup = BeautifulSoup('<html><head></head><body></body></html>', 'html.parser')
        body = soup.body

        title = page['properties'].get('Name', {}).get('title', [{}])[0].get('plain_text', 'Untitled')
        h1 = soup.new_tag('h1')
        h1.string = title
        body.append(h1)

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
        logging.info("Starting Notion to HTML sync...")
        page = get_notion_page()
        html = convert_to_html(page)
        save_html(html, "index.html")
        logging.info("Sync completed successfully")
    except Exception as e:
        logging.error(f"Sync failed: {e}")

if __name__ == "__main__":
    main()
