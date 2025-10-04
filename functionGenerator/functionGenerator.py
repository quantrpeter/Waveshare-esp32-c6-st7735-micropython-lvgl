import lcd_bus
from micropython import const
import machine
import time
import AD9833

# ad9833 = AD9833.AD9833(sdo=22, clk=21, cs=-1, fmclk=20)
ad9833 = AD9833.AD9833(sdo = 3, clk = 2, cs = 1,  fmclk = 25)
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

while True:
	time.usleep(100)

