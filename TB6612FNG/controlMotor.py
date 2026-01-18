# tb6612fng_simple.py
# MicroPython example for TB6612FNG + two DC motors (e.g. Tamiya 4WD)
# Works on Pico, ESP32, etc.

from machine import Pin, PWM
from time import sleep

# ────────────────────────────────────────────────
# Pin definitions (change to match YOUR wiring!)
# ────────────────────────────────────────────────

STBY = Pin(22, Pin.OUT)          # Standby pin – must be HIGH to enable driver

# Motor A (usually left motors on Tamiya 4WD)
AIN1 = Pin(18, Pin.OUT)
AIN2 = Pin(19, Pin.OUT)
PWMA = PWM(Pin(20), freq=1000, duty_u16=0)   # PWM freq 1kHz is fine

# ────────────────────────────────────────────────
# Helper functions
# ────────────────────────────────────────────────

def motor_a(speed):
    """
    speed: -1000 to +1000
      positive = forward
      negative = reverse
      0 = stop (coast)
    """
    if speed > 0:
        AIN1.value(1)
        AIN2.value(0)
        PWMA.duty_u16(speed * 65)          # 0→65535 range
    elif speed < 0:
        AIN1.value(0)
        AIN2.value(1)
        PWMA.duty_u16((-speed) * 65)
    else:
        AIN1.value(0)                       # coast stop
        AIN2.value(0)
        PWMA.duty_u16(0)


def drive(left_speed):
    """ left_speed: -1000 to 1000 """
    motor_a(left_speed)


# ────────────────────────────────────────────────
# Main demo
# ────────────────────────────────────────────────

STBY.value(1)  # Enable the driver (important!)
print("TB6612FNG enabled")

try:
    print("Forward slow...")
    drive(700)
    sleep(5)

    print("Forward full...")
    drive(1000)
    sleep(5)

    print("Stop (coast)...")
    drive(0)
    sleep(3)

    print("Backward slow...")
    drive(-700)
    sleep(5)

    print("Backward full...")
    drive(-1000)
    sleep(5)

    print("Brake demo (short brake)...")
    AIN1.value(1);
    AIN2.value(1)    # short brake on A
    PWMA.duty_u16(0)
    sleep(3)

    print("Stop everything")
    drive(0)

finally:
    STBY.value(0)               # Optional: go to low-power standby
    print("Done.")