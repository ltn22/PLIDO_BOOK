import CoAP
import socket

SERVER = "192.168.1.XX" # change to your server's IP address
PORT   = 5683

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

coap = CoAP.Message()
coap.new_header()
coap.dump(hexa=True)

s.settimeout(10)
s.sendto (coap.to_byte(), (SERVER, 5683))

resp,addr = s.recvfrom(2000)
answer = CoAP.Message(resp)
answer.dump(hexa=True)
