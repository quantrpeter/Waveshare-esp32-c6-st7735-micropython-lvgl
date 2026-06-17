from machine import Pin, SoftI2C, ADC, PWM, UART
from time import sleep,sleep_ms, sleep_us
#import tm1637
import network
import math
 
### start
 
import machine
import lcd_bus
import st7735
import lvgl as lv
import urandom
import utime as time
_WIDTH =   128
_HEIGHT =   128
_BL =   19
_RST =   14
_DC =   15
_MOSI =   21
_SCK =   22
_HOST =   1
_LCD_CS =   18
_LCD_FREQ =   4000000
_OFFSET_X =   1
_OFFSET_Y =   2
spi_bus = machine.SPI.Bus(host=_HOST, mosi=_MOSI, miso=0, sck=_SCK)
display_bus = lcd_bus.SPIBus(spi_bus=spi_bus, freq=_LCD_FREQ, dc=_DC, cs=_LCD_CS)
display = st7735.ST7735(data_bus=display_bus, display_width=_WIDTH, display_height=_HEIGHT, backlight_pin=_BL, reset_pin=_RST, reset_state=st7735.STATE_LOW, backlight_on_state=st7735.STATE_HIGH, color_space=lv.COLOR_FORMAT.RGB565, color_byte_order=st7735.BYTE_ORDER_BGR, rgb565_byte_swap=True, offset_x=_OFFSET_X, offset_y=_OFFSET_Y)
display.init(st7735.TYPE_R_RED)
display.set_rotation(lv.DISPLAY_ROTATION._180)
display.set_backlight(100)
btn_left = Pin(1, Pin.IN, Pin.PULL_DOWN)
btn_right = Pin(2, Pin.IN, Pin.PULL_DOWN)
CELL =   8
COLS =   16
ROWS =   14
SCORE_H =   16
CLR_BG =   lv.color_hex(0x9BBC0F)
CLR_SNAKE =   lv.color_hex(0x306230)
CLR_FOOD =   lv.color_hex(0x0F380F)
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x9BBC0F), 0)
scrn.set_style_pad_all(0, 0)
scrn.remove_flag(lv.obj.FLAG.SCROLLABLE)
score_lbl = lv.label(scrn)
score_lbl.set_style_text_color(lv.color_hex(0x0F380F), 0)
score_lbl.align(lv.ALIGN.TOP_MID, 0, 1)
CANVAS_W =   COLS * CELL
CANVAS_H =   ROWS * CELL
cbuf = bytearray(CANVAS_W * CANVAS_H * 2)
canvas = lv.canvas(scrn)
canvas.set_buffer(cbuf, CANVAS_W, CANVAS_H, lv.COLOR_FORMAT.RGB565)
canvas.set_pos(0, SCORE_H)
canvas.fill_bg(CLR_BG, lv.OPA.COVER)
def draw_cell(col, row, color):
  x0 =   col * CELL
  y0 =   row * CELL
  for y in range(y0, y0 + CELL):
    for x in range(x0, x0 + CELL):
      canvas.set_px(x, y, color, lv.OPA.COVER)
 
 
def clear_cell(col, row):
  draw_cell(col, row, CLR_BG)
snake =   []
food =   None
direction =   1
score =   0
game_over =   False 