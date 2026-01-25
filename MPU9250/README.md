# MPU9250 Sensor Visualization

A comprehensive toolkit for reading and visualizing MPU9250 9-axis IMU sensor data with both console output and PyQt GUI visualization featuring a 3D orientation arrow.

## Features

- **9-Axis Sensor Support**: Reads accelerometer, gyroscope, and magnetometer data
- **Real-time Orientation Tracking**: Integrates gyroscope data to calculate roll, pitch, and yaw angles
- **3D Visualization**: Interactive 3D arrow showing device orientation in real-time
- **PyQt GUI**: Modern desktop application with live sensor data display
- **Data Streaming**: JSON-based data streaming from ESP32 to PC via serial
- **Temperature Monitoring**: Real-time temperature readings from the MPU9250

## Hardware Requirements

- ESP32-C6 (or compatible ESP32 variant)
- MPU9250 9-axis IMU sensor
- I2C connection:
  - SDA: GPIO 21
  - SCL: GPIO 22

## Software Requirements

### ESP32 (MicroPython)
- MicroPython firmware
- `mpremote` tool for uploading and running scripts

### PC/Mac (Python 3)
- Python 3.8 or higher
- PyQt5
- pyserial

## Installation

### 1. Install Python Dependencies (PC/Mac)

```bash
pip install PyQt5 pyserial
```

### 2. Install mpremote

```bash
pip install mpremote
```

### 3. Upload MPU9250 Driver to ESP32

```bash
mpremote cp mpu9250.py :
```

### 4. Upload Stream Script to ESP32

```bash
mpremote cp mpu9250_stream.py :
```

## Project Files

### mpu9250.py
The main MPU9250 driver library for MicroPython. Handles:
- I2C communication with MPU9250
- Accelerometer configuration and reading (±2g range)
- Gyroscope configuration and reading (±250°/s range)
- Magnetometer (AK8963) initialization and reading
- Temperature sensor reading
- Data conversion and scaling

**Usage:**
```python
from mpu9250 import MPU9250
from machine import I2C, Pin

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
mpu = MPU9250(i2c)

# Read sensors
ax, ay, az = mpu.read_accel()  # m/s²
gx, gy, gz = mpu.read_gyro()   # °/s
mx, my, mz = mpu.read_mag()    # µT
temp = mpu.read_temp()          # °C
```

### mpu9250_stream.py
Data streaming script that runs on the ESP32. Continuously reads sensor data and outputs it as JSON via serial connection for real-time visualization on PC/Mac.

**Features:**
- Angle integration from gyroscope data
- 20Hz update rate (configurable)
- JSON output format for easy parsing
- Automatic reconnection handling

**Output Format:**
```json
{
  "accel": [ax, ay, az],
  "gyro": [gx, gy, gz],
  "mag": [mx, my, mz],
  "angles": [roll, pitch, yaw],
  "temp": temperature
}
```

### mpu9250_gui_qt.py
PyQt5-based desktop GUI application for visualizing MPU9250 data on PC/Mac.

**Features:**
- Serial port auto-detection and selection
- Real-time 3D arrow visualization with perspective projection
- Live sensor value display with color-coded readouts:
  - Accelerometer (green)
  - Gyroscope (cyan)
  - Magnetometer (magenta)
  - Temperature (orange)
- Dark theme UI
- Automatic mpremote process management
- Connection status monitoring

**Controls:**
- **Refresh Ports**: Scan for available serial devices
- **Connect/Disconnect**: Start/stop data streaming
- **Port Selection**: Choose ESP32 device from dropdown

### mpu9250_gui.py
LVGL-based GUI for ST7735 display (128x128). Shows sensor data and 3D arrow on the ESP32's attached display.

**Note**: This version is for embedded display, not for PC visualization.

## Usage

### Option 1: Console Output (ESP32 Only)

Run the basic example directly on ESP32:

```bash
mpremote run mpu9250.py
```

This displays sensor data in the terminal with real-time updates.

### Option 2: PyQt GUI Visualization (Recommended)

1. **Start the GUI on your PC/Mac:**
   ```bash
   python mpu9250_gui_qt.py
   ```

