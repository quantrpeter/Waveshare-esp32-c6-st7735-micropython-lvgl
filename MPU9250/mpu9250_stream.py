"""
MPU9250 Data Streamer - Sends sensor data over serial for GUI visualization
Run this on ESP32-C6 to stream data to Mac
"""

from machine import I2C, Pin
from time import sleep_ms, ticks_ms, ticks_diff
import json
from mpu9250 import MPU9250


def main():
    """Stream MPU9250 data as JSON over serial"""
    
    # Initialize I2C and MPU9250
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    mpu = MPU9250(i2c)
    
    # Initialize angle tracking
    angle_x = 0.0
    angle_y = 0.0
    angle_z = 0.0
    last_time = ticks_ms()
    
    print("MPU9250 streaming started")
    sleep_ms(1000)  # Wait for serial connection
    
    try:
        while True:
            # Calculate time difference
            current_time = ticks_ms()
            dt = ticks_diff(current_time, last_time) / 1000.0
            last_time = current_time
            
            # Read sensors
            ax, ay, az = mpu.read_accel()
            gx, gy, gz = mpu.read_gyro()
            mx, my, mz = mpu.read_mag()
            temp = mpu.read_temp()
            
            # Integrate gyroscope to get angles
            angle_x += gx * dt
            angle_y += gy * dt
            angle_z += gz * dt
            
            # Create data packet
            data = {
                'accel': [ax, ay, az],
                'gyro': [gx, gy, gz],
                'mag': [mx, my, mz],
                'angles': [angle_x, angle_y, angle_z],
                'temp': temp
            }
            
            # Send as JSON
            print(json.dumps(data))
            
            sleep_ms(50)  # 20Hz update rate
            
    except KeyboardInterrupt:
        print("\nStopped by user")


if __name__ == "__main__":
    main()
