import os
import logging
from notion_client import Client
from notion_client.errors import APIResponseError
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение токенов из переменных окружения
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

# Удаление дефисов из ID базы данных
if NOTION_DATABASE_ID:
    NOTION_DATABASE_ID = NOTION_DATABASE_ID.replace('-', '')

# Проверка, что переменные окружения загружены
if not NOTION_API_TOKEN or not NOTION_DATABASE_ID:
    logging.error("Missing NOTION_API_TOKEN or NOTION_DATABASE_ID. Please check your environment variables.")
    exit(1)

# Инициализация клиента Notion
notion = Client(auth=NOTION_API_TOKEN)

def get_notion_page():
    try:
        logging.info(f"Attempting to query database with ID: {NOTION_DATABASE_ID}")
        # Получение одной страницы из базы данных
        pages = notion.databases.query(database_id=NOTION_DATABASE_ID).get('results')
        if not pages:
            raise ValueError("No pages found in the database.")
        logging.info(f"Successfully retrieved {len(pages)} pages from the database")
        logging.info(f"Page ID: {pages[0]['id']}")
        return pages[0]  # Возвращаем первую страницу
    except APIResponseError as e:
        logging.error(f"Error querying Notion database: {e}")
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
