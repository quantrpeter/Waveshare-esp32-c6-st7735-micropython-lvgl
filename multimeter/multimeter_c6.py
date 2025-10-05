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

# AD9833 c6 zero
AD9833_SDO = 1
AD9833_CLK = 2
AD9833_CS = 22

# AD9833 c6 zero
# AD9833_SDO = 15
# AD9833_CLK = 14
# AD9833_CS = 22

# display settings
_WIDTH = 128
_HEIGHT = 128
_BL = 21
_RST = 18
_DC = 19

_MOSI = 15  # SDA
# _MISO = 20
_SCK = 14  # SCL
_HOST = 1  # SPI2
_LCD_CS = 20
_LCD_FREQ = 4000000
_OFFSET_X = 2
_OFFSET_Y = 3

# Buttons
BUTTON0 = 4
ROTATE_BUTTON_S1 = 5
ROTATE_BUTTON_S2 = 3

selected = 0
selectedFreqBtn = 0
currentFreq = 4000
currentPhase = 0  # Current phase in degrees


def format_frequency(freq):
    """Format frequency display with appropriate units"""
    if freq < 1000:
        return f"{freq} Hz"
    elif freq < 1000000:
        khz = freq / 1000.0
        if freq % 1000 == 0:
            return f"{khz} kHz"
        else:
            return f"{khz:.3f} kHz"
    else:
        mhz = freq / 1000000.0
        if freq % 1000000 == 0:
            return f"{mhz} MHz"
        else:
            return f"{mhz:.6f} MHz"


def drawMenu():
    # Only update button backgrounds and frequency label
    global menu_buttons, selected
    for i, btn in enumerate(menu_buttons):
        if i == selected:
            btn.set_style_bg_color(lv.color_hex(0xffffff), 0)
        else:
            btn.set_style_bg_color(lv.color_hex(0x8888dd), 0)


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

# Initialize display
display.init(st7735.TYPE_R_RED)
display.set_rotation(lv.DISPLAY_ROTATION._180)
display.set_backlight(100)

# Create screen
scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x000000), 0)
scrn.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

fs_drv = lv.fs_drv_t()
fs_register(fs_drv, "S")

img = lv.image(scrn)
img.set_src("S:blue.png")
img.set_size(20, 20)
img.set_pos(0, 5)


label = lv.label(scrn)
label.set_text("Func Generator")
label.set_pos(24, 8)
label.set_style_text_color(lv.color_hex(0xffffff), 0)
label.set_style_text_font(lv.font_montserrat_12, 0)

button0 = Pin(BUTTON0, Pin.IN, Pin.PULL_UP)  # Button pin

# Rotary encoder pins
rotary_s1 = Pin(ROTATE_BUTTON_S1, Pin.IN, Pin.PULL_UP)
rotary_s2 = Pin(ROTATE_BUTTON_S2, Pin.IN, Pin.PULL_UP)

# Initialize rotary encoder state
rotary_s1_prev = rotary_s1.value()
rotary_s2_prev = rotary_s2.value()

# --- Create menu buttons and labels once ---

freq = ["SQU", "SIN", "TRI"]
currentFreqLabelIndex = 0

menu_buttons = []
btn = lv.button(scrn)
btn.set_pos(0, 30)
btn.set_size(75, 20)  # Reduced width for waveform button
freqLbl = lv.label(btn)
freqLbl.set_text(freq[0])
freqLbl.set_style_text_color(lv.color_hex(0x000000), 0)
freqLbl.set_style_text_font(lv.font_montserrat_12, 0)
freqLbl.center()
menu_buttons.append(btn)

# PHASE button next to waveform button
phase_btn = lv.button(scrn)
phase_btn.set_pos(80, 30)  # Position next to waveform button
phase_btn.set_size(45, 20)
phase_btn_lbl = lv.label(phase_btn)
phase_btn_lbl.set_text("PHASE")
phase_btn_lbl.set_style_text_color(lv.color_hex(0x000000), 0)
phase_btn_lbl.set_style_text_font(lv.font_montserrat_12, 0)
phase_btn_lbl.center()
menu_buttons.append(phase_btn)  # Insert PHASE button as second button

for i, label in enumerate(["1Hz", "10Hz", "100Hz", "1kHz", "10kHz", "1MHz"]):
    btn = lv.button(scrn)
    if i < 3:
        btn.set_pos(i*40+i*3, 55)
    else:
        btn.set_pos((i-3)*40+(i-3)*3, 80)
    btn.set_size(40, 20)
    lbl = lv.label(btn)
    lbl.set_text(label)
    lbl.set_style_text_color(lv.color_hex(0x000000), 0)
    lbl.set_style_text_font(lv.font_montserrat_12, 0)
    lbl.center()
    menu_buttons.append(btn)


# --- Create frequency label once ---
freq_label = lv.label(scrn)
freq_label.set_pos(5, 100)
freq_label.set_style_text_color(lv.color_hex(0xffffff), 0)
freq_label.set_style_text_font(lv.font_montserrat_16, 0)
freq_label.set_text(format_frequency(currentFreq))

# --- Create phase label ---
phase_label = lv.label(scrn)
phase_label.set_pos(5, 115)
phase_label.set_style_text_color(lv.color_hex(0xffffff), 0)
phase_label.set_style_text_font(lv.font_montserrat_12, 0)
phase_label.set_text(f"Phase: {currentPhase}°")

