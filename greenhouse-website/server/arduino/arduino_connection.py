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

def read(arduino) -> bytes:
    # output = arduino.readline()
    output = pack('i', 0x3F65) # false, 31.5, 50.5.  0/011_1111/_0110_0101
    return output

def write(x: bytes, arduino) -> None:
    arduino.write(x)

arduino = serial.Serial(port="COM0", baudrate=9600, timeout=2)

graph_time = 60 # add a new graph entry every 60 seconds
last_graph = 0

while True:
    if time.time - last_graph >= graph_time:
        output = decode_output(read(arduino))
        last_graph = time.time
        add_graph_entry(last_graph, output["temperature"], output["humidity"], output["error"])

    ardu_conf = encode_input(get_arduino_conf())
    write(ardu_conf, arduino)
    
    time.sleep(0.5)




