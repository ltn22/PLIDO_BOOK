import socket
import binascii

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 33033))

while True:
    data, addr = s.recvfrom(1500)
    print (data)
    s.sendto("Pleased to meet you!".encode(), addr)