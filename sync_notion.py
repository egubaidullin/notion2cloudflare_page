import requests
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
        logging.info("Fetched Notion page successfully.")
        return response.text  # Возвращаем HTML-код страницы
    except requests.RequestException as e:
        logging.error(f"Error fetching Notion page: {e}")
        raise

def publish_to_cloudflare(html_content):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects/{CLOUDFLARE_PROJECT}/deployments"
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    }

    # Загрузка HTML-кода
    files = {
        'index.html': ('index.html', html_content, 'text/html')
    }

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
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
        html_content = get_notion_content()  # Получаем HTML-код страницы
        publish_to_cloudflare(html_content)  # Загружаем HTML на Cloudflare
        logging.info("Sync and publish completed successfully")
    except Exception as e:
        logging.error(f"Sync failed: {e}")

if __name__ == "__main__":
    main()
