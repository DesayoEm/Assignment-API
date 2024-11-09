import json
from uuid import uuid4

def load_file():
    try:
        with open('data.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_file(users):
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(users, file, indent=4)

def create_user_id():
    return str(uuid4()).replace('-', '')[:5]
