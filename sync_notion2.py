import os
import requests
import logging
from html import escape

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_PAGE_IDS = os.getenv('NOTION_PAGE_IDS').split(",")

# Добавляем логирование для проверки, установлен ли NOTION_PAGE_IDS
if not NOTION_PAGE_IDS:
    logging.error("Переменная окружения 'NOTION_PAGE_IDS' не установлена или пуста.")
    raise ValueError("Переменная 'NOTION_PAGE_IDS' требуется, но не установлена.")

# Проверка, установлен ли NOTION_API_TOKEN
if not NOTION_API_TOKEN:
    logging.error("Переменная окружения 'NOTION_API_TOKEN' не установлена.")
    raise ValueError("Переменная 'NOTION_API_TOKEN' требуется, но не установлена.")

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

            logging.info(f"Получено {len(data['results'])} блоков для страницы {page_id}. Всего блоков: {len(all_blocks)}")

        except requests.RequestException as e:
            logging.error(f"Ошибка при получении контента страницы Notion: {e}")
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
            text = get_text_content(block['paragraph']['rich_text'])
            html_content.append(f"<p>{text}</p>")
        elif block_type.startswith('heading_'):
            level = int(block_type[-1])
            text = get_text_content(block[block_type]['rich_text'])
            heading_id = text.replace(" ", "-").lower()
            html_content.append(f"<h{level} id='{heading_id}' class='text-{level}xl font-bold mb-4'>{text}</h{level}>")
        elif block_type == 'bulleted_list_item':
            if list_type != 'ul':
                if list_type:
                    html_content.append(f"</{'ol' if list_type == 'ol' else 'ul'}>")
                html_content.append("<ul>")
                list_type = 'ul'
            text = get_text_content(block['bulleted_list_item']['rich_text'])
            html_content.append(f"<li>{text}</li>")
        elif block_type == 'numbered_list_item':
            if list_type != 'ol':
                if list_type:
                    html_content.append(f"</{'ol' if list_type == 'ol' else 'ul'}>")
                html_content.append("<ol>")
                list_type = 'ol'
            text = get_text_content(block['numbered_list_item']['rich_text'])
            html_content.append(f"<li>{text}</li>")
        elif block_type == 'code':
            code = escape(get_text_content(block['code']['rich_text']))
            language = block['code']['language'] or 'plaintext'
            html_content.append(f"""
            <div class="code-block relative">
              <pre><code class="language-{language}">{code}</code></pre>
              <button class="copy-button" aria-label="Copy code">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy h-4 w-4">
                  <rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect>
                  <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path>
                </svg>
                <span class="copied-tooltip">Copied!</span>
              </button>
            </div>
            """)
        elif block_type == 'image':
            image_url = block['image']['file']['url']
            html_content.append(f"<img src='{image_url}' alt='Notion image'>")
        elif block_type == 'divider':
            html_content.append("<hr>")
        elif block_type == 'quote':
            text = get_text_content(block['quote']['rich_text'])
            html_content.append(f"<blockquote>{text}</blockquote>")
        elif block_type == 'callout':
            emoji = block['callout']['icon']['emoji'] if block['callout']['icon']['type'] == 'emoji' else ''
            text = get_text_content(block['callout']['rich_text'])
            html_content.append(f"<div class='callout'>{emoji} {text}</div>")
        
        # Обработка дочерних блоков, если есть
        if 'has_children' in block and block['has_children']:
            child_blocks = get_child_blocks(block['id'])
            html_content.extend(convert_to_html(child_blocks))

    # Закрытие открытых списков
    if list_type:
        html_content.append(f"</{'ol' if list_type == 'ol' else 'ul'}>")

    return ''.join(html_content)  # Объединяем список в одну строку

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

        logging.warning("Заголовок страницы не найден.")
        return "Ваш Заголовок Страницы из Notion"
    
    except requests.RequestException as e:
        logging.error(f"Ошибка при получении заголовка страницы: {e}")
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
    Генерирует HTML для навигации со ссылками на все страницы в строку, разделённые пробелами.
    :param pages_data: Список кортежей (заголовок, имя файла)
    :return: Строка HTML для навигации
    """
    nav_html = ""
    for i, (title, filename) in enumerate(pages_data):
        if i > 0:
            nav_html += " "  # Добавляем разделитель для всех, кроме первой ссылки
        nav_html += f"<a href='{filename}.html' class='hover:text-blue-500'>{title}</a>"
    return nav_html

def save_html(toc, html_content, title, filename, navigation):
    try:
        with open('template.html', 'r', encoding='utf-8') as f:
            template = f.read()

        full_html = template.replace('{{ title }}', title) \
                            .replace('{{ toc }}', toc) \
                            .replace('{{ content }}', html_content) \
                            .replace('{{ pages_navigation }}', navigation)

        with open(f'{filename}.html', 'w', encoding='utf-8') as f:
            f.write(full_html)
        logging.info(f"HTML сохранён в {filename}.html")
    except IOError as e:
        logging.error(f"Ошибка при сохранении HTML: {e}")
        raise

def main():
    try:
        logging.info("Начало синхронизации страниц Notion...")

        pages_data = []
        for idx, page_id in enumerate(NOTION_PAGE_IDS):
            logging.info(f"Обработка страницы {page_id}")
            notion_content = get_notion_content(page_id)
            html_content = convert_to_html(notion_content)
            title = get_title(page_id)
            toc = generate_toc(notion_content)

            filename = f'page_{idx + 1}'
            if idx == 0:
                filename = 'index'  # Первый файл будет index.html
            pages_data.append((title, filename))  # Сохраняем заголовок и имя файла для навигации
            save_html(toc, html_content, title, filename, '')  # Временно оставляем навигацию пустой

        # После обработки всех страниц, генерируем навигацию и сохраняем каждую страницу заново
        navigation = generate_navigation(pages_data)

        for title, filename in pages_data:
            # Повторное сохранение каждой страницы с навигацией
            notion_content = get_notion_content(NOTION_PAGE_IDS[pages_data.index((title, filename))])
            html_content = convert_to_html(notion_content)
            toc = generate_toc(notion_content)
            save_html(toc, html_content, title, filename, navigation)

        logging.info("Синхронизация завершена успешно")
    except Exception as e:
        logging.error(f"Синхронизация не удалась: {e}")
        raise

if __name__ == "__main__":
    main()
