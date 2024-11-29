from machine import Pin, SoftI2C
import time

# Configure I2C
# Replace Pin numbers with the pins you are using for SDA and SCL
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))  # Adjust pin numbers as needed

# Function to scan for I2C devices
def scan_i2c():
    devices = i2c.scan()
    
    if devices:
        print("I2C devices found:", len(devices))
        for device in devices:
            print("Device found at address:", hex(device))
    else:
        print("No I2C devices found")

# Run the scan function
while True:
    scan_i2c()
    time.sleep(5)  # Scan every 5 seconds