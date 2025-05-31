#!/usr/bin/env python3
"""
Fix syntax errors in event_dispatcher.py
"""

import re

def fix_event_dispatcher():
    file_path = "systems/events/event_dispatcher.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix quoted parameter names
    content = re.sub(r'def ([a-zA-Z_][a-zA-Z0-9_]*)\(self, "([^"]+)"', r'def \1(self, \2', content)
    content = re.sub(r', "([^"]+)"', r', \1', content)
    
    # Fix quoted docstring parameters 
    content = re.sub(r'"([a-zA-Z_][a-zA-Z0-9_]+)": ', r'\1: ', content)
    
    # Fix malformed lambda expressions
    content = re.sub(r'lambda "([^"]+)":', r'lambda \1:', content)
    
    # Fix quoted string literals that should be strings
    content = re.sub(r'"pre_dispatch"', r'pre_dispatch', content)
    content = re.sub(r'"post_dispatch"', r'post_dispatch', content)
    content = re.sub(r'"event"', r'event', content)
    
    # Fix incorrect docstring quotes
    content = re.sub(r'""""', r'"""', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed syntax errors in {file_path}")

if __name__ == "__main__":
    fix_event_dispatcher() 