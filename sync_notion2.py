import os
import requests
import logging
from html import escape

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_PAGE_IDS = os.getenv('NOTION_PAGE_IDS').split(",")

# Add logging to check if NOTION_PAGE_IDS is set
if NOTION_PAGE_IDS is None:
    logging.error("Environment variable 'NOTION_PAGE_IDS' is not set or is None.")
    raise ValueError("The 'NOTION_PAGE_IDS' environment variable is required but is not set.")
else:
    logging.info(f"NOTION_PAGE_IDS: {NOTION_PAGE_IDS}")

# Check if NOTION_API_TOKEN is set
if NOTION_API_TOKEN is None:
    logging.error("Environment variable 'NOTION_API_TOKEN' is not set.")
    raise ValueError("The 'NOTION_API_TOKEN' environment variable is required but is not set.")

headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Notion-Version": "2022-06-28"
}

def get_notion_content(page_id):
    notion_api_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    all_blocks = []
    has_more = True
    start_cursor = None

    while has_more:
        try:
            params = {"page_size": 100}
            if start_cursor:
                params["start_cursor"] = start_cursor

            response = requests.get(notion_api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            all_blocks.extend(data['results'])
            has_more = data['has_more']
            start_cursor = data.get('next_cursor')

            logging.info(f"Fetched {len(data['results'])} blocks for page {page_id}. Total blocks: {len(all_blocks)}")

        except requests.RequestException as e:
            logging.error(f"Error fetching Notion page content: {e}")
            raise

    return all_blocks

def get_text_content(rich_text):
    return ''.join([t['plain_text'] for t in rich_text])

def convert_to_html(blocks):
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
        
        # Process child blocks if present
        if 'has_children' in block and block['has_children']:
            child_blocks = get_child_blocks(block['id'])
            html_content.extend(convert_to_html(child_blocks))

    # Close any open list
    if list_type:
        html_content.append(f"</{'ol' if list_type == 'ol' else 'ul'}>")

    return ''.join(html_content)  # Join the list into a single string

def get_child_blocks(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['results']

def get_title(page_id):
    try:
        url = f"https://api.notion.com/v1/pages/{page_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        page_data = response.json()

        # Получаем заголовок страницы из свойства title
        title_property = page_data.get("properties", {}).get("title", {}).get("title", [])
        if title_property:
            return title_property[0]["text"]["content"]

        logging.warning("Page title not found.")
        return "Your Page Title from Notion"

    except requests.RequestException as e:
        logging.error(f"Error fetching page title: {e}")
        raise

def generate_toc(blocks):
    toc = []
    for block in blocks:
        if block['type'].startswith('heading_'):
            level = int(block['type'][-1])
            text = get_text_content(block[block['type']]['rich_text'])
            heading_id = text.replace(" ", "-").lower()
            toc.append(f"<li class='toc-item' style='margin-left: {level * 20}px;'><a href='#{heading_id}'>{text}</a></li>")
    return "<ul class='toc'>" + ''.join(toc) + "</ul>"

def generate_navigation(pages_data):
    """
    Generates navigation HTML with links to all pages.
    :param pages_data: A list of tuples with (title, filename)
    :return: Navigation HTML string
    """
    nav_html = "<ul>"
    for title, filename in pages_data:
        nav_html += f"<li><a href='{filename}.html'>{title}</a></li>"
    nav_html += "</ul>"
    return nav_html

def save_html(toc, html_content, title, filename, navigation):
    try:
        with open('template.html', 'r', encoding='utf-8') as f:
            template = f.read()

        full_html = template.replace('{{ title }}', title) \
                            .replace('{{ toc }}', toc) \
                            .replace(f'{{ content_{filename} }}', html_content) \
                            .replace('{{ pages_navigation }}', navigation)

        with open(f'{filename}.html', 'w', encoding='utf-8') as f:
            f.write(full_html)
        logging.info(f"HTML content saved to {filename}.html")
    except IOError as e:
        logging.error(f"Error saving HTML content: {e}")
        raise

def main():
    try:
        logging.info("Starting Notion pages sync...")

        pages_data = []
        for idx, page_id in enumerate(NOTION_PAGE_IDS):
            logging.info(f"Processing page {page_id}")
            notion_content = get_notion_content(page_id)
            html_content = convert_to_html(notion_content)
            title = get_title(page_id)
            toc = generate_toc(notion_content)

            filename = f'page_{idx + 1}'
            pages_data.append((title, filename))  # Store title and filename for navigation
            save_html(toc, html_content, title, filename, '')  # Temporarily leave navigation empty

        # After all pages are processed, generate navigation and save each page again
        navigation = generate_navigation(pages_data)

        for title, filename in pages_data:
            # Re-save each page with navigation inserted
            notion_content = get_notion_content(NOTION_PAGE_IDS[pages_data.index((title, filename))])
            html_content = convert_to_html(notion_content)
            toc = generate_toc(notion_content)
            save_html(toc, html_content, title, filename, navigation)

        logging.info("Sync completed successfully")
    except Exception as e:
        logging.error(f"Sync failed: {e}")
        raise

if __name__ == "__main__":
    main()
