"""
MPU9250 MicroPython Example
9-axis IMU (Accelerometer, Gyroscope, Magnetometer)
"""

from machine import I2C, Pin
from time import sleep_ms, ticks_ms, ticks_diff
import math

class MPU9250:
    """MPU9250 9-axis IMU driver"""
    
    # MPU9250 I2C address
    MPU9250_ADDRESS = 0x68
    AK8963_ADDRESS = 0x0C
    
    # Register addresses
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43
    TEMP_OUT_H = 0x41
    WHO_AM_I = 0x75
    
    # Magnetometer registers
    MAG_CNTL = 0x0A
    MAG_XOUT_L = 0x03
    MAG_ST1 = 0x02
    MAG_CNTL2 = 0x0B
    MAG_ASAX = 0x10
    
    # Configuration registers
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    ACCEL_CONFIG2 = 0x1D
    INT_PIN_CFG = 0x37
    USER_CTRL = 0x6A
    
    def __init__(self, i2c, address=MPU9250_ADDRESS):
        self.i2c = i2c
        self.address = address
        
        # Wake up the MPU9250
        self.i2c.writeto_mem(self.address, self.PWR_MGMT_1, b'\x00')
        sleep_ms(100)
        
        # Check WHO_AM_I register
        who_am_i = self.i2c.readfrom_mem(self.address, self.WHO_AM_I, 1)[0]
        if who_am_i != 0x71:
            raise RuntimeError(f"MPU9250 not found. WHO_AM_I: 0x{who_am_i:02X}")
        
        # Configure gyroscope (±250°/s)
        self.i2c.writeto_mem(self.address, self.GYRO_CONFIG, b'\x00')
        
        # Configure accelerometer (±2g)
        self.i2c.writeto_mem(self.address, self.ACCEL_CONFIG, b'\x00')
        
        # Set accelerometer data rate (1kHz) and bandwidth (184Hz)
        self.i2c.writeto_mem(self.address, self.ACCEL_CONFIG2, b'\x01')
        
        # Set gyroscope data rate (1kHz) and bandwidth (184Hz)
        self.i2c.writeto_mem(self.address, self.CONFIG, b'\x01')
        
        # Initialize magnetometer
        self._init_magnetometer()
        
        print("MPU9250 initialized successfully")
    
    def read_accel(self):
        """Read accelerometer data (m/s²)"""
        data = self.i2c.readfrom_mem(self.address, self.ACCEL_XOUT_H, 6)
        
        # Convert to signed 16-bit integers
        ax = self._combine_bytes(data[0], data[1])
        ay = self._combine_bytes(data[2], data[3])
        az = self._combine_bytes(data[4], data[5])
        
        # Scale to g (±2g range, 16384 LSB/g)
        scale = 16384.0
        ax = (ax / scale) * 9.81  # Convert to m/s²
        ay = (ay / scale) * 9.81
        az = (az / scale) * 9.81
        
        return (ax, ay, az)
    
    def read_gyro(self):
        """Read gyroscope data (°/s)"""
        data = self.i2c.readfrom_mem(self.address, self.GYRO_XOUT_H, 6)
        
        # Convert to signed 16-bit integers
        gx = self._combine_bytes(data[0], data[1])
        gy = self._combine_bytes(data[2], data[3])
        gz = self._combine_bytes(data[4], data[5])
        
        # Scale to °/s (±250°/s range, 131 LSB/°/s)
        scale = 131.0
        gx = gx / scale
        gy = gy / scale
        gz = gz / scale
        
        return (gx, gy, gz)
    
    def read_temp(self):
        """Read temperature (°C)"""
        data = self.i2c.readfrom_mem(self.address, self.TEMP_OUT_H, 2)
        temp_raw = self._combine_bytes(data[0], data[1])
        
        # Convert to °C
        temp = (temp_raw / 333.87) + 21.0
        return temp
    
    def _init_magnetometer(self):
        """Initialize AK8963 magnetometer"""
        # Enable I2C master mode and set I2C bypass
        self.i2c.writeto_mem(self.address, self.INT_PIN_CFG, b'\x02')
        sleep_ms(10)
        
        # Power down magnetometer
        self.i2c.writeto_mem(self.AK8963_ADDRESS, self.MAG_CNTL, b'\x00')
        sleep_ms(10)
        
        # Enter fuse ROM access mode
        self.i2c.writeto_mem(self.AK8963_ADDRESS, self.MAG_CNTL, b'\x0F')
        sleep_ms(10)
        
        # Read sensitivity adjustment values
        asa_data = self.i2c.readfrom_mem(self.AK8963_ADDRESS, self.MAG_ASAX, 3)
        self.mag_sensitivity = [(((d - 128) * 0.5) / 128 + 1) for d in asa_data]
        
        # Power down magnetometer
        self.i2c.writeto_mem(self.AK8963_ADDRESS, self.MAG_CNTL, b'\x00')
        sleep_ms(10)
        
        # Set to continuous measurement mode (16-bit, 100Hz)
        self.i2c.writeto_mem(self.AK8963_ADDRESS, self.MAG_CNTL, b'\x16')
        sleep_ms(10)
        
        print("Magnetometer initialized")
    
    def read_mag(self):
        """Read magnetometer data (µT - microtesla)"""
        try:
            # Check if data is ready
            status = self.i2c.readfrom_mem(self.AK8963_ADDRESS, self.MAG_ST1, 1)[0]
            if not (status & 0x01):
                return (0, 0, 0)
            
            # Read magnetometer data (7 bytes: ST1, XL, XH, YL, YH, ZL, ZH)
            data = self.i2c.readfrom_mem(self.AK8963_ADDRESS, self.MAG_XOUT_L, 7)
            
            # Check overflow
            if data[6] & 0x08:
                return (0, 0, 0)
            
            # Convert to signed 16-bit integers (little-endian)
            mx = self._combine_bytes(data[2], data[1])
            my = self._combine_bytes(data[4], data[3])
            mz = self._combine_bytes(data[6], data[5])
            
            # Apply sensitivity adjustment
            mx = mx * self.mag_sensitivity[0] * 0.6  # Convert to µT (4912/32760 * 4)
            my = my * self.mag_sensitivity[1] * 0.6
            mz = mz * self.mag_sensitivity[2] * 0.6
            
            return (mx, my, mz)
        except:
            return (0, 0, 0)
    
    def _combine_bytes(self, msb, lsb):
        """Combine two bytes into signed 16-bit integer"""
        value = (msb << 8) | lsb
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value


