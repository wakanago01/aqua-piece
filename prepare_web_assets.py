import base64
import os
import json

def generate_base64_assets(directory):
    assets = {}
    
    for root, dirs, files in os.walk(directory):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg']:
                filepath = os.path.join(root, filename)
                with open(filepath, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    mime = "image/png" if ext == ".png" else "image/jpeg"
                    name = os.path.splitext(filename)[0]
                    if name not in assets or ext == ".png":
                        assets[name] = f"data:{mime};base64,{encoded_string}"
            
            elif ext == '.mp3':
                filepath = os.path.join(root, filename)
                with open(filepath, "rb") as audio_file:
                    encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
                    assets[os.path.splitext(filename)[0]] = f"data:audio/mp3;base64,{encoded_string}"
    
    with open(os.path.join(directory, "assets_data.json"), "w", encoding='utf-8') as f:
        json.dump(assets, f, ensure_ascii=False)
    print("Generated assets_data.json with Base64 strings from all subdirectories.")

if __name__ == "__main__":
    target_dir = r"C:\Users\藤本　羽奏\puzzle"
    generate_base64_assets(target_dir)
