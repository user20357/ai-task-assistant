#!/usr/bin/env python3
"""
Script to fix f-strings in ai_chat.py that are causing syntax errors
"""

import re

def fix_fstrings():
    with open('src/core/ai_chat.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix logger.error f-strings
    content = re.sub(r'logger\.error\(f"([^"]*): \{([^}]+)\}"\)', r'logger.error("\1: " + str(\2))', content)
    
    # Fix other common f-string patterns that might cause issues
    content = re.sub(r'f"([^"]*)\{([^}]+)\.get\(\'([^\']+)\', \'([^\']*)\'\)\}([^"]*)"', r'"\1" + str(\2.get("\3", "\4")) + "\5"', content)
    
    # Fix self.error_occurred.emit f-strings
    content = re.sub(r'self\.error_occurred\.emit\(f"([^"]*): \{([^}]+)\}"\)', r'self.error_occurred.emit("\1: " + str(\2))', content)
    
    with open('src/core/ai_chat.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed f-strings in ai_chat.py")

if __name__ == "__main__":
    fix_fstrings()