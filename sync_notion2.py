import os
import requests
import logging
from html import escape
from datetime import datetime
import json
from slugify import slugify

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_PAGE_IDS = os.getenv('NOTION_PAGE_IDS').split(',')
CLOUDFLARE_PAGES_DIR = 'pages'

headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Notion-Version": "2022-06-28"
}

def sanitize_title(title, max_length=50):
    """Sanitize and truncate the title."""
    sanitized = slugify(title)
    return sanitized[:max_length]

def get_notion_page_info(page_id):
    """Fetch page info including title, created and last edited time."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    page_data = response.json()
    
    title = page_data['properties']['title']['title'][0]['plain_text']
    created_time = page_data['created_time']
    last_edited_time = page_data['last_edited_time']
    
    return title, created_time, last_edited_time

def get_notion_content(page_id):
    all_blocks = []
    has_more = True
    start_cursor = None

    while has_more:
        try:
            params = {"page_size": 100}
            if start_cursor:
                params["start_cursor"] = start_cursor

            url = f"https://api.notion.com/v1/blocks/{page_id}/children"
            response = requests.get(url, headers=headers, params=params)
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
            heading_id = slugify(text)
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
            html_content.append(f"<pre><code class='language-{language}'>{code}</code></pre>")
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
            html_content.extend(convert_to_html(child_blocks))

    if list_type:
        html_content.append(f"</{'ol' if list_type == 'ol' else 'ul'}>")

    return ''.join(html_content)

def get_child_blocks(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['results']

def get_text_content(rich_text):
    return ''.join([t['plain_text'] for t in rich_text])

def generate_toc(blocks):
    toc = []
    for block in blocks:
        if block['type'].startswith('heading_'):
            level = int(block['type'][-1])
            text = get_text_content(block[block['type']]['rich_text'])
            heading_id = slugify(text)
            toc.append(f"<li class='toc-item' style='margin-left: {level * 20}px;'><a href='#{heading_id}'>{text}</a></li>")
    return "<ul class='toc'>" + ''.join(toc) + "</ul>"

def save_html(toc, html_content, title, filename, created_time, last_edited_time, all_pages):
    try:
        with open('template2.html', 'r', encoding='utf-8') as f:
            template = f.read()

        menu = "<ul>"
        for page in all_pages:
            menu += f"<li><a href='/{page['path']}'>{page['title']}</a></li>"
        menu += "</ul>"

        full_html = template.replace('{{ title }}', title) \
                            .replace('{{ toc }}', toc) \
                            .replace('{{ content }}', html_content) \
                            .replace('{{ created_time }}', created_time) \
                            .replace('{{ last_edited_time }}', last_edited_time) \
                            .replace('{{ menu }}', menu)

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_html)
        logging.info(f"HTML content saved to {filename}")
    except IOError as e:
        logging.error(f"Error saving HTML content: {e}")
        raise

def create_index_page(pages):
    index_content = "<h1>Index of Notion Pages</h1><ul>"
    for page in pages:
        index_content += f"<li><a href='/{page['path']}'>{page['title']}</a> (Last edited: {page['last_edited_time']})</li>"
    index_content += "</ul>"
    
    with open(os.path.join(CLOUDFLARE_PAGES_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_content)

def main():
    pages = []
    files_count = 0

    for page_id in NOTION_PAGE_IDS:
        try:
            title, created_time, last_edited_time = get_notion_page_info(page_id)
            sanitized_title = sanitize_title(title)
            
            cache_file = f"{CLOUDFLARE_PAGES_DIR}/cache/{page_id}.json"
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
                if cache['last_edited_time'] == last_edited_time:
                    logging.info(f"Page '{title}' hasn't changed. Skipping.")
                    pages.append(cache)
                    continue

            notion_content = get_notion_content(page_id)
            html_content = convert_to_html(notion_content)
            toc = generate_toc(notion_content)
            
            year_month = datetime.now().strftime("%Y/%m")
            page_path = f"{year_month}/{sanitized_title}/index.html"
            full_path = os.path.join(CLOUDFLARE_PAGES_DIR, page_path)
            
            page_info = {
                "title": title,
                "path": page_path,
                "created_time": created_time,
                "last_edited_time": last_edited_time
            }
            pages.append(page_info)

            save_html(toc, html_content, title, full_path, created_time, last_edited_time, pages)

            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump(page_info, f)

            files_count += 1
            logging.info(f"Page '{title}' processed successfully")
        except Exception as e:
            logging.error(f"Error processing page {page_id}: {e}")
    
    create_index_page(pages)
    logging.info(f"Index page created. Total files generated: {files_count + 1}")

if __name__ == "__main__":
    main()
