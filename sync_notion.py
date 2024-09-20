import requests
import hashlib
import json
from bs4 import BeautifulSoup
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# URL вашей публичной страницы Notion
NOTION_PAGE_URL = "https://egub.notion.site/Tips-and-scripts-for-the-job-2939fb1d8d514e25af07d9596b52cdbe"

# Cloudflare API параметры
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
CLOUDFLARE_PROJECT = os.getenv('CLOUDFLARE_PROJECT')

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
    
    # Извлекаем весь контент
    main_content = soup.body

    if not main_content:
        logging.warning("Main content not found. The page structure might have changed.")
        return f"<h1>{title}</h1><p>Content could not be extracted.</p>"

    return f"<h1>{title}</h1>{main_content}"

def create_manifest(html_content):
    # Создание манифеста с хешем файла
    file_hash = hashlib.sha256(html_content.encode('utf-8')).hexdigest()
    
    manifest = {
        "files": {
            "/index.html": {
                "path": "index.html",
                "hash": file_hash
            }
        }
    }
    return manifest

def publish_to_cloudflare(html_content):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects/{CLOUDFLARE_PROJECT}/deployments"
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # Создаем SHA256 хеш для index.html
    file_hash = hashlib.sha256(html_content.encode('utf-8')).hexdigest()
    
    # Формируем манифест с хэшом
    manifest = {
        "files": {
            "/index.html": {
                "path": "index.html",
                "hash": file_hash
            }
        }
    }

    # Формируем JSON данные для запроса
    data = {
        "manifest": manifest,  # Манифест обязателен для деплоя
        "files": {
            "/index.html": html_content  # Контент HTML файла
        }
    }

    try:
        # Отправляем запрос на деплой
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Проверяем успешность запроса
        deployment = response.json()
        logging.info(f"Deployment successful. URL: {deployment['result']['url']}")
    except requests.RequestException as e:
        logging.error(f"Error publishing to Cloudflare Pages: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Response content: {e.response.content}")
        raise

def main():
    try:
        logging.info("Starting Notion page sync...")
        html_content = get_notion_content()
        parsed_content = parse_notion_content(html_content)
        publish_to_cloudflare(parsed_content)
        logging.info("Sync and publish completed successfully")
    except Exception as e:
        logging.error(f"Sync failed: {e}")

if __name__ == "__main__":
    main()
