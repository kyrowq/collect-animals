import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ANIMAL_FILE = os.path.join(BASE_DIR, "data", "animals.json")
PLAYER_FILE = os.path.join(BASE_DIR, "data", "players.json")

def load_data(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_data(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def get_animals():
    return load_data(ANIMAL_FILE)

def get_players():
    return load_data(PLAYER_FILE)

def save_players(players):
    save_data(PLAYER_FILE, players)