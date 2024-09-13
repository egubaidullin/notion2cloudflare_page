import requests
import os
from datetime import datetime

# Токен и ID базы данных Notion
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Функция для получения данных с Notion
def get_notion_data():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching data from Notion: {response.status_code}, {response.text}")

# Генерация контента для Cloudflare Pages
def generate_content(data):
    page_content = "# Notion Page Data\n\n"
    for item in data["results"]:
        title = item["properties"]["Name"]["title"][0]["text"]["content"]
        page_content += f"## {title}\n\n"
        page_content += f"- Created: {item['created_time']}\n"
        page_content += f"- Last Edited: {item['last_edited_time']}\n\n"
    return page_content

# Сохранение контента в Markdown файл
def save_content(content):
    with open("index.md", "w") as file:
        file.write(content)

def main():
    data = get_notion_data()
    content = generate_content(data)
    save_content(content)
    print("Content updated successfully!")

if __name__ == "__main__":
    main()
