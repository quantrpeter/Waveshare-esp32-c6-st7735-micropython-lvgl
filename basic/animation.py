import lcd_bus
from micropython import const
import machine
from time import sleep
import st7735
import lvgl as lv

lv.init()

# display settings
_WIDTH = 128
_HEIGHT = 128
_BL = 19
_RST = 14
_DC = 15

_MOSI = 21 #SDA
_MISO = 20
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
scrn.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)  # Disable scrollbars

# Create animated text label
animated_label = lv.label(scrn)
animated_label.set_text('SemiBlock')
animated_label.set_style_text_color(lv.color_hex(0x00ff00), 0)  # Green text

# Position the label initially at left edge
animated_label.set_pos(0, 60)

# Animation variables - keep within screen bounds
anim_x = 0
anim_direction = 1
anim_speed = 2

print('end')

import utime as time
time_passed = 1000

while True:
    start_time = time.ticks_ms()
    
    # Manual animation logic
    anim_x += anim_speed * anim_direction
    
    # Check boundaries and reverse direction - stay within screen
    if anim_x > 80:  # Right boundary (screen width - text width)
        anim_direction = -1  # Reverse direction
    elif anim_x < 0:  # Left boundary
        anim_direction = 1  # Reverse direction
    
    # Update label position
    animated_label.set_x(int(anim_x))
    
    time.sleep_ms(20)  # Animation frame delay
    lv.tick_inc(time_passed)
    lv.task_handler()
    end_time = time.ticks_ms()
    time_passed = time.ticks_diff(end_time, start_time)