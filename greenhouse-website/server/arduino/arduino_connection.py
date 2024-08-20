import serial
import sys
import time
from struct import pack

from server.arduino import encode_input, decode_output
from server.database import get_arduino_conf, add_graph_entry

# data sent by arduino:
# error (bool)
# temperature (int7)
# humidity (int8)
# 2 bytes needed
# 
# data sent by pi:
# manual window setting 2 bits
# open window temperature (int7)
# close window temperature (int7)
# 2 bytes needed

arduino = serial.Serial(port="/dev/tty.usbmodem1301", 
                        baudrate=9600,
                        timeout=2)

graph_time = 3 # add a new graph entry every 60 seconds
last_graph = 0

while True:
    if time.time() - last_graph >= graph_time:
        raw = arduino.readline().removesuffix(b'\n')
        if raw != b'':
            output = decode_output(raw)
            last_graph = time.time()
            add_graph_entry(int(last_graph), output["temperature"], output["humidity"], output["error"])

    ardu_conf = b'\xFE' + encode_input(get_arduino_conf()) + b'\xFF'
    print(ardu_conf)
    arduino.write(ardu_conf)
    
    time.sleep(0.5)
