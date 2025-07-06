import lcd_bus
from micropython import const
import machine
from time import sleep
import st7735
import lvgl as lv
import utime as time
from fs_driver import fs_register
from machine import Pin

# display settings
_WIDTH = 128
_HEIGHT = 128
_BL = 19
_RST = 14
_DC = 15

_MOSI = 21 #SDA
#_MISO = 20
_SCK = 22  # SCL
_HOST = 1  # SPI2

_LCD_CS = 18
_LCD_FREQ = 2000000

_OFFSET_X = 2
_OFFSET_Y = 3

print('s1');
spi_bus = machine.SPI.Bus(
	host=_HOST,
	mosi=_MOSI,
	#miso=_MISO,
	sck=_SCK
)

print('s2');
display_bus = lcd_bus.SPIBus(
    spi_bus=spi_bus,
    freq=_LCD_FREQ,
    dc=_DC,
    cs=_LCD_CS,
)

print('s3');
display = st7735.ST7735(
    data_bus=display_bus,
    display_width=_WIDTH,
    display_height=_HEIGHT,
    backlight_pin=_BL,
    reset_pin=_RST,
    reset_state=st7735.STATE_LOW,
    backlight_on_state=st7735.STATE_HIGH,
    color_space=lv.COLOR_FORMAT.RGB565,
    color_byte_order=st7735.BYTE_ORDER_BGR,
    rgb565_byte_swap=True,
    offset_x=_OFFSET_X,
    offset_y=_OFFSET_Y
)

print('s4');

# Initialize display
display.init(st7735.TYPE_R_RED)
display.set_rotation(lv.DISPLAY_ROTATION._180)
display.set_backlight(100)

# Create screen
scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)  # Black background

fs_drv = lv.fs_drv_t()
fs_register(fs_drv, "S")

img = lv.image(scrn)
img.set_src("S:semiblock.png")
img.set_size(56, 20)
img.set_pos(0, 5)

label = lv.label(scrn)
label.set_text("Multimeter")
label.set_pos(54, 8)
label.set_style_text_color(lv.color_hex(0xffffff), 0)  # Black background\
# smaller font
label.set_style_text_font(lv.font_montserrat_12, 0)
p4=Pin(20, Pin.IN, Pin.PULL_UP)  # Button pin

print("end")

while True:
    time.sleep_ms(20)
    lv.task_handler()
    sleep(0.2)
    if not p4.value():  # Button pressed
        print("Button pressed")
        sleep(0.1)  # Debounce delay
        img.set_src("S:colorful.png")
        lv.refr_now(lv.screen_active().get_display())

