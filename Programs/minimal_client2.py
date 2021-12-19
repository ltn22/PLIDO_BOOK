from virtual_sensor import virtual_sensor 
import time
import socket

temperature = virtual_sensor(start=20, variation = 0.1)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    t = temperature.read_value()

    s.sendto (str(t).encode(), ("127.0.0.1", 33033))
    time.sleep(10)