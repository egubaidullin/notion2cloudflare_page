import requests
import logging
import os
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NOTION_PAGE_URL = "https://egub.notion.site/Tips-and-scripts-for-the-job-2939fb1d8d514e25af07d9596b52cdbe"
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
CLOUDFLARE_PROJECT = os.getenv('CLOUDFLARE_PROJECT')

def get_notion_content():
    try:
        response = requests.get(NOTION_PAGE_URL)
        response.raise_for_status()
        logging.info("Fetched Notion page successfully.")
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching Notion page: {e}")
        raise

def process_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract the main content
    main_content = soup.find('div', class_='notion-page-content')
    
    if not main_content:
        logging.error("Could not find main content")
        return None
    
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
        "Content-Type": "application/json"
    }

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
