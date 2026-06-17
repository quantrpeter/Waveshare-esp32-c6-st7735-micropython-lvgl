from machine import Pin, SoftI2C, ADC, PWM, UART
from time import sleep,sleep_ms, sleep_us
#import tm1637
import network
import math
 
### start
 
p0 = Pin(20, Pin.IN, Pin.PULL_DOWN)
from machine import Pin, SoftI2C, ADC, PWM, UART
from time import sleep, sleep_ms, sleep_us
import utime as time
import network
import math
import lcd_bus
from micropython import const
import machine
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
 
# display.set_power(True)
display.init(st7735.TYPE_R_RED)
display.set_rotation(lv.DISPLAY_ROTATION._180)
display.set_backlight(100)
 
scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0xff0000), 0)
 
label = lv.label(scrn)
label.set_text("Hello Peter")
label.set_style_text_color(lv.color_hex(0xffffff), 0)
label.align(lv.ALIGN.CENTER, 0, 30)
while True:
  time_passed = 1000
  start_time = time.ticks_ms()
  time.sleep_ms(1)  # sleep for 1 ms
  lv.tick_inc(time_passed)
  lv.task_handler()
  end_time = time.ticks_ms()
  time_passed = time.ticks_diff(end_time, start_time)
 
  var1=p0.read(8)
  print(var1)
  sleep_ms(500)