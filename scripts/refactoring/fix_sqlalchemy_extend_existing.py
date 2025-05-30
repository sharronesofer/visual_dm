import os
import re

def fix_sqlalchemy_extend_existing(root_dir):
    table_pattern = re.compile(r'(Table\s*\(\s*\"[\w_]+\"\s*,)')
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                path = os.path.join(dirpath, filename)
                with open(path, 'r') as f:
                    code = f.read()
                # Add extend_existing=True if not present
                def replacer(match):
                    if 'extend_existing=True' not in code[match.start():match.start()+200]:
                        return match.group(1) + ' extend_existing=True,'
                    return match.group(0)
                new_code = table_pattern.sub(replacer, code)
                if new_code != code:
                    print(f'Fixed SQLAlchemy Table in {path}')
                    with open(path, 'w') as f:
                        f.write(new_code)

if __name__ == '__main__':
    fix_sqlalchemy_extend_existing('backend/') 