import CoAP
import socket
import time
try:
    import kpn_senml.cbor_encoder as cbor #pycom
except:
    import cbor2 as cbor  # terminal on computer

SERVER = "192.168.1.77" # change to your server's IP address
PORT   = 5683
destination = (SERVER, PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

coap = CoAP.Message()
coap.new_header(type=CoAP.NON, code=CoAP.POST)
coap.add_option (CoAP.Uri_path, "temp")
coap.add_option (CoAP.Content_format, CoAP.Content_format_CBOR)
coap.add_option (CoAP.No_Response, 0b00000010)
coap.add_payload(cbor.dumps(23.5))
coap.dump()

answer = CoAP.send_ack(s, destination, coap)
if answer != None:
    answer.dump()
else:
    answer = CoAP.get_msg(s)
    if answer != None:
        answer.dump()
