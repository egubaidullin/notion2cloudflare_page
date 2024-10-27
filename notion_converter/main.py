import os
import logging
from typing import List, Tuple
from notion_client import NotionClient
from template_engine import TemplateEngine
from html_renderer import HTMLRenderer
from file_manager import FileManager

def generate_navigation(pages_data: List[Tuple[str, str]]) -> str:
    """Генерирует навигацию по страницам"""
    nav_items = []
    for title, filename in pages_data:
        nav_items.append(f'<a href="{filename}.html">{title}</a>')
    return ' '.join(nav_items)

def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
    )

    # Загрузка переменных окружения
    notion_token = os.getenv('NOTION_API_TOKEN')
    page_ids = os.getenv('NOTION_PAGE_IDS', '').split(',')

    if not notion_token or not page_ids:
        raise ValueError("Required environment variables are not set")

    try:
        # Инициализация компонентов
        notion_client = NotionClient(notion_token)
        template_engine = TemplateEngine()
        html_renderer = HTMLRenderer(template_engine)
        file_manager = FileManager()

        # Обработка страниц
        pages_data = []
        for idx, page_id in enumerate(page_ids):
            logging.info(f"Processing page {page_id}")
            
            # Получение данных страницы
            notion_content = notion_client.get_page_content(page_id)
            html_content = html_renderer.convert_to_html(notion_content)
            title = notion_client.get_page_title(page_id)
            toc = html_renderer.generate_toc(notion_content)
            
            # Генерация имени файла
            filename = 'index' if idx == 0 else f'page_{idx + 1}'
            pages_data.append((title, filename))
            
            # Сохранение страницы
            file_manager.save_html(
                filename,
                template_engine.render_page('template.html',
                    title=title,
                    content=html_content,
                    toc=toc,
                    navigation=''
                )
            )

        # Генерация навигации и обновление страниц
        navigation = generate_navigation(pages_data)
        for title, filename in pages_data:
            page_id = page_ids[pages_data.index((title, filename))]
            notion_content = notion_client.get_page_content(page_id)
            html_content = html_renderer.convert_to_html(notion_content)
            toc = html_renderer.generate_toc(notion_content)
            
            file_manager.save_html(
                filename,
                template_engine.render_page('template.html',
                    title=title,
                    content=html_content,
                    toc=toc,
                    navigation=navigation
                )
            )

        logging.info("Sync completed successfully")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

if __name__ == '__main__':
    main()
