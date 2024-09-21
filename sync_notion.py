import os
import requests
import logging
import json
from html import escape

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_PAGE_ID = os.getenv('NOTION_PAGE_ID')

NOTION_API_URL = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children"

headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Notion-Version": "2022-06-28"
}

def get_notion_content():
    all_blocks = []
    has_more = True
    start_cursor = None

    while has_more:
        try:
            params = {"page_size": 100}
            if start_cursor:
                params["start_cursor"] = start_cursor

            response = requests.get(NOTION_API_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            all_blocks.extend(data['results'])
            has_more = data['has_more']
            start_cursor = data.get('next_cursor')

            logging.info(f"Fetched {len(data['results'])} blocks. Total blocks: {len(all_blocks)}")

        except requests.RequestException as e:
            logging.error(f"Error fetching Notion page content: {e}")
            raise

    return all_blocks

def convert_to_html(blocks, level=0):
    html_content = []
    list_type = None

    for block in blocks:
        block_type = block['type']
        if block_type == 'paragraph':
            html_content.append(f"<p>{get_text_content(block['paragraph']['rich_text'])}</p>")
        elif block_type.startswith('heading_'):
            level = int(block_type[-1])
            text = get_text_content(block[block_type]['rich_text'])
            heading_id = text.replace(" ", "-").lower()
            html_content.append(f"<h{level} id='{heading_id}'>{text}</h{level}>")
        elif block_type == 'bulleted_list_item':
            if list_type != 'ul':
                if list_type:
                    html_content.append(f"</{'ol' if list_type == 'ol' else 'ul'}>")
                html_content.append("<ul>")
                list_type = 'ul'
            html_content.append(f"<li>{get_text_content(block['bulleted_list_item']['rich_text'])}</li>")
        elif block_type == 'numbered_list_item':
            if list_type != 'ol':
                if list_type:
                    html_content.append(f"</{'ol' if list_type == 'ol' else 'ul'}>")
                html_content.append("<ol>")
                list_type = 'ol'
            html_content.append(f"<li>{get_text_content(block['numbered_list_item']['rich_text'])}</li>")
        elif block_type == 'code':
            code = escape(get_text_content(block['code']['rich_text']))
            language = block['code']['language']
            html_content.append(f"<pre><code class='{language}'>{code}</code></pre>")
        elif block_type == 'image':
            image_url = block['image']['file']['url']
            html_content.append(f"<img src='{image_url}' alt='Notion image'>")
        elif block_type == 'divider':
            html_content.append("<hr>")
        elif block_type == 'quote':
            html_content.append(f"<blockquote>{get_text_content(block['quote']['rich_text'])}</blockquote>")
        elif block_type == 'callout':
            emoji = block['callout']['icon']['emoji'] if block['callout']['icon']['type'] == 'emoji' else ''
            text = get_text_content(block['callout']['rich_text'])
            html_content.append(f"<div class='callout'>{emoji} {text}</div>")
        
        if 'has_children' in block and block['has_children']:
            child_blocks = get_child_blocks(block['id'])
            html_content.extend(convert_to_html(child_blocks, level + 1))

    if list_type:
        html_content.append(f"</{'ol' if list_type == 'ol' else 'ul'}>")

    return ''.join(html_content)  # Join the list into a single string

def get_child_blocks(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['results']

def get_text_content(rich_text):
    return ''.join([t['plain_text'] for t in rich_text])

def get_title(blocks):
    for block in blocks:
        if block['type'] == 'heading_1':
            return get_text_content(block['heading_1']['rich_text'])
    return "Your Page Title from Notion"

def generate_toc(blocks):
    toc = []
    for block in blocks:
        if block['type'].startswith('heading_'):
            level = int(block['type'][-1])
            text = get_text_content(block[block['type']]['rich_text'])
            heading_id = text.replace(" ", "-").lower()
            toc.append(f"<li class='toc-item' style='margin-left: {level * 20}px;'><a href='#{heading_id}'>{text}</a></li>")
    return "<ul class='toc'>" + ''.join(toc) + "</ul>"

def save_html(toc, html_content, title, filename='index.html'):
    try:
        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
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
                .toc {{
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #f9f9f9;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    z-index: 1000;
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
                .callout {{
                    background-color: #f1f1f1;
                    padding: 16px;
                    border-radius: 4px;
                    margin-bottom: 16px;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            <div class="content">
                <h1>{title}</h1>
                {toc}
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
        title = get_title(notion_content)  # Extract title from Notion
        toc = generate_toc(notion_content)  # Generate TOC from Notion content
        save_html(toc, html_content, title)  # Call save_html with TOC, content, and title
        logging.info("Sync completed successfully")
    except Exception as e:
        logging.error(f"Sync failed: {e}")
        raise

if __name__ == "__main__":
    main()
