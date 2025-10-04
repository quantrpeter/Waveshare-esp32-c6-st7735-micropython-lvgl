from machine import Pin

# Set up pin 1 as output
pin = Pin(1, Pin.OUT)

# Toggle pin as fast as possible using toggle() method
while True:
    pin.toggle()