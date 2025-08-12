# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)

import network
import time
ssid = "peter 2.4G"
password = "peter1234"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('Connecting to network...')
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
print('MAC address:', ':'.join(['%02x' % b for b in wlan.config('mac')]))
print('Network config:', wlan.ifconfig())


import webrepl
webrepl.start()