drawMenu()

# temp.value(1)
# display_bus.deinit()

ad9833 = AD9833.AD9833(sdo=AD9833_SDO, clk=AD9833_CLK, cs=AD9833_CS,  fmclk=25)
ad9833.set_frequency(currentFreq, 0)
ad9833.set_phase(currentPhase, 0, rads=False)
ad9833.set_phase((currentPhase + 180) % 360, 1, rads=False)
ad9833.select_freq_phase(0, 0)
ad9833.set_mode('SQUARE')
time.sleep(2)

drawMenu()
lv.refr_now(lv.screen_active().get_display())
lv.task_handler()
while True:
    # time.sleep_ms(20)
    # sleep(0.2)
    b = False

    # Button handling
    if not button0.value():  # Button pressed
        selected = (selected + 1) % len(menu_buttons)
        print(selected)
        drawMenu()
        lv.refr_now(lv.screen_active().get_display())
        lv.task_handler()
        b = True
        while not button0.value():
            pass  # Wait for release (debounce)

    # Rotary encoder handling
    s1 = rotary_s1.value()
    s2 = rotary_s2.value()

    if s1 != rotary_s1_prev or s2 != rotary_s2_prev:
        # Detect rotation direction
        if selected == 0 and rotary_s1_prev == 1 and s1 == 0:  # S1 falling edge
            if s2 == 0:  # Clockwise
                currentFreqLabelIndex = (currentFreqLabelIndex + 1) % len(freq)
                print(f"Rotary CW: selected {selected}")
                freqLbl.set_text(freq[currentFreqLabelIndex])
                lv.refr_now(lv.screen_active().get_display())
                lv.task_handler()
                b = True
        elif selected == 0 and rotary_s2_prev == 1 and s2 == 0:  # S2 falling edge
            if s1 == 0:  # Counter-clockwise
                currentFreqLabelIndex = (currentFreqLabelIndex - 1) % len(freq)
                print(f"Rotary CCW: selected {selected}")
                freqLbl.set_text(freq[currentFreqLabelIndex])
                lv.refr_now(lv.screen_active().get_display())
                lv.task_handler()
                b = True
        elif selected > 1 and selected < 8 and rotary_s1_prev == 1 and s1 == 0:  # S1 falling edge
            if s2 == 0:  # Clockwise
                print(f"Rotary CW: selected {selected}")
                if selected == 2:
                    currentFreq += 1
                elif selected == 3:
                    currentFreq += 10
                elif selected == 4:
                    currentFreq += 100
                elif selected == 5:
                    currentFreq += 1000
                elif selected == 6:
                    currentFreq += 10000
                elif selected == 7:
                    currentFreq += 1000000
                if currentFreq > 12600000:
                    currentFreq = 12600000
                freq_label.set_text(format_frequency(currentFreq))
                lv.refr_now(lv.screen_active().get_display())
                lv.task_handler()
                b = True
        elif selected > 1 and selected < 8 and rotary_s2_prev == 1 and s2 == 0:  # S2 falling edge
            if s1 == 0:  # Counter-clockwise
                if selected == 2:
                    currentFreq -= 1
                elif selected == 3:
                    currentFreq -= 10
                elif selected == 4:
                    currentFreq -= 100
                elif selected == 5:
                    currentFreq -= 1000
                elif selected == 6:
                    currentFreq -= 10000
                elif selected == 7:
                    currentFreq -= 1000000
                if currentFreq < 0:
                    currentFreq = 0
                freq_label.set_text(format_frequency(currentFreq))
                lv.refr_now(lv.screen_active().get_display())
                lv.task_handler()
                b = True
        elif selected == 1 and rotary_s1_prev == 1 and s1 == 0:  # Phase adjustment - S1 falling edge
            if s2 == 0:  # Clockwise - increase phase
                currentPhase = (currentPhase + 10) % 360
                phase_label.set_text(f"Phase: {currentPhase}°")
                lv.refr_now(lv.screen_active().get_display())
                lv.task_handler()
                b = True
        elif selected == 1 and rotary_s2_prev == 1 and s2 == 0:  # Phase adjustment - S2 falling edge
            if s1 == 0:  # Counter-clockwise - decrease phase
                currentPhase = (currentPhase - 10) % 360
                phase_label.set_text(f"Phase: {currentPhase}°")
                lv.refr_now(lv.screen_active().get_display())
                lv.task_handler()
                b = True

        rotary_s1_prev = s1
        rotary_s2_prev = s2
        time.sleep_ms(10)  # Debounce delay

    if b:
        print(currentFreqLabelIndex, currentFreq, currentPhase)
        if currentFreqLabelIndex == 0:
            ad9833.set_frequency(currentFreq, 0)
            # ad9833.select_freq_phase(0, 0)
            ad9833.set_mode('SQUARE')
        elif currentFreqLabelIndex == 1:
            ad9833.set_frequency(currentFreq, 0)
            ad9833.set_phase((currentPhase + 180) % 360, 0, rads=False)
            # ad9833.set_phase((currentPhase + 180) % 360, 1, rads=False)
            ad9833.select_freq_phase(0, 0)
            ad9833.set_mode('SIN')
        elif currentFreqLabelIndex == 2:
            ad9833.select_freq_phase(0, 0)
            ad9833.set_frequency(currentFreq, 0)
            ad9833.set_mode('TRIANGLE')
