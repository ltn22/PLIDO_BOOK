from network import Sigfox
import binascii
import socket

# initalise Sigfox for RCZ1 (You may need a different RCZ Region)
# RCZ1: Europe, Oman, South Africa
# RCZ2: USA, Mexico, Brazil
# RCZ3: Japan
# RCZ4: Australia, New Zealand, Singapore, Taiwan, Hong Kong, Columbia, Argentina
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)

# print Sigfox Device ID
print("Sigfox ID:", binascii.hexlify(sigfox.id()))

# print Sigfox PAC number
print("PAC Number:", binascii.hexlify(sigfox.pac()))

s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
s.send("Hi! Sigfox")
