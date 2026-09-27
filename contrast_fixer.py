import os
import glob
import re

def fix_contrast(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. Simple strings where bg-black and text-black or text-slate-900 are right next to each other
    content = content.replace("bg-black text-black border border-black", "bg-black text-white border border-black")
    content = content.replace("bg-black border-black text-black", "bg-black border-black text-white")
    content = content.replace("bg-black hover:bg-black border border-black text-xs font-semibold text-black", "bg-black hover:bg-slate-800 border border-black text-xs font-semibold text-white")

    # 2. Find className="..." strings and apply contrast logic
    def replace_class_string(match):
        class_str = match.group(1)
        if 'bg-black' in class_str and not 'bg-black/10' in class_str:
            # If the background is black, the text shouldn't be black or slate-900/800
            if 'text-black' in class_str:
                class_str = class_str.replace('text-black', 'text-white')
            if 'text-slate-900' in class_str:
                class_str = class_str.replace('text-slate-900', 'text-white')
            if 'text-slate-800' in class_str:
                class_str = class_str.replace('text-slate-800', 'text-white')
                
        return f'className="{class_str}"'

    # Same for className={`...`}
    def replace_class_template(match):
        class_str = match.group(1)
        if 'bg-black' in class_str and not 'bg-black/10' in class_str:
            if 'text-black' in class_str:
                class_str = class_str.replace('text-black', 'text-white')
            if 'text-slate-900' in class_str:
                class_str = class_str.replace('text-slate-900', 'text-white')
            if 'text-slate-800' in class_str:
                class_str = class_str.replace('text-slate-800', 'text-white')
                
        return f'className={{`{class_str}`}}'
        
    content = re.sub(r'className="([^"]+)"', replace_class_string, content)
    content = re.sub(r'className=\{`([^`]+)`\}', replace_class_template, content)
    
    # 3. Direct replacement for ternary strings like `... ? 'bg-black text-black' : ...`
    def replace_ternary(match):
        cond = match.group(1)
        true_case = match.group(2)
        false_case = match.group(3)
        
        if 'bg-black' in true_case and not 'bg-black/10' in true_case:
            true_case = true_case.replace('text-black', 'text-white').replace('text-slate-900', 'text-white')
        if 'bg-black' in false_case and not 'bg-black/10' in false_case:
            false_case = false_case.replace('text-black', 'text-white').replace('text-slate-900', 'text-white')
            
        return f"{cond} ? '{true_case}' : '{false_case}'"
        
    content = re.sub(r"([^?]+)\s*\?\s*'([^']+)'\s*:\s*'([^']+)'", replace_ternary, content)
    
    # A few specific remaining issues
    content = content.replace("bg-black hover:from-black hover:to-black", "bg-black hover:bg-slate-800")
    
    with open(filepath, 'w') as f:
        f.write(content)

src_dir = './frontend/src'
files = glob.glob(os.path.join(src_dir, '**/*.jsx'), recursive=True)

for file in files:
    fix_contrast(file)
    print(f"Fixed contrast in {file}")
