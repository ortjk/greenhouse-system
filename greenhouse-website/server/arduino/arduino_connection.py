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

# open up serial port
arduino = serial.Serial(port="/dev/tty.usbmodem1301", 
                        baudrate=9600,
                        timeout=2)

# helper function to read data coming from arduino
# necessary as Serial read functions alone don't always capture all data properly
# see greenhouse-arduino/greenhouse-arduino.ino for a description of a similar function
def read_arduino():
    finished = False
    started = False
    i = 0
    raw = [0, 0]

    while (not finished):
        b = arduino.read()

        if started:
            if b != b'\xFF':
                raw[i] = b
                i += 1
                if i > 1:
                    i = 1
            else:
                started = False
                finished = True
                i = 0
        elif b == b'\xFE':
            started = True

    return raw[0] + raw[1]

graph_time = 60 # add a new graph entry every 60 seconds
last_graph = 0 # timestamp of last graph entry

last_conf = b'' # keep track of last configuration sent

while True:
    if time.time() - last_graph >= graph_time:
        raw = read_arduino()
        output = decode_output(raw)
        last_graph = time.time()
        add_graph_entry(int(last_graph), output["temperature"], output["humidity"], output["error"])

    new_conf = b'\xFE' + encode_input(get_arduino_conf()) + b'\xFF'
    if new_conf != last_conf:
        arduino.write(new_conf)
        last_conf = new_conf
    
    time.sleep(0.5)
