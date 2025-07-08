# Example using Micropython + LVGL + Waveshare ESP32 Zero

<<<<<<< HEAD
https://www.waveshare.com/wiki/ESP32-C6-Zero

!!! Read the code, then you know what pins are connected to LCD
=======
![](https://peter.quantr.hk/wp-content/uploads/2025/07/image-7.png)

https://peter.quantr.hk/2025/07/waveshare-esp32-c6-zero-st7735s/

## 128x128 LCD

https://e.tb.cn/h.hTP9hHMJnnsuv3r?tk=8Gu0VAFIgtS

https://detail.tmall.com/item.htm?app=chrome&bxsign=scd_zKwB5BjniToNIfqwaVQ5hkirRtbb0dHPuS5ZIJfWUmD8b-Wh20kyQWTEfb3uJXs68_TbBnu0uv26dO4EIiN_A3bMZr7rjdacs-M4lpYMuDonZ-3Hfcoo-AY0bWYx6Sa&cpp=1&id=947263405666&price=10.08&shareUniqueId=32298060381&share_crt_v=1&shareurl=true&short_name=h.hTPkUGqipFjUwqW&skuId=5854107368485&sourceType=item&sp_tk=UzhHZFZBRkltOWg%3D&spm=a2159r.13376460.0.0&suid=DB7129DD-0713-4A5A-87DA-E2FC5EABA983&tbSocialPopKey=shareItem&tk=S8GdVAFIm9h&un=8a0a0fd7954c2f6e4c6e4bed9157ce66&un_site=0&ut_sk=1.YQ5qR5EunYQDAGcswWUaYJAm_21380790_1751781871962.Copy.1&wxsign=tbwaztIB4G-2oX1kazN-09hj3rqgSXYo2F7SyTrX8jAQOhd9xo7vtQ7xma1bhiZdWIo4cbQvqlhEDBAEv1psgDhAjCWFZq1Tb9VKxhWlb65wmy1C01TLht5wY8bn8ba1AmK

## 80x160 LCD

https://detail.tmall.com/item.htm?app=chrome&bxsign=scd_zKwB5BjniToNIfqwaVQ5hkirRtbb0dHPuS5ZIJfWUmD8b-Wh20kyQWTEfb3uJXs68_TbBnu0uv26dO4EIiN_A3bMZr7rjdacs-M4lpYMuDonZ-3Hfcoo-AY0bWYx6Sa&cpp=1&id=947263405666&price=10.08&shareUniqueId=32298060381&share_crt_v=1&shareurl=true&short_name=h.hTPkUGqipFjUwqW&sourceType=item&sp_tk=UzhHZFZBRkltOWg%3D&spm=a2159r.13376460.0.0&suid=DB7129DD-0713-4A5A-87DA-E2FC5EABA983&tbSocialPopKey=shareItem&tk=S8GdVAFIm9h&un=8a0a0fd7954c2f6e4c6e4bed9157ce66&un_site=0&ut_sk=1.YQ5qR5EunYQDAGcswWUaYJAm_21380790_1751781871962.Copy.1&wxsign=tbwaztIB4G-2oX1kazN-09hj3rqgSXYo2F7SyTrX8jAQOhd9xo7vtQ7xma1bhiZdWIo4cbQvqlhEDBAEv1psgDhAjCWFZq1Tb9VKxhWlb65wmy1C01TLht5wY8bn8ba1AmK
>>>>>>> 592c8505e797237f324de1b7286d057de99f98e0

## Convert png size to height 20px

python3 -c "from PIL import Image; img=Image.open('semiblock.png'); w,h=img.size; new_height=20; new_width=int(w*(new_height/h)); img=img.resize((new_width,new_height), Image.LANCZOS); img.save('semiblock.png')"
<<<<<<< HEAD

## Resize image to height 20px

sips -Z 20 colorful.png --out colorful20.png

## AD9833 python module

https://github.com/owainm713/AD9833-MicroPython-Module

=======
>>>>>>> 592c8505e797237f324de1b7286d057de99f98e0
