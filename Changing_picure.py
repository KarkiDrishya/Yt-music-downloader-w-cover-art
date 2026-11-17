import os
import re
import io
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image

def clean_filename(filename):
    name, ext = os.path.splitext(filename)
    if ext.lower() != '.mp3':
        return filename
    
    # Remove text inside parentheses () and square brackets []
    cleaned = re.sub(r'\s*[\(\[].*?[\)\]]', '', name)
    cleaned = cleaned.strip()
    
    return cleaned + ext

def crop_album_art(filepath):
    try:
        audio = MP3(filepath, ID3=ID3)
        if audio.tags is None:
            return

        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                img = Image.open(io.BytesIO(tag.data))
                width, height = img.size
                
                if width == height:
                    continue
                
                if width > height:
                    new_size = height
                    left = (width - new_size) // 2
                    right = left + new_size
                    img_cropped = img.crop((left, 0, right, height))
                else:
                    new_size = width
                    top = (height - new_size) // 2
                    bottom = top + new_size
                    img_cropped = img.crop((0, top, width, bottom))
                
                output = io.BytesIO()
                img_format = img.format if img.format else 'JPEG'
                img_cropped.save(output, format=img_format)
                
                tag.data = output.getvalue()
                audio.save()
                print(f"Cropped cover art for: {os.path.basename(filepath)}")
                break
    except Exception as e:
        print(f"Error processing art for {os.path.basename(filepath)}: {e}")

def main():
    # Target the "Hindi songs" folder relative to this script
    folder = "Hindi songs"
    
    if not os.path.exists(folder):
        print(f"Error: The folder '{folder}' was not found.")
        return
    
    for filename in os.listdir(folder):
        if not filename.endswith('.mp3'):
            continue
            
        old_path = os.path.join(folder, filename)
        
        # 1. Process and crop album art
        crop_album_art(old_path)
        
        # 2. Rename file
        new_filename = clean_filename(filename)
        if new_filename != filename:
            new_path = os.path.join(folder, new_filename)
            counter = 1
            base, ext = os.path.splitext(new_filename)
            while os.path.exists(new_path) and new_path != old_path:
                new_filename = f"{base} ({counter}){ext}"
                new_path = os.path.join(folder, new_filename)
                counter += 1
                
            os.rename(old_path, new_path)
            print(f"Renamed: '{filename}' -> '{new_filename}'")

if __name__ == "__main__":
    main()