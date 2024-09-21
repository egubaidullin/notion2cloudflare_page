import requests
import logging
import os
import json
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NOTION_PAGE_URL = "https://egub.notion.site/Tips-and-scripts-for-the-job-2939fb1d8d514e25af07d9596b52cdbe"
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
CLOUDFLARE_PROJECT = os.getenv('CLOUDFLARE_PROJECT')

def get_notion_content():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(NOTION_PAGE_URL, headers=headers)
        response.raise_for_status()
        logging.info("Fetched Notion page successfully.")
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching Notion page: {e}")
        raise

def process_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try to find the main content
    main_content = soup.find('div', class_='notion-page-content')
    
    if not main_content:
        # If we can't find the specific class, let's try to get all the content
        main_content = soup.find('body')
        if not main_content:
            logging.error("Could not find any content")
            return None
    
    # Remove script tags
    for script in main_content(["script", "style"]):
        script.decompose()
    
    # Create a new HTML structure
    new_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tips and scripts for the job</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
                line-height: 1.6;
                color: #37352f;
                margin: 0;
                padding: 20px;
            }}
            .content {{
                max-width: 900px;
                margin: 0 auto;
            }}
            h1, h2, h3 {{
                margin-top: 24px;
                margin-bottom: 16px;
            }}
            pre {{
                background-color: #f6f6f6;
                padding: 16px;
                border-radius: 4px;
                overflow-x: auto;
            }}
            code {{
                font-family: SFMono-Regular, Consolas, 'Liberation Mono', Menlo, Courier, monospace;
            }}
        </style>
    </head>
    <body>
        <div class="content">
            {main_content}
        </div>
    </body>
    </html>
    """
    
    return new_html

def deploy_to_cloudflare(html_content):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/pages/projects/{CLOUDFLARE_PROJECT}/deployments"
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "multipart/form-data"
    }

    # Создаем временный файл index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Создаем манифест файлов
    manifest = {
        "version": 1,
        "include": ["index.html"],
        "exclude": []
    }

    # Формируем данные для отправки
    files = {
        'manifest': ('manifest.json', json.dumps(manifest), 'application/json'),
        'index.html': ('index.html', open('index.html', 'rb'), 'text/html')
    }

    data = {
        "branch": "main"  # или используйте нужную вам ветку
    }

    try:
        logging.info(f"Sending request to URL: {url}")
        logging.info(f"Headers: {headers}")
        logging.info(f"Files: {files.keys()}")
        response = requests.post(url, headers=headers, data=data, files=files)
        response.raise_for_status()
        deployment = response.json()
        logging.info(f"Deployment successful. URL: {deployment['result']['url']}")
    except requests.RequestException as e:
        logging.error(f"Error publishing to Cloudflare Pages: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Response content: {e.response.content}")
        raise
    finally:
        # Удаляем временные файлы
        os.remove('index.html')
        os.remove('manifest.json')

def main():
    try:
        logging.info(f"CLOUDFLARE_ACCOUNT_ID: {CLOUDFLARE_ACCOUNT_ID}")
        logging.info(f"CLOUDFLARE_PROJECT: {CLOUDFLARE_PROJECT}")
        logging.info(f"CLOUDFLARE_API_TOKEN: {'*' * len(CLOUDFLARE_API_TOKEN) if CLOUDFLARE_API_TOKEN else 'Not set'}")
        logging.info("Starting Notion page sync...")
        html_content = get_notion_content()
        processed_html = process_html(html_content)
        if processed_html:
            deploy_to_cloudflare(processed_html)
            logging.info("Sync and deploy completed successfully")
        else:
            logging.error("Failed to process HTML content")
    except Exception as e:
        logging.error(f"Sync failed: {e}")

if __name__ == "__main__":
    main()
