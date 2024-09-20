import os
from notion_client import Client
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

notion = Client(auth=NOTION_API_TOKEN)

def get_notion_pages():
    pages = notion.databases.query(database_id=NOTION_DATABASE_ID).get('results')
    return pages

def convert_to_html(page):
    # Получаем содержимое страницы
    page_id = page['id']
    blocks = notion.blocks.children.list(block_id=page_id).get('results')

    # Создаем HTML-структуру
    soup = BeautifulSoup('<html><head></head><body></body></html>', 'html.parser')
    body = soup.body

    # Добавляем заголовок
    title = page['properties']['Name']['title'][0]['plain_text']
    h1 = soup.new_tag('h1')
    h1.string = title
    body.append(h1)

    # Преобразуем блоки в HTML
    for block in blocks:
        if block['type'] == 'paragraph':
            p = soup.new_tag('p')
            p.string = block['paragraph']['rich_text'][0]['plain_text'] if block['paragraph']['rich_text'] else ''
            body.append(p)
        elif block['type'] == 'heading_1':
            h1 = soup.new_tag('h1')
            h1.string = block['heading_1']['rich_text'][0]['plain_text']
            body.append(h1)
        # Добавьте обработку других типов блоков по необходимости

    return str(soup)

def save_html(html, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    pages = get_notion_pages()
    for page in pages:
        html = convert_to_html(page)
        title = page['properties']['Name']['title'][0]['plain_text']
        filename = f"{title.lower().replace(' ', '-')}.html"
        save_html(html, filename)

if __name__ == "__main__":
    main()
