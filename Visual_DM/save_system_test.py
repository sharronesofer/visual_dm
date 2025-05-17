import os
import json
import random
import string
import shutil

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SAVE_REPORT = os.path.join(PROJECT_ROOT, 'save_system_report.md')
SAVE_DIR = os.path.join(PROJECT_ROOT, 'test_saves')

TEST_STATES = [
    {'player': 'Alice', 'score': 100, 'level': 1},
    {'player': 'Bob', 'score': 250, 'level': 5, 'inventory': ['sword', 'shield']},
    {'player': 'Carol', 'score': 9999, 'level': 99, 'inventory': [str(i) for i in range(1000)]},
]

PREV_VERSION_SAVE = os.path.join(PROJECT_ROOT, 'prev_version_save.json')  # Simulate if available


def random_string(length=1024*1024):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def save_game(state, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(state, f)

def load_game(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def corrupt_file(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(random_string(1024))

def main():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    report = ['# Save System Report\n']
    # Test save/load for various states
    for i, state in enumerate(TEST_STATES):
        fname = os.path.join(SAVE_DIR, f'save_{i}.json')
        try:
            save_game(state, fname)
            loaded = load_game(fname)
            assert loaded == state
            report.append(f'- Save/load test passed for state {i}')
        except Exception as e:
            report.append(f'- Save/load test FAILED for state {i}: {e}')
    # Test persistence across restarts (simulate by reloading)
    try:
        for i in range(len(TEST_STATES)):
            fname = os.path.join(SAVE_DIR, f'save_{i}.json')
            loaded = load_game(fname)
            assert loaded == TEST_STATES[i]
        report.append('- Persistence test passed')
    except Exception as e:
        report.append(f'- Persistence test FAILED: {e}')
    # Test compatibility with previous version saves
    if os.path.exists(PREV_VERSION_SAVE):
        try:
            loaded = load_game(PREV_VERSION_SAVE)
            report.append('- Previous version save loaded successfully')
        except Exception as e:
            report.append(f'- Previous version save FAILED: {e}')
    else:
        report.append('- No previous version save to test')
    # Stress test with large save file
    try:
        big_state = {'data': random_string(10*1024*1024)}  # 10MB
        fname = os.path.join(SAVE_DIR, 'big_save.json')
        save_game(big_state, fname)
        loaded = load_game(fname)
        assert loaded['data'] == big_state['data']
        report.append('- Large save file test passed')
    except Exception as e:
        report.append(f'- Large save file test FAILED: {e}')
    # Corrupt save file test
    try:
        fname = os.path.join(SAVE_DIR, 'corrupt_save.json')
        save_game({'valid': True}, fname)
        corrupt_file(fname)
        try:
            load_game(fname)
            report.append('- Corrupt save file test FAILED: No error raised')
        except Exception:
            report.append('- Corrupt save file test passed (error raised as expected)')
    except Exception as e:
        report.append(f'- Corrupt save file test setup FAILED: {e}')
    # Cleanup
    shutil.rmtree(SAVE_DIR)
    with open(SAVE_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    print(f"Save system tests complete. See {SAVE_REPORT}.")

if __name__ == '__main__':
    main() 