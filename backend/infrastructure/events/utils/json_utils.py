import os
import json
import logging

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
RULES_PATH = os.path.join(PROJECT_ROOT, "data/builders/content")

# def load_json(*args, **kwargs): # REMOVED STUB
#     return {} # REMOVED STUB

def save_json(data, filename_or_path, use_rules_path=True):
    """
    Saves data to a JSON file.
    If use_rules_path is True, saves to data/builders/content/ folder.
    Otherwise, uses the given full path.
    """
    if use_rules_path:
        path = os.path.join(RULES_PATH, filename_or_path)
    else:
        path = filename_or_path

    print(f"💾 Saving to path: {path}")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON to {path}: {e}")
        return False
