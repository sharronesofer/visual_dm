import requests
import os

terrain_to_emoji = {
    "grassland": "🌾",
    "forest": "🌲",
    "riverlands": "🌊",
    "hills": "🏞️",
    "wetlands": "🐸",
    "desert": "🏜️",
    "tundra": "🧊",
    "mountains": "🏔️",
    "savanna": "🐘",
    "jungle": "🐍",
    "coastal": "🏖️",
    "volcano": "🌋",
    "cursed_lands": "☠️",
    "toxic_swamp": "☣️",
    "necrotic_fields": "💀",
    "haunted_woods": "👻",
    "frozen_wastes": "❄️",
    "scorched_plains": "🔥",
    "shattered_mountains": "🪨",
    "wasteland": "🏚️",
    "ruins": "🏚️",
    "arcane_storm": "🌪️",
    "celestial_plateau": "✨",
    "void_rift": "🕳️",
    "floating_isles": "🛫",
    "crystal_forest": "💎",
    "grave_valley": "⚰️",
    "fungal_jungle": "🍄",
    "sunken_city": "🧜",
    "clockwork_canyon": "⚙️",
    "obsidian_sea": "🖤",
}

output_folder = "emoji_tiles"
os.makedirs(output_folder, exist_ok=True)

def emoji_to_codepoint(emoji):
    return "-".join(f"{ord(c):x}" for c in emoji if not (0xFE00 <= ord(c) <= 0xFE0F))

for terrain, emoji in terrain_to_emoji.items():
    codepoint = emoji_to_codepoint(emoji)
    url = f"https://twemoji.maxcdn.com/v/latest/72x72/{codepoint}.png"
    save_path = os.path.join(output_folder, f"{terrain}.png")
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print(f"✅ Downloaded {terrain}.png")
        else:
            print(f"❌ Failed {terrain} ({r.status_code})")
    except Exception as e:
        print(f"❌ Error {terrain}: {e}")
