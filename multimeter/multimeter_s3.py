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
selectedFreqBtn = 0
current_freq = 4000


def drawMenu():
    # Only update button backgrounds and frequency label
    global menu_buttons, freq_label, selected, selectedFreqBtn, current_freq
    for i, btn in enumerate(menu_buttons):
        if i == selected:
            btn.set_style_bg_color(lv.color_hex(0xffffff), 0)
        else:
            btn.set_style_bg_color(lv.color_hex(0x8888dd), 0)

    for i, btn in enumerate(freq_buttons):
        if i == selectedFreqBtn:
            btn.set_style_bg_color(lv.color_hex(0xffffff), 0)
        else:
            btn.set_style_bg_color(lv.color_hex(0x8888dd), 0)

    freq_label.set_text(f"{current_freq} Hz")


# display settings
_WIDTH = 128
_HEIGHT = 128
_BL = 10
_RST = 13
_DC = 12

_MOSI = 8  # SDA
# _MISO = 9
_SCK = 7  # SCL
_HOST = 1  # SPI2

# AD9833
AD9833_SDO = 8
AD9833_CLK = 7
AD9833_CS = 3

# Buttons
BUTTON0 = 9
BUTTON1 = 6
BUTTON2 = 1
BUTTON3 = 2

_LCD_CS = 11
_LCD_FREQ = 4000000

_OFFSET_X = 2
_OFFSET_Y = 3

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

button0 = Pin(BUTTON0, Pin.IN, Pin.PULL_UP)  # Button pin
button1 = Pin(BUTTON1, Pin.IN, Pin.PULL_UP)  # Button pin
button2 = Pin(BUTTON2, Pin.IN, Pin.PULL_UP)  # Button pin
button3 = Pin(BUTTON3, Pin.IN, Pin.PULL_UP)  # Button pin


# --- Create menu buttons and labels once ---
menu_labels = ["SQU", "Tri", "SINE"]
menu_buttons = []
for i, label in enumerate(menu_labels):
    btn = lv.button(scrn)
    btn.set_pos(i*43, 30)
    btn.set_size(40, 20)
    lbl = lv.label(btn)
    lbl.set_text(label)
    lbl.set_style_text_color(lv.color_hex(0x000000), 0)
    lbl.set_style_text_font(lv.font_montserrat_12, 0)
    lbl.center()
    menu_buttons.append(btn)

# --- Create frequency adjustment buttons once ---
freq_btn_labels = ["-1k", "-100", "-10", "+10", "+100", "+1k"]
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

# --- Create frequency label once ---
freq_label = lv.label(scrn)
freq_label.set_pos(10, 95)
freq_label.set_style_text_color(lv.color_hex(0xffffff), 0)
freq_label.set_style_text_font(lv.font_montserrat_16, 0)
freq_label.set_text(f"{current_freq} Hz")

drawMenu()

# temp.value(1)
# display_bus.deinit()

ad9833 = AD9833.AD9833(sdo=AD9833_SDO, clk=AD9833_CLK, cs=AD9833_CS,  fmclk=25)
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
drawMenu()
lv.refr_now(lv.screen_active().get_display())
lv.task_handler()
while True:
    # time.sleep_ms(20)
    # sleep(0.2)
    b = False
    if not button0.value():  # Button pressed
        selected = (selected + 1) % 3
        print(selected)
        drawMenu()
        lv.refr_now(lv.screen_active().get_display())
        lv.task_handler()
        b = True
        while not button0.value():
            pass  # Wait for release (debounce)
    if not button1.value():  # Button pressed
        # change frequency based on selectedFreqBtn
        if selectedFreqBtn == 0:
            current_freq = max(0, current_freq - 1000)
        elif selectedFreqBtn == 1:
            current_freq = max(0, current_freq - 100)
        elif selectedFreqBtn == 2:
            current_freq = max(0, current_freq - 10)
        elif selectedFreqBtn == 3:
            current_freq = current_freq + 10
        elif selectedFreqBtn == 4:
            current_freq = current_freq + 100
        elif selectedFreqBtn == 5:
            current_freq = current_freq + 1000
        drawMenu()
        lv.refr_now(lv.screen_active().get_display())
        lv.task_handler()
        b = True
        while not button1.value():
            pass  # Wait for release (debounce)

    if not button2.value():  # Button pressed
        selectedFreqBtn = (selectedFreqBtn - 1) % 6
        print("button2")
        print(selectedFreqBtn)
        drawMenu()
        lv.refr_now(lv.screen_active().get_display())
        lv.task_handler()
        b = True
        while not button2.value():
            pass  # Wait for release (debounce)
    elif not button3.value():  # Button pressed
        selectedFreqBtn = (selectedFreqBtn + 1) % 6
        print("button3")
        print(selectedFreqBtn)
        drawMenu()
        lv.refr_now(lv.screen_active().get_display())
        lv.task_handler()
        b = True
        while not button3.value():
            pass  # Wait for release (debounce)

    if b:
        print(selected, current_freq)
        if selected == 0:
            ad9833.set_frequency(current_freq, 0)
            ad9833.set_mode('SQUARE/2')
        elif selected == 1:
            ad9833.select_freq_phase(0, 0)
            ad9833.set_frequency(current_freq, 0)
            ad9833.set_mode('TRIANGLE')
        elif selected == 2:
            ad9833.set_frequency(1100, 0)
            ad9833.set_frequency(2200, 1)
            ad9833.set_phase(0, 0, rads=False)
            ad9833.set_phase(180, 1, rads=False)
            ad9833.select_freq_phase(0, 0)
            ad9833.set_mode('SIN')
