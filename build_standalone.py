import json
import os

def create_standalone_html(directory):
    html_path = os.path.join(directory, "puzzle.html")
    json_path = os.path.join(directory, "assets_data.json")
    
    with open(json_path, 'r') as f:
        assets_json = f.read()
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Replace the ASSETS_DATA object
    import re
    html_content = re.sub(r'const ASSETS_DATA = \{.*?\};', f'const ASSETS_DATA = {assets_json};', html_content, flags=re.DOTALL)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Updated HTML with assets: {html_path}")

if __name__ == "__main__":
    create_standalone_html(r"C:\Users\藤本　羽奏\puzzle")
