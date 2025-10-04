from machine import I2C, Pin
import time
from mcp4725 import MCP4725 # Assuming the driver file is named mcp4725.py

# Initialize I2C (adjust pins and frequency as needed for your board)
i2c = I2C(0, scl=Pin(2), sda=Pin(1), freq=100000) 

# Create an MCP4725 object with the I2C address (default is 0x60)
dac = MCP4725(i2c, address=0x60)

# Set the DAC output voltage
# You can set the raw 12-bit value (0-4095)
dac.raw_value = 2048 # Sets output to roughly half of VCC

# Or set a normalized value (0.0-1.0)
# dac.normalized_value = 0.5 

# Or set a value using a 16-bit range (0-65535), though it's a 12-bit DAC
# dac.value = 32767 

while True:
    time.msleep(100)
