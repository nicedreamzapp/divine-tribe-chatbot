#!/usr/bin/env python3
"""Check which Python modules are actually being used"""

import os
import re
from pathlib import Path

def check_imports(file_path):
    """Check what a file imports"""
    imports = []
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Find all import statements
            import_pattern = r'(?:from|import)\s+([\w\.]+)'
            imports = re.findall(import_pattern, content)
    except:
        pass
    return imports

def analyze_project():
    """Analyze which modules are used"""
    project_dir = Path("/Users/matthewmacosko/Desktop/dataset for Tribe Chatbot")
    
    # Main chatbot files
    main_files = [
        "chatbot_modular.py",
        "chatbot_with_human.py"
    ]
    
    # All module files
    modules_dir = project_dir / "modules"
    module_files = list(modules_dir.glob("*.py"))
    
    print("📊 MODULE USAGE ANALYSIS")
    print("=" * 60)
    
    # Check what each main file uses
    for main_file in main_files:
        file_path = project_dir / main_file
        if file_path.exists():
            imports = check_imports(file_path)
            module_imports = [i for i in imports if 'modules.' in i]
            
            print(f"\n📁 {main_file} uses:")
            for imp in module_imports:
                module_name = imp.replace('modules.', '')
                print(f"  ✓ {module_name}")
    
    # Check which modules are NOT used
    all_modules = [f.stem for f in module_files]
    
    used_modules = set()
    for main_file in main_files:
        file_path = project_dir / main_file
        if file_path.exists():
            content = open(file_path).read()
            for module in all_modules:
                if module in content:
                    used_modules.add(module)
    
    unused_modules = set(all_modules) - used_modules
    
    print("\n🗑️ POTENTIALLY UNUSED MODULES:")
    for module in sorted(unused_modules):
        print(f"  • {module}.py")
    
    print("\n✅ ACTIVELY USED MODULES:")
    for module in sorted(used_modules):
        print(f"  • {module}.py")
    
    # Files to potentially remove
    print("\n🧹 SAFE TO REMOVE:")
    safe_to_remove = [
        "reorganize_complete.py",  # Already ran
        "reorganize_products.py",  # Duplicate
        "test_reorganization.py",  # Already tested
        "test_chatbot.py",  # Old test
        "shared_sessions.json"  # Temp file
    ]
    
    for file in safe_to_remove:
        file_path = project_dir / file
        if file_path.exists():
            print(f"  • {file}")

if __name__ == "__main__":
    analyze_project()
