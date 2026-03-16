import lcd_bus
import machine
import st7735
import lvgl as lv
import urandom
import utime as time

lv.init()

# ── Display settings ──
_WIDTH = 128
_HEIGHT = 128
_BL = 21
_RST = 18
_DC = 19
_MOSI = 15
_SCK = 14
_HOST = 1
_LCD_CS = 20
_LCD_FREQ = 4000000
_OFFSET_X = 2
_OFFSET_Y = 3

BUTTON1 = 22
BUTTON2 = 23

spi_bus = machine.SPI.Bus(host=_HOST, mosi=_MOSI, sck=_SCK)
display_bus = lcd_bus.SPIBus(spi_bus=spi_bus, freq=_LCD_FREQ, dc=_DC, cs=_LCD_CS)
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
    offset_y=_OFFSET_Y,
)
display.init(st7735.TYPE_R_RED)
display.set_rotation(lv.DISPLAY_ROTATION._180)
display.set_backlight(100)

# ── Buttons ──
btn_left = machine.Pin(BUTTON1, machine.Pin.IN, machine.Pin.PULL_DOWN)
btn_right = machine.Pin(BUTTON2, machine.Pin.IN, machine.Pin.PULL_DOWN)

# ── Game constants ──
CELL = 8
COLS = 16
ROWS = 14
SCORE_H = 16

# Nokia green palette
CLR_BG = lv.color_hex(0x9BBC0F)
CLR_SNAKE = lv.color_hex(0x306230)
CLR_FOOD = lv.color_hex(0x0F380F)

DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

# ── Screen ──
scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x9BBC0F), 0)
scrn.set_style_pad_all(0, 0)
scrn.remove_flag(lv.obj.FLAG.SCROLLABLE)

# Score
score_lbl = lv.label(scrn)
score_lbl.set_style_text_color(lv.color_hex(0x0F380F), 0)
score_lbl.align(lv.ALIGN.TOP_MID, 0, 1)

# Canvas
CANVAS_W = COLS * CELL
CANVAS_H = ROWS * CELL
cbuf = bytearray(CANVAS_W * CANVAS_H * 2)
canvas = lv.canvas(scrn)
canvas.set_buffer(cbuf, CANVAS_W, CANVAS_H, lv.COLOR_FORMAT.RGB565)
canvas.set_pos(0, SCORE_H)
canvas.fill_bg(CLR_BG, lv.OPA.COVER)

def draw_cell(col, row, color):
    x0 = col * CELL
    y0 = row * CELL
    for y in range(y0, y0 + CELL):
        for x in range(x0, x0 + CELL):
            canvas.set_px(x, y, color, lv.OPA.COVER)

def clear_cell(col, row):
    draw_cell(col, row, CLR_BG)

# ── Game state ──
snake = []
food = None
direction = 1
score = 0
game_over = False

def spawn_food():
    global food
    free = []
    for c in range(COLS):
        for r in range(ROWS):
            if (c, r) not in snake:
                free.append((c, r))
    if not free:
        return
    food = free[urandom.getrandbits(8) % len(free)]
    draw_cell(food[0], food[1], CLR_FOOD)

def update_score():
    score_lbl.set_text('Score: ' + str(score))

def init_game():
    global snake, food, direction, score, game_over
    canvas.fill_bg(CLR_BG, lv.OPA.COVER)
    snake = [(8, 7), (7, 7), (6, 7)]
    food = None
    direction = 1
    score = 0
    game_over = False
    for c, r in snake:
        draw_cell(c, r, CLR_SNAKE)
    spawn_food()
    update_score()
    canvas.invalidate()

def step():
    global game_over, score
    hc, hr = snake[0]
    dx, dy = DIRS[direction]
    nc, nr = hc + dx, hr + dy

    if nc < 0 or nc >= COLS or nr < 0 or nr >= ROWS:
        game_over = True
        return
    if (nc, nr) in snake[:-1]:
        game_over = True
        return

    ate = (nc, nr) == food
    snake.insert(0, (nc, nr))
    draw_cell(nc, nr, CLR_SNAKE)

    if ate:
        score += 1
        update_score()
        spawn_food()
    else:
        tc, tr = snake.pop()
        clear_cell(tc, tr)
    canvas.invalidate()

def show_game_over():
    score_lbl.set_text('GAME OVER: ' + str(score))

# ── Main loop ──
init_game()
lv.task_handler()

last_step = time.ticks_ms()
btn1_prev = 0
btn2_prev = 0
over_shown = False

time_passed = 1000
while True:
    start_time = time.ticks_ms()
    b1 = btn_left.value()
    b2 = btn_right.value()

    if not game_over:
        if b1 == 1 and btn1_prev == 0:
            direction = (direction - 1) % 4
        if b2 == 1 and btn2_prev == 0:
            direction = (direction + 1) % 4

        speed = max(80, 200 - score * 5)
        now = time.ticks_ms()
        if time.ticks_diff(now, last_step) >= speed:
            print('Stepping, score:', score, 'speed:', speed)
            step()
            last_step = now
    else:
        if not over_shown:
            print('Game over, showing message')
            show_game_over()
            over_shown = True
        if (b1 == 1 and btn1_prev == 0) or (b2 == 1 and btn2_prev == 0):
            print('Restarting game')
            init_game()
            over_shown = False

    btn1_prev = b1
    btn2_prev = b2

    time.sleep_ms(20)
    lv.tick_inc(time_passed)
    lv.task_handler()
    end_time = time.ticks_ms()
    time_passed = time.ticks_diff(end_time, start_time)

