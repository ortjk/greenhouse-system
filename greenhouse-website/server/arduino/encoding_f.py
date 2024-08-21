from struct import pack, unpack
from math import floor, ceil

# round a float to a binary representation of the form 0b...XXXXXXY, where:
# X is the n-bit binary whole number portion
# Y is a bit that adds one half
# e.g. 28.67 -> 111001 -> 28 + 0.5 -> 28.5
def round_with_half(num: float) -> tuple[int, int]:
    half = num % 0.5
    if num - floor(num) >= 0.5:
        if half > 0.25:
            # round up with no half
            half = 0
            num = int(ceil(num))
        else:
            # round down and add a half
            half = 1
            num = int(floor(num))
    else:
        if half > 0.25:
            # round down and add a half
            half = 1
            num = int(floor(num))
        else:
            # round down with no half
            half = 0
            num = int(floor(num))

    return num, half

# encode setpoints to a binary representation of the form 0bXXYY_YYYY_YZZZ_ZZZZ, where:
# X is the manual control override (enable and open)
# Y is the maximum temperature setpoint (max 63.5)
# Z is the minimum temperature setpoint (max 63.5)
def encode_input(x: dict) -> bytes:
    if x is None: 
        return None

    # set the enable and control bit
    manual_open = int(x["manual_open"]) << 14

    # set the open temperature 7 bits
    open_temp = float(x["open_temperature"]) # << 7
    open_temp, ho = round_with_half(open_temp)
    open_temp = ((open_temp << 1) | ho) << 7

    # set the close temperature 7 bits
    close_temp = float(x["close_temperature"])
    close_temp, hc = round_with_half(close_temp)
    close_temp = (close_temp << 1) | hc

    return pack('i', manual_open | open_temp | close_temp).removesuffix(b'\x00\x00')

# decode temperature, humidity, and status from a binary representation of the form 0bXYYY_YYYY_ZZZZ_ZZZZ, where:
# X is the error status
# Y is the binary representation of temperature (max 63.5)
# Z is the binary representation of humidity (max 127.5)
def decode_output(x: bytes) -> dict:
    x = int.from_bytes(x)

    # get error status bit
    status = (1 << 15) & x

    # get temperature int
    temperature = ((1 << 6) - 1) & (x >> 9)
    if bool((1 << 8) & x):
        temperature += 0.5

    humidity = ((1 << 7) - 1) & (x >> 1)
    if bool(1 & x):
        humidity += 0.5

    return {
        "error": bool(status),
        "temperature": temperature,
        "humidity": humidity,
        }
