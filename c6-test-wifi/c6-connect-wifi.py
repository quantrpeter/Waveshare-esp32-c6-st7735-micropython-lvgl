import network
import urequests
import time
import sys

# WiFi credentials
SSID = 'Quantr 2.4G'
PASSWORD = 'quantrwifi'

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...", end="")
        wlan.connect(SSID, PASSWORD)
        # Wait for connection (with timeout)
        timeout = 10  # seconds
        start = time.time()

        while not wlan.isconnected():
            if time.time() - start > timeout:
                print("\nConnection timeout!")
                break
            time.sleep(0.3)
            print(".", end="")
        if wlan.isconnected():
            print("\nConnected successfully!")
            print("IP address:", wlan.ifconfig()[0])
            print("Network config:", wlan.ifconfig())
        else:
            print("\nFailed to connect :(")
            wlan.active(False)  # optional cleanup
            sys.exit()

def get_weather():
    try:
        # Using wttr.in for weather (no API key required)
        # Format: 3 gives location and condition
        response = urequests.get('http://wttr.in/?format=3')
        weather = response.text
        response.close()
        return weather
    except Exception as e:
        return f'Error getting weather: {e}'

# Main function
def main():
    connect_wifi()
    weather_info = get_weather()
    print('Weather:', weather_info)

if __name__ == '__main__':
    main()
