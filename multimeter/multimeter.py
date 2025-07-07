import lcd_bus
from micropython import const
import machine
from time import sleep
import st7735
import lvgl as lv
import utime as time
from fs_driver import fs_register
from machine import Pin
import AD9833

selected = 0

def drawMenu():
    button1 = lv.button(scrn)
    button1.set_pos(4, 30)
    button1.set_size(40, 20)
    label1 = lv.label(button1)
    label1.set_text("Func")
    label1.set_style_text_color(lv.color_hex(0x000000), 0)  # Black text
    label1.set_style_text_font(lv.font_montserrat_12, 0)
    if selected == 0:
        button1.set_style_bg_color(
            lv.color_hex(0xffffff), 0)
    label1.center()

    button2 = lv.button(scrn)
    button2.set_pos(50, 30)
    button2.set_size(75, 20)
    label2 = lv.label(button2)
    label2.set_text("Multimeter")
    label2.set_style_text_color(lv.color_hex(0x000000), 0)  # Black text
    label2.set_style_text_font(lv.font_montserrat_12, 0)
    if selected == 1:
        button2.set_style_bg_color(
            lv.color_hex(0xffffff), 0)
    label2.center()


# display settings
_WIDTH = 128
_HEIGHT = 128
_BL = 19
_RST = 14
_DC = 15

_MOSI = 21  # SDA
# _MISO = 20
_SCK = 22  # SCL
_HOST = 1  # SPI2

_LCD_CS = 18
_LCD_FREQ = 8000000

_OFFSET_X = 2
_OFFSET_Y = 3

print('s1')
spi_bus = machine.SPI.Bus(
    host=_HOST,
    mosi=_MOSI,
    # miso=_MISO,
    sck=_SCK
)

print('s2')
display_bus = lcd_bus.SPIBus(
    spi_bus=spi_bus,
    freq=_LCD_FREQ,
    dc=_DC,
    cs=_LCD_CS,
)

print('s3')
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

print('s4')

# Initialize display
display.init(st7735.TYPE_R_RED)
display.set_rotation(lv.DISPLAY_ROTATION._180)
display.set_backlight(100)

# Create screen
scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)

fs_drv = lv.fs_drv_t()
fs_register(fs_drv, "S")

img = lv.image(scrn)
img.set_src("S:colorful20.png")
img.set_size(20, 20)
img.set_pos(0, 5)


label = lv.label(scrn)
label.set_text("Multimeter")
label.set_pos(24, 8)
label.set_style_text_color(lv.color_hex(0xffffff), 0)
label.set_style_text_font(lv.font_montserrat_12, 0)

button0 = Pin(20, Pin.IN, Pin.PULL_UP)  # Button pin
button1 = Pin(5, Pin.IN, Pin.PULL_UP)  # Button pin

drawMenu()

display_bus.deinit()

ad9833 = AD9833.AD9833(sdo = 4, clk = 3, cs = 2,  fmclk = 25)
ad9833.set_frequency(1300, 0)
ad9833.set_frequency(2600, 1)
ad9833.set_phase(0, 0, rads = False)
ad9833.set_phase(180, 1, rads = False)
ad9833.select_freq_phase(0,0)
ad9833.set_mode('SIN')

time.sleep(3)

ad9833.set_mode('SQUARE')
time.sleep(3)

print("end")
while True:
    time.sleep_ms(20)
    lv.task_handler()
    sleep(0.2)
    if not button0.value():
        selected = (selected + 1) % 2
        print(selected)
        drawMenu()
        lv.refr_now(lv.screen_active().get_display())
    if not button1.value():
        selected = (selected - 1) % 2
        print(selected)
        drawMenu()
        lv.refr_now(lv.screen_active().get_display())
