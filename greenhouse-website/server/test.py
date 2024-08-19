import io
from time import sleep
import serial

arduino = serial.Serial(port="/dev/tty.usbmodem1301", 
                        baudrate=9600,
                        timeout=2)

while True:
    raw = arduino.readline().removesuffix(b'\n')
    print(raw)
    if raw == b'':
        print("empty")
    else:
        print(int.from_bytes(raw))

    sleep(3)