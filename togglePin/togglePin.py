from machine import Pin

# Set up pin 1 as output
pin = Pin(1, Pin.OUT)

# Toggle pin as fast as possible
while True:
    pin.value(1)
    pin.value(0)