import base64
import os
import json

def generate_base64_assets(directory):
    assets = {}
    # Image assets
    image_files = [f for f in os.listdir(directory) if f.endswith('.png') or f.endswith('.jpg')]
    for filename in image_files:
        filepath = os.path.join(directory, filename)
        with open(filepath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            ext = os.path.splitext(filename)[1].lower()
            mime = "image/png" if ext == ".png" else "image/jpeg"
            # Prioritize PNG by checking if it already exists in the dict
            name = os.path.splitext(filename)[0]
            if name not in assets or ext == ".png":
                assets[name] = f"data:{mime};base64,{encoded_string}"
    
    # Audio assets
    audio_files = [f for f in os.listdir(directory) if f.endswith('.mp3')]
    for filename in audio_files:
        filepath = os.path.join(directory, filename)
        with open(filepath, "rb") as audio_file:
            encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
            assets[os.path.splitext(filename)[0]] = f"data:audio/mp3;base64,{encoded_string}"
    
    with open(os.path.join(directory, "assets_data.json"), "w") as f:
        json.dump(assets, f)
    print("Generated assets_data.json with Base64 strings for images and audio.")

if __name__ == "__main__":
    target_dir = r"C:\Users\藤本　羽奏\puzzle"
    generate_base64_assets(target_dir)
