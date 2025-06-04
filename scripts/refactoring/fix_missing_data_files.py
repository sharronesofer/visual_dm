import os
import json

def ensure_data_file(path, default_content=None):
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print(f'Created directory: {dir_name}')
    if not os.path.exists(path):
        with open(path, 'w') as f:
            if default_content is not None:
                json.dump(default_content, f)
            else:
                f.write('{}')
        print(f'Created data file: {path}')

if __name__ == '__main__':
    ensure_data_file('data/systems/equipment/items.json', default_content={})
    ensure_data_file('backend/rules_json/equipment.json', default_content={}) 