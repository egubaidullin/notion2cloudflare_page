from jinja2 import Environment, FileSystemLoader
import yaml
from pathlib import Path

class TemplateEngine:
    def __init__(self, templates_dir: str = 'templates', config_dir: str = 'config'):
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.load_config(config_dir)

    def load_config(self, config_dir: str):
        config_path = Path(config_dir) / 'styles.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def render_block(self, block_type: str, **kwargs) -> str:
        """Рендерит HTML для конкретного типа блока"""
        template = self.env.get_template(f'blocks/{block_type}.html')
        return template.render(
            classes=self.config['classes'],
            **kwargs
        )

    def render_page(self, template_name: str, **kwargs) -> str:
        """Рендерит целую страницу"""
        template = self.env.get_template(template_name)
        return template.render(**kwargs)