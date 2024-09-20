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
NOTION_PAGE_ID = os.getenv('NOTION_PAGE_ID')

# Проверка, что переменные окружения загружены
if not NOTION_API_TOKEN or not NOTION_PAGE_ID:
    logging.error("Missing NOTION_API_TOKEN or NOTION_PAGE_ID. Please check your environment variables.")
    exit(1)

# Инициализация клиента Notion
notion = Client(auth=NOTION_API_TOKEN)

def get_notion_page_content(page_id):
    """Получает контент страницы в виде блоков."""
    try:
        logging.info(f"Attempting to retrieve blocks for page with ID: {page_id}")
        # Получение блоков страницы
        blocks = notion.blocks.children.list(block_id=page_id).get('results')
        if not blocks:
            raise ValueError(f"No blocks found for page ID: {page_id}")
        logging.info(f"Successfully retrieved {len(blocks)} blocks from the page")
        return blocks
    except APIResponseError as e:
        logging.error(f"Error retrieving blocks for page: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

def convert_to_html(blocks):
    """Конвертирует блоки страницы в HTML формат."""
    try:
        soup = BeautifulSoup('<html><head></head><body></body></html>', 'html.parser')
        body = soup.body

        # Пример получения заголовка страницы (если он есть)
        title_tag = soup.new_tag('h1')
        title_tag.string = "Page Title"
        body.append(title_tag)

        # Проход по блокам страницы и их конвертация в HTML
        for block in blocks:
            if block['type'] == 'paragraph':
                p = soup.new_tag('p')
                p.string = block['paragraph']['rich_text'][0]['plain_text'] if block['paragraph']['rich_text'] else ''
                body.append(p)
            elif block['type'] == 'heading_1':
                h1 = soup.new_tag('h1')
                h1.string = block['heading_1']['rich_text'][0]['plain_text']
                body.append(h1)
            elif block['type'] == 'heading_2':
                h2 = soup.new_tag('h2')
                h2.string = block['heading_2']['rich_text'][0]['plain_text']
                body.append(h2)
            elif block['type'] == 'heading_3':
                h3 = soup.new_tag('h3')
                h3.string = block['heading_3']['rich_text'][0]['plain_text']
                body.append(h3)
            # Добавьте другие типы блоков по необходимости

        return str(soup)
    except Exception as e:
        logging.error(f"Error converting blocks to HTML: {e}")
        raise

def save_html(html, filename):
    """Сохраняет HTML в файл."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        logging.info(f"Successfully saved HTML to {filename}")
    except Exception as e:
        logging.error(f"Error saving HTML to {filename}: {e}")
        raise

def main():
    try:
        logging.info("Starting Notion page to HTML sync...")
        blocks = get_notion_page_content(NOTION_PAGE_ID)
        html = convert_to_html(blocks)
        save_html(html, "index.html")
        logging.info("Sync completed successfully")
    except Exception as e:
        logging.error(f"Sync failed: {e}")

if __name__ == "__main__":
    main()
