import requests
import logging
import os
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NOTION_PAGE_URL = "https://egub.notion.site/Tips-and-scripts-for-the-job-2939fb1d8d514e25af07d9596b52cdbe"

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
    
    main_content = soup.find('div', class_='notion-page-content')
    
    if not main_content:
        main_content = soup.find('body')
        if not main_content:
            logging.error("Could not find any content")
            return None
    
    for script in main_content(["script", "style"]):
        script.decompose()
    
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

def save_html(html_content, filename='index.html'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"HTML content saved to {filename}")
    except IOError as e:
        logging.error(f"Error saving HTML content: {e}")
        raise

def main():
    try:
        logging.info("Starting Notion page sync...")
        html_content = get_notion_content()
        processed_html = process_html(html_content)
        if processed_html:
            save_html(processed_html)
            logging.info("Sync completed successfully")
        else:
            logging.error("Failed to process HTML content")
    except Exception as e:
        logging.error(f"Sync failed: {e}")

if __name__ == "__main__":
    main()
