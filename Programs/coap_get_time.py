import CoAP
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


coap = CoAP.Message()
coap.new_header()
coap.new_header(code=CoAP.GET, mid=0xF001)
coap.add_option(CoAP.Uri_path, "time")
coap.dump()

s.settimeout(10)
s.sendto (coap.to_byte(), ("192.168.1.77", 5683))

resp,addr = s.recvfrom(2000)
answer = CoAP.Message(resp)
answer.dump()

s.settimeout(10)
resp,addr = s.recvfrom(2000)
answer = CoAP.Message(resp)
answer.dump()