def main():
    """Example usage of MPU9250"""
    
    # Initialize I2C
    # For ESP32-C6: Adjust pins according to your wiring
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    
    # Scan I2C bus
    print("Scanning I2C bus...")
    devices = i2c.scan()
    print(f"Found devices: {[hex(d) for d in devices]}")
    
    # Initialize MPU9250
    try:
        mpu = MPU9250(i2c)
    except Exception as e:
        print(f"Error initializing MPU9250: {e}")
        return
    
    print("\nReading MPU9250 data...")
    print("Press Ctrl+C to stop\n")
    
    # Initialize angle tracking
    angle_x = 0.0
    angle_y = 0.0
    angle_z = 0.0
    last_time = ticks_ms()
    
    try:
        while True:
            # Calculate time difference
            current_time = ticks_ms()
            dt = ticks_diff(current_time, last_time) / 1000.0  # Convert to seconds
            last_time = current_time
            
            # Read accelerometer
            ax, ay, az = mpu.read_accel()
            
            # Read gyroscope
            gx, gy, gz = mpu.read_gyro()
            
            # Integrate gyroscope to get angles
            angle_x += gx * dt
            angle_y += gy * dt
            angle_z += gz * dt
            
            # Read magnetometer
            mx, my, mz = mpu.read_mag()
            
            # Calculate heading (0-360°)
            heading = math.atan2(my, mx) * 180 / math.pi
            if heading < 0:
                heading += 360
            
            # Read temperature
            temp = mpu.read_temp()
            
            # clear console
            print("\033[2J\033[H", end="")  # ANSI escape codes to clear screen
            
            # Display data
            print("=" * 50)
            print(f"Accelerometer (m/s²):")
            print(f"  X: {ax:7.3f}  Y: {ay:7.3f}  Z: {az:7.3f}")
            print(f"Gyroscope Angles (°):")
            print(f"  Roll:  {angle_x:7.2f}°  (X-axis)")
            print(f"  Pitch: {angle_y:7.2f}°  (Y-axis)")
            print(f"  Yaw:   {angle_z:7.2f}°  (Z-axis)")
            print(f"Gyroscope Speed (°/s):")
            print(f"  X: {gx:7.2f}  Y: {gy:7.2f}  Z: {gz:7.2f}")
            print(f"Magnetometer (µT):")
            print(f"  X: {mx:7.2f}  Y: {my:7.2f}  Z: {mz:7.2f}")
            print(f"Heading: {heading:6.2f}° (0°=North, 90°=East)")
            print(f"Temperature: {temp:.2f}°C")
            
            sleep_ms(100)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user")


if __name__ == "__main__":
    main()
