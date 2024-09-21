import os
import requests
import logging
import json
import markdown2

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_PAGE_ID = os.getenv('NOTION_PAGE_ID')

NOTION_API_URL = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children"

headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Notion-Version": "2022-06-28"
}

def get_notion_content():
    try:
        response = requests.get(NOTION_API_URL, headers=headers)
        response.raise_for_status()
        logging.info("Fetched Notion page content successfully.")
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching Notion page content: {e}")
        raise

def convert_to_html(blocks):
    html_content = []
    for block in blocks['results']:
        if block['type'] == 'paragraph':
            text = block['paragraph']['rich_text']
            if text:
                html_content.append(f"<p>{text[0]['plain_text']}</p>")
        elif block['type'] == 'heading_1':
            text = block['heading_1']['rich_text']
            if text:
                html_content.append(f"<h1>{text[0]['plain_text']}</h1>")
        elif block['type'] == 'heading_2':
            text = block['heading_2']['rich_text']
            if text:
                html_content.append(f"<h2>{text[0]['plain_text']}</h2>")
        elif block['type'] == 'heading_3':
            text = block['heading_3']['rich_text']
            if text:
                html_content.append(f"<h3>{text[0]['plain_text']}</h3>")
        elif block['type'] == 'bulleted_list_item':
            text = block['bulleted_list_item']['rich_text']
            if text:
                html_content.append(f"<li>{text[0]['plain_text']}</li>")
        elif block['type'] == 'numbered_list_item':
            text = block['numbered_list_item']['rich_text']
            if text:
                html_content.append(f"<li>{text[0]['plain_text']}</li>")
        elif block['type'] == 'code':
            code = block['code']['rich_text'][0]['plain_text']
            language = block['code']['language']
            html_content.append(f"<pre><code class='{language}'>{code}</code></pre>")
    
    return "\n".join(html_content)

def save_html(html_content, filename='index.html'):
    try:
        full_html = f"""
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
                {html_content}
            </div>
        </body>
        </html>
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_html)
        logging.info(f"HTML content saved to {filename}")
    except IOError as e:
        logging.error(f"Error saving HTML content: {e}")
        raise

def main():
    try:
        logging.info("Starting Notion page sync...")
        notion_content = get_notion_content()
        html_content = convert_to_html(notion_content)
        save_html(html_content)
        logging.info("Sync completed successfully")
    except Exception as e:
        logging.error(f"Sync failed: {e}")

if __name__ == "__main__":
    main()
