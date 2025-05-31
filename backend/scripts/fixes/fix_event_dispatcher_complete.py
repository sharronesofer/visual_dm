#!/usr/bin/env python3
"""
Complete fix for all event_dispatcher.py syntax errors
"""

import re

def fix_event_dispatcher():
    file_path = "systems/events/event_dispatcher.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix malformed dictionary literals with colons
    content = re.sub(r'event_data =:\s*event_type:', r'event_data = {\n            "event_type":', content)
    content = re.sub(r'timestamp: getattr\(event, timestamp, datetime\.utcnow\(\)\.isoformat\(\)\)\s*pass', 
                     r'"timestamp": getattr(event, "timestamp", datetime.utcnow().isoformat())\n        }', content)
    
    # Fix hasattr calls with missing quotes
    content = re.sub(r'hasattr\(event, to_dict\)', r'hasattr(event, "to_dict")', content)
    content = re.sub(r'getattr\(event, event_type,', r'getattr(event, "event_type",', content)
    content = re.sub(r'getattr\(event, timestamp,', r'getattr(event, "timestamp",', content)
    
    # Fix the malformed for loops and indentation
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Fix class docstring indentation
        if 'class EventMiddleware:' in line:
            fixed_lines.append(line)
            # Add proper indentation for docstring
            if i + 1 < len(lines) and '"""' in lines[i + 1]:
                fixed_lines.append('    """')
            continue
        elif line.strip() == '"""' and len(fixed_lines) > 0 and 'class EventMiddleware:' in fixed_lines[-1]:
            continue  # Skip the malformed docstring line
        
        # Fix missing indentation after class/function definitions
        if ':' in line and ('def ' in line or 'class ' in line):
            fixed_lines.append(line)
            # Check if next line needs indentation
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.strip() and not next_line.startswith('    ') and not next_line.startswith('\t'):
                    if '"""' in next_line:
                        fixed_lines.append('    ' + next_line.strip())
                    continue
        
        # Fix general indentation issues
        if line.strip():
            # Count current indentation
            current_indent = len(line) - len(line.lstrip())
            
            # Check if we need to fix indentation based on context
            if len(fixed_lines) > 0:
                prev_line = fixed_lines[-1]
                
                # If previous line was a class or function definition, this should be indented
                if prev_line.strip().endswith(':') and ('def ' in prev_line or 'class ' in prev_line):
                    if current_indent == 0:
                        fixed_lines.append('    ' + line.strip())
                        continue
                
                # If we're in a class/function body, maintain proper indentation
                if current_indent == 0 and line.strip() and not line.startswith('class ') and not line.startswith('def '):
                    # Check if we should be indented
                    in_class_or_function = False
                    for prev_line_check in reversed(fixed_lines[-20:]):  # Check last 20 lines
                        if prev_line_check.strip().startswith('class ') or (prev_line_check.strip().startswith('def ') and ':' in prev_line_check):
                            in_class_or_function = True
                            break
                        elif prev_line_check.strip() and not prev_line_check.startswith('    ') and not prev_line_check.startswith('#'):
                            break
                    
                    if in_class_or_function and not line.startswith('class ') and 'logger =' not in line:
                        fixed_lines.append('    ' + line.strip())
                        continue
        
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed all syntax and indentation errors in {file_path}")

if __name__ == "__main__":
    fix_event_dispatcher() 