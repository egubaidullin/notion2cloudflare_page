import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any

class FileManager:
    def __init__(self, base_dir: str = '.'):
        self.base_dir = Path(base_dir)
        self.build_dir = self.base_dir / 'build'
        self.assets_dir = self.base_dir / 'assets'
        self.ensure_build_directory()

    def ensure_build_directory(self):
        """Подготавливает build директорию"""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(parents=True)
        
        # Копируем assets
        build_assets = self.build_dir / 'assets'
        shutil.copytree(self.assets_dir, build_assets)
        logging.info(f"Build directory prepared at {self.build_dir}")

    def save_html(self, filename: str, content: str):
        """Сохраняет HTML файл"""
        output_path = self.build_dir / f"{filename}.html"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"Generated {output_path}")
        except IOError as e:
            logging.error(f"Error saving file {output_path}: {e}")
            raise