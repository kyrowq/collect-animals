import unicodedata


def normalize(text):
    """Minuscules + sans accents ('Épique' -> 'epique')."""
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


# weight = probabilité de tirage (en %)
RARITIES = {
    "commun":     {"name": "Commun",     "color": 0x9AA0A6, "stars": "⭐",         "icon": "⚪", "weight": 60},
    "rare":       {"name": "Rare",       "color": 0x3498DB, "stars": "⭐⭐",       "icon": "🔵", "weight": 25},
    "epique":     {"name": "Épique",     "color": 0x9B59B6, "stars": "⭐⭐⭐",     "icon": "🟣", "weight": 12},
    "legendaire": {"name": "Légendaire", "color": 0xF1C40F, "stars": "⭐⭐⭐⭐",   "icon": "🟡", "weight": 3},
}

# ordre d'affichage : du plus rare au plus commun
ORDER = ["legendaire", "epique", "rare", "commun"]


def get_rarity(rarity_name):
    return RARITIES.get(normalize(rarity_name), RARITIES["commun"])


def progress_bar(current, total, size=10):
    filled = round(size * current / total) if total else 0
    return "▰" * filled + "▱" * (size - filled)


def find_animal(query, animals):
    """Trouve un animal à partir d'un nom partiel, sans tenir compte des accents."""
    q = normalize(query)

    for animal in animals:
        if normalize(animal["name"]) == q:
            return animal

    for animal in animals:
        if q in normalize(animal["name"]):
            return animal

    return None

def get_image(animal):
    """Retourne (None, url) : l'image vient du champ "image" de animals.json."""
    url = animal.get("image")

    if url:
        return None, url

    return None, None