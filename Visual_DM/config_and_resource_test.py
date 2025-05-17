import os
import json
import pygame
import gc
import tracemalloc

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_REPORT = os.path.join(PROJECT_ROOT, 'config_validation_report.md')
RESOURCE_REPORT = os.path.join(PROJECT_ROOT, 'resource_management_report.md')

CONFIG_EXTS = ['.json', '.ini', '.cfg']
RESOURCE_EXTS = ['.png', '.jpg', '.jpeg', '.bmp', '.ogg', '.wav', '.mp3', '.ttf', '.otf']

REQUIRED_CONFIG_KEYS = [
    'screen_width', 'screen_height', 'scaling', 'input', 'audio', 'visual'
]


def find_files_by_ext(root, exts):
    found = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if any(f.endswith(ext) for ext in exts):
                found.append(os.path.join(dirpath, f))
    return found

def validate_json_config(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        missing = [k for k in REQUIRED_CONFIG_KEYS if k not in data]
        return True, missing
    except Exception as e:
        return False, str(e)

def config_validation():
    report = ['# Configuration Validation Report\n']
    config_files = find_files_by_ext(PROJECT_ROOT, CONFIG_EXTS)
    for cfg in config_files:
        if cfg.endswith('.json'):
            valid, info = validate_json_config(cfg)
            if valid:
                if info:
                    report.append(f'- {cfg}: Missing keys: {info}')
                else:
                    report.append(f'- {cfg}: Valid')
            else:
                report.append(f'- {cfg}: Invalid JSON ({info})')
        else:
            report.append(f'- {cfg}: Skipped (non-JSON config)')
    with open(CONFIG_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))


def resource_management():
    report = ['# Resource Management Report\n']
    resource_files = find_files_by_ext(PROJECT_ROOT, RESOURCE_EXTS)
    pygame.init()
    tracemalloc.start()
    mem_before = tracemalloc.get_traced_memory()[0]
    loaded = []
    for res in resource_files:
        try:
            if res.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                img = pygame.image.load(res)
                loaded.append(img)
                report.append(f'- Loaded image: {res}')
            elif res.endswith(('.ogg', '.wav', '.mp3')):
                snd = pygame.mixer.Sound(res)
                loaded.append(snd)
                report.append(f'- Loaded sound: {res}')
            elif res.endswith(('.ttf', '.otf')):
                font = pygame.font.Font(res, 16)
                loaded.append(font)
                report.append(f'- Loaded font: {res}')
        except Exception as e:
            report.append(f'- Failed to load {res}: {e}')
    mem_after = tracemalloc.get_traced_memory()[0]
    report.append(f'\nMemory before loading: {mem_before} bytes')
    report.append(f'Memory after loading: {mem_after} bytes')
    # Unload resources
    del loaded
    gc.collect()
    mem_post_gc = tracemalloc.get_traced_memory()[0]
    report.append(f'Memory after GC: {mem_post_gc} bytes')
    tracemalloc.stop()
    pygame.quit()
    with open(RESOURCE_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

def main():
    config_validation()
    resource_management()
    print(f"Config and resource tests complete. See {CONFIG_REPORT} and {RESOURCE_REPORT}.")

if __name__ == '__main__':
    main() 