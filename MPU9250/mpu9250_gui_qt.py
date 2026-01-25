"""
MPU9250 PyQt GUI - Display sensor values with 3D orientation arrow
Runs on Mac and receives data from ESP32 via serial
"""

import sys
import json
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QComboBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
import math
import subprocess


class Arrow3DWidget(QWidget):
    """3D Arrow visualization widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.setMinimumSize(400, 400)
        
    def set_orientation(self, roll, pitch, yaw):
        """Update orientation angles (in degrees)"""
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.update()
        
    def paintEvent(self, event):
        """Draw 3D arrow"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Clear background
        painter.fillRect(self.rect(), QColor(20, 20, 20))
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        
        # Arrow size
        size = min(width, height) // 4
        
        # Convert angles to radians
        roll_rad = math.radians(self.roll)
        pitch_rad = math.radians(self.pitch)
        yaw_rad = math.radians(self.yaw)
        
        # Define arrow points in 3D space (pointing up along Z axis)
        arrow_points_3d = [
            (0, 0, size),           # tip
            (0, 8, size * 0.7),     # shaft right
            (0, -8, size * 0.7),    # shaft left
            (8, 0, size * 0.7),     # shaft front
            (-8, 0, size * 0.7),    # shaft back
            (0, 0, -size * 0.3),    # base
        ]
        
        # Rotate and project points
        projected_points = []
        for px, py, pz in arrow_points_3d:
            # Apply rotations (yaw, pitch, roll)
            # Yaw rotation (Z axis)
            x1 = px * math.cos(yaw_rad) - py * math.sin(yaw_rad)
            y1 = px * math.sin(yaw_rad) + py * math.cos(yaw_rad)
            z1 = pz
            
            # Pitch rotation (Y axis)
            x2 = x1 * math.cos(pitch_rad) + z1 * math.sin(pitch_rad)
            y2 = y1
            z2 = -x1 * math.sin(pitch_rad) + z1 * math.cos(pitch_rad)
            
            # Roll rotation (X axis)
            x3 = x2
            y3 = y2 * math.cos(roll_rad) - z2 * math.sin(roll_rad)
            z3 = y2 * math.sin(roll_rad) + z2 * math.cos(roll_rad)
            
            # Perspective projection
            scale = 400 / (400 + z3)
            screen_x = int(x3 * scale + center_x)
            screen_y = int(-y3 * scale + center_y)
            
            projected_points.append((screen_x, screen_y, z3))
        
        # Draw arrow
        if len(projected_points) >= 6:
            # Draw from base to shaft points
            base = projected_points[5]
            pen = QPen(QColor(0, 255, 0), 3)
            painter.setPen(pen)
            
            for i in range(1, 5):
                painter.drawLine(base[0], base[1], 
                               projected_points[i][0], projected_points[i][1])
            
            # Draw from shaft to tip (color-coded by depth)
            tip = projected_points[0]
            for i in range(1, 5):
                if tip[2] > projected_points[i][2]:
                    pen = QPen(QColor(255, 0, 0), 4)  # Red for front
                else:
                    pen = QPen(QColor(0, 0, 255), 4)  # Blue for back
                painter.setPen(pen)
                painter.drawLine(tip[0], tip[1], 
                               projected_points[i][0], projected_points[i][1])
            
            # Draw tip point
            painter.setBrush(QColor(255, 255, 0))
            painter.drawEllipse(tip[0] - 5, tip[1] - 5, 10, 10)
        
        # Draw orientation info
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Monospace", 10)
        painter.setFont(font)
        painter.drawText(10, 20, f"Roll:  {self.roll:7.1f}°")
        painter.drawText(10, 40, f"Pitch: {self.pitch:7.1f}°")
        painter.drawText(10, 60, f"Yaw:   {self.yaw:7.1f}°")


