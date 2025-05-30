import os
import re

def fix_singleton_instantiations(root_dir, class_name, get_instance_call):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                path = os.path.join(dirpath, filename)
                with open(path, 'r') as f:
                    code = f.read()
                # Replace direct instantiation with get_instance()
                new_code = re.sub(
                    rf'(\W){class_name}\s*\(\s*\)',
                    rf'\1{get_instance_call}()',
                    code
                )
                if new_code != code:
                    print(f'Fixed singleton in {path}')
                    with open(path, 'w') as f:
                        f.write(new_code)

if __name__ == '__main__':
    fix_singleton_instantiations('backend/', 'WorldStateManager', 'WorldStateManager.get_instance') 