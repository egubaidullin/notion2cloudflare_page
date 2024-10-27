from typing import List, Dict, Any
from html import escape
from template_engine import TemplateEngine

class HTMLRenderer:
    def __init__(self, template_engine: TemplateEngine):
        self.template_engine = template_engine

    def get_text_content(self, rich_text: List[Dict[str, Any]]) -> str:
        """Извлекает текст из rich_text объекта Notion"""
        return ''.join([t.get('plain_text', '') for t in rich_text])

    def convert_to_html(self, blocks: List[Dict[str, Any]]) -> str:
        """Конвертирует блоки Notion в HTML"""
        html_content = []
        list_type = None

        for block in blocks:
            block_type = block.get('type')

            if block_type == 'paragraph':
                text = self.get_text_content(block['paragraph'].get('rich_text', []))
                html_content.append(
                    self.template_engine.render_block('paragraph', content=text)
                )

            elif block_type.startswith('heading_'):
                level = int(block_type.split('_')[-1])
                text = self.get_text_content(block[block_type].get('rich_text', []))
                heading_id = text.replace(" ", "-").lower()
                html_content.append(
                    self.template_engine.render_block('heading',
                        content=text,
                        level=level,
                        heading_id=heading_id
                    )
                )

            elif block_type == 'code':
                code = escape(self.get_text_content(block['code'].get('rich_text', [])))
                language = block['code'].get('language') or 'plaintext'
                html_content.append(
                    self.template_engine.render_block('code',
                        content=code,
                        language=language
                    )
                )

            elif block_type == 'image':
                image_data = block['image']
                if 'file' in image_data:
                    image_url = image_data['file']['url']
                    html_content.append(
                        self.template_engine.render_block('image',
                            url=image_url,
                            alt="Notion image"
                        )
                    )

            elif block_type == 'callout':
                icon = block['callout']['icon'].get('emoji', '')
                text = self.get_text_content(block['callout'].get('rich_text', []))
                html_content.append(
                    self.template_engine.render_block('callout',
                        icon=icon,
                        content=text
                    )
                )

            elif block_type in ['bulleted_list_item', 'numbered_list_item']:
                current_list = 'ul' if block_type == 'bulleted_list_item' else 'ol'
                text = self.get_text_content(block[block_type].get('rich_text', []))
                
                if list_type != current_list:
                    if list_type:
                        html_content.append(f"</{list_type}>")
                    html_content.append(f"<{current_list}>")
                    list_type = current_list
                
                html_content.append(
                    self.template_engine.render_block('list_item',
                        content=text
                    )
                )

        if list_type:
            html_content.append(f"</{list_type}>")

        return '\n'.join(html_content)

    def generate_toc(self, blocks: List[Dict[str, Any]]) -> str:
        """Генерирует оглавление"""
        toc_items = []
        
        for block in blocks:
            if block.get('type') == 'heading_1':
                text = self.get_text_content(block['heading_1'].get('rich_text', []))
                heading_id = text.replace(" ", "-").lower()
                toc_items.append(
                    self.template_engine.render_block('toc_item',
                        content=text,
                        heading_id=heading_id
                    )
                )

        return self.template_engine.render_block('toc',
            items=toc_items
        )