class MPU9250GUI(QMainWindow):
    """Main GUI window"""
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.mpremote_process = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle('MPU9250 Sensor Visualization')
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Connection controls
        conn_layout = QHBoxLayout()
        
        self.port_label = QLabel("Serial Port:")
        conn_layout.addWidget(self.port_label)
        
        self.port_combo = QComboBox()
        self.refresh_ports()
        conn_layout.addWidget(self.port_combo)
        
        self.refresh_btn = QPushButton("Refresh Ports")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        conn_layout.addWidget(self.refresh_btn)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_btn)
        
        self.status_label = QLabel("Status: Disconnected")
        conn_layout.addWidget(self.status_label)
        
        conn_layout.addStretch()
        main_layout.addLayout(conn_layout)
        
        # 3D Arrow visualization
        self.arrow_widget = Arrow3DWidget()
        main_layout.addWidget(self.arrow_widget)
        
        # Sensor data display
        data_layout = QHBoxLayout()
        
        # Accelerometer
        accel_layout = QVBoxLayout()
        accel_title = QLabel("Accelerometer (m/s²)")
        accel_title.setStyleSheet("font-weight: bold; color: #00ff00;")
        accel_layout.addWidget(accel_title)
        self.accel_label = QLabel("X: 0.0\nY: 0.0\nZ: 0.0")
        self.accel_label.setStyleSheet("font-family: monospace; color: #00ff00;")
        accel_layout.addWidget(self.accel_label)
        data_layout.addLayout(accel_layout)
        
        # Gyroscope
        gyro_layout = QVBoxLayout()
        gyro_title = QLabel("Gyroscope (°/s)")
        gyro_title.setStyleSheet("font-weight: bold; color: #00aaff;")
        gyro_layout.addWidget(gyro_title)
        self.gyro_label = QLabel("X: 0.0\nY: 0.0\nZ: 0.0")
        self.gyro_label.setStyleSheet("font-family: monospace; color: #00aaff;")
        gyro_layout.addWidget(self.gyro_label)
        data_layout.addLayout(gyro_layout)
        
        # Magnetometer
        mag_layout = QVBoxLayout()
        mag_title = QLabel("Magnetometer (µT)")
        mag_title.setStyleSheet("font-weight: bold; color: #ff00ff;")
        mag_layout.addWidget(mag_title)
        self.mag_label = QLabel("X: 0.0\nY: 0.0\nZ: 0.0")
        self.mag_label.setStyleSheet("font-family: monospace; color: #ff00ff;")
        mag_layout.addWidget(self.mag_label)
        data_layout.addLayout(mag_layout)
        
        # Temperature
        temp_layout = QVBoxLayout()
        temp_title = QLabel("Temperature")
        temp_title.setStyleSheet("font-weight: bold; color: #ffaa00;")
        temp_layout.addWidget(temp_title)
        self.temp_label = QLabel("0.0 °C")
        self.temp_label.setStyleSheet("font-family: monospace; font-size: 14pt; color: #ffaa00;")
        temp_layout.addWidget(self.temp_label)
        data_layout.addLayout(temp_layout)
        
        main_layout.addLayout(data_layout)
        
        # Timer for reading data
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial_data)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: white;
                border: 1px solid #555;
                padding: 3px;
            }
        """)
        
    def refresh_ports(self):
        """Refresh available serial ports"""
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}")
            
    def toggle_connection(self):
        """Toggle serial connection"""
        if self.mpremote_process is None:
            self.connect()
        else:
            self.disconnect()
            
    def connect(self):
        """Connect to ESP32 via mpremote"""
        try:
            # Get selected port
            port_text = self.port_combo.currentText()
            if not port_text:
                self.status_label.setText("Status: No port selected")
                return
            
            port = port_text.split(" - ")[0]
            
            # Get the full path to mpu9250_stream.py
            import os
            stream_script = os.path.join(os.path.dirname(__file__), 'mpu9250_stream.py')
            
            # Start mpremote process with unbuffered output
            self.mpremote_process = subprocess.Popen(
                ['mpremote', 'connect', port, 'run', stream_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.timer.start(50)  # 20Hz update rate
            self.connect_btn.setText("Disconnect")
            self.status_label.setText(f"Status: Connected to {port}")
            self.status_label.setStyleSheet("color: #00ff00;")
            
        except Exception as e:
            self.status_label.setText(f"Status: Error - {str(e)}")
            self.status_label.setStyleSheet("color: #ff0000;")
            
    def disconnect(self):
        """Disconnect from ESP32"""
        self.timer.stop()
        if self.mpremote_process:
            self.mpremote_process.terminate()
            self.mpremote_process = None
        self.connect_btn.setText("Connect")
        self.status_label.setText("Status: Disconnected")
        self.status_label.setStyleSheet("color: #ffffff;")
        
    def read_serial_data(self):
        """Read and parse data from serial port"""
        if self.mpremote_process is None:
            return
            
        try:
            # Check if process is still running
            if self.mpremote_process.poll() is not None:
                self.status_label.setText("Status: Connection lost")
                self.status_label.setStyleSheet("color: #ff0000;")
                self.disconnect()
                return
            
            # Read line from process (non-blocking)
            line = self.mpremote_process.stdout.readline()
            if not line:
                return
                
            line = line.strip()
            
            # Debug: print first few characters to see what we're getting
            if line and not line.startswith('{'):
                print(f"Non-JSON line: {line[:100]}")
                return
                
            # Parse JSON data
            data = json.loads(line)
            
            # Update display
            ax, ay, az = data['accel']
            gx, gy, gz = data['gyro']
            mx, my, mz = data['mag']
            roll, pitch, yaw = data['angles']
            temp = data['temp']
            
            self.accel_label.setText(f"X: {ax:7.2f}\nY: {ay:7.2f}\nZ: {az:7.2f}")
            self.gyro_label.setText(f"X: {gx:7.1f}\nY: {gy:7.1f}\nZ: {gz:7.1f}")
            self.mag_label.setText(f"X: {mx:7.1f}\nY: {my:7.1f}\nZ: {mz:7.1f}")
            self.temp_label.setText(f"{temp:.1f} °C")
            
            # Update 3D arrow
            self.arrow_widget.set_orientation(roll, pitch, yaw)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}, line: {line[:100] if line else 'empty'}")
        except Exception as e:
            print(f"Error reading data: {e}")
            
    def closeEvent(self, event):
        """Handle window close"""
        self.disconnect()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    gui = MPU9250GUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
