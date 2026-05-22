import os
from PIL import Image

def convert_jpg_to_transparent_png(directory):
    files = [f for f in os.listdir(directory) if f.endswith('.jpg')]
    print(f"Found {len(files)} JPG files.")

    for filename in files:
        filepath = os.path.join(directory, filename)
        with Image.open(filepath) as img:
            img = img.convert("RGBA")
            datas = img.getdata()

            new_data = []
            # Assuming the background is roughly white (thresholding for better results)
            threshold = 240
            for item in datas:
                if item[0] > threshold and item[1] > threshold and item[2] > threshold:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)

            img.putdata(new_data)
            
            # Trim the image to the actual content
            bbox = img.getbbox()
            if bbox:
                img = img.crop(bbox)
            
            # Save as PNG
            new_filename = os.path.splitext(filename)[0] + ".png"
            img.save(os.path.join(directory, new_filename), "PNG")
            print(f"Converted {filename} to {new_filename} and trimmed.")

if __name__ == "__main__":
    target_dir = r"C:\Users\藤本　羽奏\puzzle"
    convert_jpg_to_transparent_png(target_dir)
