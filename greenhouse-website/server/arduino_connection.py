# import serial
import sys

from struct import pack

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

# arduino = serial.Serial(port="COM0", baudrate=9600, timeout=1)
last = 0

# return output and push buffer
# output = arduino.readline()
output = pack('i', 0x3F65) # false, 31.5, 50.5.  0/011_1111/_0110_0101
sys.stdout.buffer.write(output)
sys.stdout.flush()

while last == 0:
    # get input and post to arduino
    last = sys.stdin.readline()
    # arduino.write(last)
