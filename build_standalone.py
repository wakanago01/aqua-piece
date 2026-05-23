import json
import os

def create_standalone_html(directory):
    html_path = os.path.join(directory, "puzzle.html")
    json_path = os.path.join(directory, "assets_data.json")
    
    with open(json_path, 'r') as f:
        assets_json = f.read()
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Use robust searching for the constant declaration
    placeholder = "const ASSETS_DATA = {}; // ASSETS_DATA_PLACEHOLDER"
    if placeholder in html_content:
        new_content = html_content.replace(placeholder, f"const ASSETS_DATA = {assets_json};")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated HTML with assets: {html_path}")
    else:
        # Fallback to standard declaration if placeholder missing
        start_tag = "const ASSETS_DATA = {"
        end_tag = "};"
...

if __name__ == "__main__":
    create_standalone_html(r"C:\Users\藤本　羽奏\puzzle")
