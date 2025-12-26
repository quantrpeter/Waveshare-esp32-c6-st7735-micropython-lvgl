import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

for net in wlan.scan():
    print(f"{net[0].decode():<20} RSSI: {net[3]:<4} Ch: {net[2]}")