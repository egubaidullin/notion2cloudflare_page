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
    title = soup.find('title').text if soup.find('title') else 'Untitled'
    main_content = soup.find('div', class_='notion-page-content')
    
    if not main_content:
        logging.warning("Main content not found. The page structure might have changed.")
        return f"<h1>{title}</h1><p>Content could not be extracted.</p>"
    
    return f"<h1>{title}</h1>{main_content}"

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
