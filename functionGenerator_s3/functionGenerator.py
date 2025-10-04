
import AD9833
import utime as time


# AD9833
AD9833_SDO = 42
AD9833_CLK = 41
AD9833_CS = 1

ad9833 = AD9833.AD9833(sdo=AD9833_SDO, clk=AD9833_CLK, cs=AD9833_CS,  fmclk=25)
# ad9833 = AD9833.AD9833(sdo = 42, clk = 41, cs = 1,  fmclk = 25)

# setup frequency and phase registers
ad9833.set_frequency(1300,0)
ad9833.set_frequency(2600, 1)
ad9833.set_phase(0, 0, rads = False)
ad9833.set_phase(180, 1, rads = False)

delay = 1.5  # number of seconds to display each feature

# freq 0 Sin wave output
ad9833.select_freq_phase(0,0)
ad9833.set_mode('SIN')
time.sleep(delay)

# freq 1 Sin wave output
ad9833.select_freq_phase(1,0)
time.sleep(delay)

# freq 0 Triangle wave output
ad9833.select_freq_phase(0,0)
ad9833.set_mode('TRIANGLE')
time.sleep(delay)

# freq 0 Square wave output
ad9833.set_mode('SQUARE')
time.sleep(delay)

# freq 0 divide by 2 Square wave output
ad9833.set_mode('SQUARE/2')
time.sleep(delay)

# freq 0 Sin wave output
ad9833.set_mode('SIN')
time.sleep(delay)

# change freq 0 to 1700 Hz, Sin wave output
ad9833.set_frequency(1700,0)
time.sleep(delay)

# output off
ad9833.set_mode('OFF')