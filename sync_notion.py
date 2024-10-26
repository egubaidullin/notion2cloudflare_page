import os
import requests
import logging
from html import escape

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize environment variables
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_PAGE_IDS = os.getenv('NOTION_PAGE_IDS')

if not NOTION_PAGE_IDS:
    logging.error("Environment variable 'NOTION_PAGE_IDS' is not set or is None.")
    raise ValueError("The 'NOTION_PAGE_IDS' environment variable is required but is not set.")
NOTION_PAGE_IDS = NOTION_PAGE_IDS.split(",")

if not NOTION_API_TOKEN:
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

            all_blocks.extend(data.get('results', []))
            has_more = data.get('has_more', False)
            start_cursor = data.get('next_cursor')

            logging.info(f"Fetched {len(data.get('results', []))} blocks for page {page_id}. Total blocks: {len(all_blocks)}")

        except requests.RequestException as e:
            logging.error(f"Error fetching Notion page content: {e}")
            raise

    return all_blocks

def get_text_content(rich_text):
    return ''.join([t.get('plain_text', '') for t in rich_text])

def get_text_content(rich_text):
    return ''.join([part['text']['content'] for part in rich_text])

def get_child_blocks(block_id):
    # Ваша реализация получения дочерних блоков
    pass

def convert_to_html(blocks):
    html_content = []
    list_type = None

    for block in blocks:
        block_type = block.get('type')

        if block_type == 'paragraph':
            text = get_text_content(block['paragraph'].get('rich_text', []))
            html_content.append(f"<p>{text}</p>")

        elif block_type.startswith('heading_'):
            level = int(block_type.split('_')[-1])
            text = get_text_content(block[block_type].get('rich_text', []))
            heading_id = text.replace(" ", "-").lower()
            html_content.append(f"<hr class='major' />")
            html_content.append(f"<h{level} id='{heading_id}' class='heading-level-{level}'>{text}</h{level}>")
            html_content.append(f"<hr class='major' />")

        elif block_type in ['bulleted_list_item', 'numbered_list_item']:
            current_list = 'ul' if block_type == 'bulleted_list_item' else 'ol'
            if list_type != current_list:
                if list_type:
                    html_content.append(f"</{list_type}>")
                html_content.append(f"<{current_list}>")
                list_type = current_list
            text = get_text_content(block[block_type].get('rich_text', []))
            html_content.append(f"<li>{text}</li>")

        elif block_type == 'code':
            code = escape(get_text_content(block['code'].get('rich_text', [])))
            language = block['code'].get('language') or 'plaintext'
            html_content.append(f"""
            <div class="code-block">
              <pre><code class="language-{language}">{code}</code></pre>
              <button class="copy-button icon fa-clipboard" onclick="copyToClipboard(this)">
              </button>
            </div>
            """)

        elif block_type == 'image':
            if 'file' in block['image']:
                image_url = block['image']['file']['url']
                html_content.append(f"<img src='{image_url}' alt='Notion image' class='image-block'>")
            else:
                logging.warning(f"Image block does not contain a 'file' key: {block['image']}")

        elif block_type == 'divider':
            html_content.append("<hr>")

        elif block_type == 'quote':
            text = get_text_content(block['quote'].get('rich_text', []))
            html_content.append(f"<blockquote>{text}</blockquote>")

        elif block_type == 'callout':
            icon = block['callout']['icon'].get('emoji', '') if block['callout']['icon'].get('type') == 'emoji' else ''
            text = get_text_content(block['callout'].get('rich_text', []))
            html_content.append(f"<div class='callout'>{icon} {text}</div>")

        # Обработка дочерних блоков
        if block.get('has_children'):
            child_blocks = get_child_blocks(block['id'])
            html_content.extend(convert_to_html(child_blocks))

    if list_type:
        html_content.append(f"</{list_type}>")

    return ''.join(html_content)


def get_child_blocks(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('results', [])
    except requests.RequestException as e:
        logging.error(f"Error fetching child blocks: {e}")
        return []

def get_title(page_id):
    try:
        url = f"https://api.notion.com/v1/pages/{page_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        page_data = response.json()

        title_property = page_data.get("properties", {}).get("title", {}).get("title", [])
        if title_property:
            return title_property[0].get("text", {}).get("content", "Untitled")

        logging.warning("Page title not found.")
        return "Untitled"

    except requests.RequestException as e:
        logging.error(f"Error fetching page title: {e}")
        return "Untitled"
    
def generate_toc(blocks):
    toc = []

    for block in blocks:
        if block.get('type') == 'heading_1':
            text = get_text_content(block['heading_1'].get('rich_text', []))
            heading_id = text.replace(" ", "-").lower()
            toc_item = f"<li><a href='#{heading_id}'>{text}</a></li>"
            toc.append(toc_item)

    # Wrap in the main <ul> list
    return "<ul>" + ''.join(toc) + "</ul>"


def get_text_content(rich_text):
    # Function to extract text from rich_text
    return ' '.join([item['text']['content'] for item in rich_text])


def generate_navigation(pages_data):
    nav_html = ""
    for i, (title, filename) in enumerate(pages_data):
        if i > 0:
            nav_html += " "
        nav_html += f"<a href='{filename}.html' class='logo'><strong>{title}</strong></a>"
    return nav_html

def load_template(template_name='template.html'):
    try:
        with open(template_name, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError as e:
        logging.error(f"Error loading template {template_name}: {e}")
        raise

def save_html(toc, html_content, title, filename, navigation, template='template.html'):
    try:
        full_html = template.replace('{{ title }}', escape(title)) \
                            .replace('{{ toc }}', toc) \
                            .replace('{{ content }}', html_content) \
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

        template = load_template()
        pages_data = []
        for idx, page_id in enumerate(NOTION_PAGE_IDS):
            logging.info(f"Processing page {page_id}")
            notion_content = get_notion_content(page_id)
            html_content = convert_to_html(notion_content)
            title = get_title(page_id)
            toc = generate_toc(notion_content)

            filename = 'index' if idx == 0 else f'page_{idx + 1}'
            pages_data.append((title, filename))
            save_html(toc, html_content, title, filename, '', template)

        navigation = generate_navigation(pages_data)

        for title, filename in pages_data:
            notion_content = get_notion_content(NOTION_PAGE_IDS[pages_data.index((title, filename))])
            html_content = convert_to_html(notion_content)
            toc = generate_toc(notion_content)
            save_html(toc, html_content, title, filename, navigation, template)

        logging.info("Sync completed successfully")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

if __name__ == '__main__':
    main()
