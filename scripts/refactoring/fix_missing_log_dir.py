import os

def ensure_log_dir_and_file(log_dir='logs', log_file='system.log'):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f'Created directory: {log_dir}')
    log_path = os.path.join(log_dir, log_file)
    if not os.path.exists(log_path):
        with open(log_path, 'w') as f:
            f.write('')
        print(f'Created log file: {log_path}')

if __name__ == '__main__':
    ensure_log_dir_and_file() 