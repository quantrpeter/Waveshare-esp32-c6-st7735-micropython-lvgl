from machine import I2C, Pin
import time
import math
from mcp4725 import MCP4725 # Assuming the driver file is named mcp4725.py

# Initialize I2C (adjust pins and frequency as needed for your board)
i2c = I2C(0, scl=Pin(1), sda=Pin(2), freq=100000) 

# Create an MCP4725 object with the I2C address (default is 0x60)
dac = MCP4725(i2c, address=0x60)

# Sine wave parameters
frequency = 1000.0  # Hz
amplitude = 2048  # DAC units (0-4095, so 2048 is half range)
offset = 2048     # DAC offset (center around VCC/2)
samples_per_cycle = 100  # Number of samples per sine wave cycle
delay_us = int((1_000_000 / frequency) / samples_per_cycle)  # Microseconds between samples

print(f"Generating sine wave at {frequency} Hz")
print(f"Sample delay: {delay_us} microseconds")

# Generate sine wave
step = 0
while True:
    # Calculate sine value (-1 to 1)
    angle = (step * 2 * math.pi) / samples_per_cycle
    sine_value = math.sin(angle)
    
    # Convert to DAC value (0-4095)
    dac_value = int(offset + amplitude * sine_value)
    
    # Ensure value is within DAC range
    dac_value = max(0, min(4095, dac_value))
    
    # Output to DAC
    dac.raw_value = dac_value
    
    # Move to next sample
    step = (step + 1) % samples_per_cycle
    
    # Small delay to control frequency
    time.sleep_us(delay_us)
