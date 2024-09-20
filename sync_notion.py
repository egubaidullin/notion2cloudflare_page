import requests
from bs4 import BeautifulSoup
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# URL вашей публичной страницы Notion
NOTION_PAGE_URL = "https://egub.notion.site/Tips-and-scripts-for-the-job-2939fb1d8d514e25af07d9596b52cdbe"

def get_notion_content():
    try:
        response = requests.get(NOTION_PAGE_URL)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching Notion page: {e}")
        raise

def parse_notion_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Извлечение заголовка
    title = soup.find('title').text if soup.find('title') else 'Untitled'
    
    # Находим основной контейнер с контентом
    main_content = soup.find('div', class_='notion-page-content')
    
    if not main_content:
        logging.warning("Main content not found. The page structure might have changed.")
        return f"<h1>{title}</h1><p>Content could not be extracted.</p>"

    content_html = f"<h1>{title}</h1>"

    # Извлечение всех блоков контента
    for block in main_content.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol', 'img']):
        if block.name == 'p':
            content_html += f"<p>{block.text}</p>"
        elif block.name.startswith('h'):
            content_html += f"<{block.name}>{block.text}</{block.name}>"
        elif block.name == 'ul':
            content_html += "<ul>"
            for li in block.find_all('li'):
                content_html += f"<li>{li.text}</li>"
            content_html += "</ul>"
        elif block.name == 'ol':
            content_html += "<ol>"
            for li in block.find_all('li'):
                content_html += f"<li>{li.text}</li>"
            content_html += "</ol>"
        elif block.name == 'img':
            img_src = block['src'] if 'src' in block.attrs else ''
            content_html += f'<img src="{img_src}" alt="Image"/>'

    return content_html


def save_to_file(parsed_content, filename="index.html"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(parsed_content)
    logging.info(f"Content saved to {filename}")

def main():
    try:
        logging.info("Starting Notion page sync...")
        html_content = get_notion_content()
        parsed_content = parse_notion_content(html_content)
        save_to_file(parsed_content)
        logging.info("Sync completed successfully")
    except Exception as e:
        logging.error(f"Sync failed: {e}")

if __name__ == "__main__":
    main()
