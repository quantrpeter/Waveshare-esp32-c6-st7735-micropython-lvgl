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
current_freq = 1300


def drawMenu():
    button1 = lv.button(scrn)
    button1.set_pos(0, 30)
    button1.set_size(40, 20)
    label1 = lv.label(button1)
    label1.set_text("SQU")
    label1.set_style_text_color(lv.color_hex(0x000000), 0)  # Black text
    label1.set_style_text_font(lv.font_montserrat_12, 0)
    if selected == 0:
        button1.set_style_bg_color(
            lv.color_hex(0xffffff), 0)
    label1.center()

    button2 = lv.button(scrn)
    button2.set_pos(43, 30)
    button2.set_size(40, 20)
    label2 = lv.label(button2)
    label2.set_text("Tri")
    label2.set_style_text_color(lv.color_hex(0x000000), 0)  # Black text
    label2.set_style_text_font(lv.font_montserrat_12, 0)
    if selected == 1:
        button2.set_style_bg_color(
            lv.color_hex(0xffffff), 0)
    label2.center()

    button3 = lv.button(scrn)
    button3.set_pos(86, 30)
    button3.set_size(40, 20)
    label3 = lv.label(button3)
    label3.set_text("SINE")
    label3.set_style_text_color(lv.color_hex(0x000000), 0)  # Black text
    label3.set_style_text_font(lv.font_montserrat_12, 0)
    if selected == 2:
        button3.set_style_bg_color(
            lv.color_hex(0xffffff), 0)
    label3.center()

    # --- Add 6 frequency adjustment buttons below ---
    freq_btn_labels = ["-1k", "-100", "-10", "+10", "+100", "+1k"]
    freq_btn_steps = [-1000, -100, -10, 10, 100, 1000]
    global freq_buttons
    freq_buttons = []
    for i, label in enumerate(freq_btn_labels):
        btn = lv.button(scrn)
        btn.set_pos(2 + i*21, 60)
        btn.set_size(20, 20)
        lbl = lv.label(btn)
        lbl.set_text(label)
        lbl.set_style_text_color(lv.color_hex(0x000000), 0)
        lbl.set_style_text_font(lv.font_montserrat_12, 0)
        lbl.center()
        freq_buttons.append(btn)

    # --- Display frequency in next row ---
    global freq_label
    freq_label = lv.label(scrn)
    freq_label.set_pos(10, 95)
    freq_label.set_style_text_color(lv.color_hex(0xffffff), 0)
    freq_label.set_style_text_font(lv.font_montserrat_16, 0)
    freq_label.set_text(f"{current_freq} Hz")


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
_LCD_FREQ = 4000000

_OFFSET_X = 2
_OFFSET_Y = 3

print('s1')
spi_bus = machine.SPI.Bus(
    host=_HOST,
    mosi=_MOSI,
    # miso=_MISO,
    sck=_SCK
)
display_bus = lcd_bus.SPIBus(
    spi_bus=spi_bus,
    freq=_LCD_FREQ,
    dc=_DC,
    cs=_LCD_CS,
)


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
label.set_text("Func Generator")
label.set_pos(24, 8)
label.set_style_text_color(lv.color_hex(0xffffff), 0)
label.set_style_text_font(lv.font_montserrat_12, 0)

button0 = Pin(20, Pin.IN, Pin.PULL_UP)  # Button pin
button1 = Pin(5, Pin.IN, Pin.PULL_UP)  # Button pin

drawMenu()

# temp.value(1)
# display_bus.deinit()

ad9833 = AD9833.AD9833(sdo=21, clk=22, cs=2,  fmclk=25)
ad9833.set_frequency(1300, 0)
# ad9833.set_frequency(2600, 1)
ad9833.set_phase(0, 0, rads=False)
ad9833.set_phase(180, 1, rads=False)

time.sleep(0.5)

# ad9833.select_freq_phase(0,0)
# ad9833.set_mode('SIN')
# time.sleep(2)

ad9833.set_mode('SQUARE')
# ad9833.disable()
# time.sleep(2)

# temp.value(0)
# time.sleep(200)

print("end")
while True:
    time.sleep_ms(20)
    lv.task_handler()
    sleep(0.2)
    if not button0.value():  # Button pressed
        selected = (selected - 1) % 3
        print(selected)
        drawMenu()
    if not button1.value():  # Button pressed
        selected = (selected + 1) % 3
        print(selected)
        drawMenu()
    lv.refr_now(lv.screen_active().get_display())
    if selected == 0:
        ad9833.set_frequency(9000, 0)
        ad9833.set_mode('SQUARE')
    if selected == 1:
        ad9833.set_frequency(1300, 0)
        ad9833.set_mode('TRIANGLE')
    if selected == 2:
        # ad9833.select_freq_phase(0,0)
        ad9833.set_mode('SIN')