2. **In the GUI window:**
   - Select your ESP32's serial port from the dropdown
   - Click **Connect**
   - The GUI will automatically:
     - Run `mpu9250_stream.py` on the ESP32 via mpremote
     - Stream data over serial
     - Update the 3D visualization in real-time

3. **Interact with the visualization:**
   - Move/rotate the MPU9250 sensor
   - Watch the 3D arrow update in real-time
   - Monitor all sensor values at the bottom

### Option 3: Manual Data Streaming

If you want to see raw JSON data or integrate with other tools:

```bash
mpremote run mpu9250_stream.py
```

This streams JSON data that can be piped to other applications.

## Sensor Data Explained

### Accelerometer (m/s²)
Measures linear acceleration along X, Y, Z axes. When stationary, shows gravity (~9.81 m/s² on Z-axis).

### Gyroscope (°/s)
Measures angular velocity (rotation speed) around X, Y, Z axes.

### Magnetometer (µT - microtesla)
Measures magnetic field strength. Used for heading/compass calculations.

### Angles (degrees)
- **Roll**: Rotation around X-axis (left/right tilt)
- **Pitch**: Rotation around Y-axis (forward/backward tilt)
- **Yaw**: Rotation around Z-axis (compass direction)

*Note: Angles are calculated by integrating gyroscope data and will drift over time without sensor fusion.*

## Troubleshooting

### "MPU9250 not found" Error
- Check I2C wiring (SDA: GPIO 21, SCL: GPIO 22)
- Verify MPU9250 is powered (3.3V)
- Check I2C address (default 0x68)
- Try scanning I2C bus: `i2c.scan()`

### GUI Shows All Zeros
- Ensure `mpu9250_stream.py` is uploaded to ESP32
- Check serial port selection
- Try disconnecting and reconnecting
- Verify ESP32 is not running other scripts
- Check terminal for debug output

### Connection Issues
- Make sure only one program accesses the serial port
- Close Arduino IDE or other serial monitors
- Try unplugging and replugging the ESP32
- Check USB cable quality (use data cable, not charge-only)

### Angle Drift
This is normal behavior when using gyroscope integration. For better results:
- Use complementary filter with accelerometer
- Implement sensor fusion (Kalman filter, Madgwick filter)
- Reset angles periodically if needed

### Serial Import Error on ESP32
If you see "ImportError: no module named 'serial'" when running with mpremote:
- This means you're trying to run the GUI on ESP32
- Run `python mpu9250_gui_qt.py` on your PC/Mac instead
- Never use `mpremote run` with the GUI file

## Performance Tuning

### Adjust Update Rate
In `mpu9250_stream.py`, change the sleep time:
```python
sleep_ms(50)  # 20Hz (default)
sleep_ms(100) # 10Hz (lower CPU usage)
sleep_ms(20)  # 50Hz (higher rate)
```

### GUI Refresh Rate
In `mpu9250_gui_qt.py`, modify timer interval:
```python
self.timer.start(50)  # 20Hz (default)
self.timer.start(100) # 10Hz (smoother but slower)
```

## Advanced Usage

### Custom Sensor Ranges

Edit `mpu9250.py` to change sensor ranges:

```python
# Gyroscope: ±250, ±500, ±1000, ±2000 °/s
self.i2c.writeto_mem(self.address, self.GYRO_CONFIG, b'\x08')  # ±500°/s

# Accelerometer: ±2g, ±4g, ±8g, ±16g
self.i2c.writeto_mem(self.address, self.ACCEL_CONFIG, b'\x08')  # ±4g
```

### Data Logging

Capture streaming data to file:
```bash
mpremote run mpu9250_stream.py > sensor_log.json
```

Parse in Python:
```python
import json

with open('sensor_log.json') as f:
    for line in f:
        if line.startswith('{'):
            data = json.loads(line)
            print(data['angles'])
```

## License

MIT License - Free for personal and commercial use.

## Contributing

Feel free to submit issues and pull requests for:
- Bug fixes
- Performance improvements
- Additional visualization modes
- Sensor fusion algorithms
- Documentation improvements

## References

- [MPU9250 Datasheet](https://invensense.tdk.com/products/motion-tracking/9-axis/mpu-9250/)
- [AK8963 Magnetometer](https://www.akm.com/akm/en/file/datasheet/AK8963C.pdf)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [MicroPython Documentation](https://docs.micropython.org/)