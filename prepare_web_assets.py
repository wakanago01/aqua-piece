import base64
import os
import json

def generate_base64_assets(directory):
    assets = {}
    files = [f for f in os.listdir(directory) if f.endswith('.png')]
    for filename in files:
        filepath = os.path.join(directory, filename)
        with open(filepath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            assets[os.path.splitext(filename)[0]] = f"data:image/png;base64,{encoded_string}"
    
    with open(os.path.join(directory, "assets_data.json"), "w") as f:
        json.dump(assets, f)
    print("Generated assets_data.json with Base64 strings.")

if __name__ == "__main__":
    target_dir = r"C:\Users\藤本　羽奏\puzzle"
    generate_base64_assets(target_dir)
