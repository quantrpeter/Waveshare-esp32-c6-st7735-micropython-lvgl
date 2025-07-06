# Example using Micropython + LVGL + Waveshare ESP32 Zero

## Convert png size to height 20px

python3 -c "from PIL import Image; img=Image.open('semiblock.png'); w,h=img.size; new_height=20; new_width=int(w*(new_height/h)); img=img.resize((new_width,new_height), Image.LANCZOS); img.save('semiblock.png')"