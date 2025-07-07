# Example using Micropython + LVGL + Waveshare ESP32 Zero

https://www.waveshare.com/wiki/ESP32-C6-Zero

!!! Read the code, then you know what pins are connected to LCD

## Convert png size to height 20px

python3 -c "from PIL import Image; img=Image.open('semiblock.png'); w,h=img.size; new_height=20; new_width=int(w*(new_height/h)); img=img.resize((new_width,new_height), Image.LANCZOS); img.save('semiblock.png')"

## Resize image to height 20px

sips -Z 20 colorful.png --out colorful20.png

## AD9833 python module

https://github.com/owainm713/AD9833-MicroPython-Module

