import json
import os

def create_standalone_html(directory):
    html_path = os.path.join(directory, "puzzle.html")
    json_path = os.path.join(directory, "assets_data.json")
    
    with open(json_path, 'r') as f:
        assets_json = f.read()
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Use a simpler string replacement to avoid regex escape issues
    placeholder = "const ASSETS_DATA = {};"
    if placeholder in html_content:
        new_content = html_content.replace(placeholder, f"const ASSETS_DATA = {assets_json};")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated HTML with assets: {html_path}")
    else:
        # Fallback if the script was already injected once
        import re
        # Find the start and end of the object to replace it manually
        start_tag = "const ASSETS_DATA = {"
        end_tag = "};"
        start_idx = html_content.find(start_tag)
        if start_idx != -1:
            end_idx = html_content.find(end_tag, start_idx)
            if end_idx != -1:
                new_content = html_content[:start_idx] + f"const ASSETS_DATA = {assets_json}" + html_content[end_idx:]
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated HTML (manual replacement): {html_path}")
            else:
                print("Could not find end of ASSETS_DATA object.")
        else:
            print("Could not find ASSETS_DATA placeholder.")

if __name__ == "__main__":
    create_standalone_html(r"C:\Users\藤本　羽奏\puzzle")
