from network import LoRa
import socket
import time
import pycom
import binascii

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
#
mac = lora.mac()
print ('devEUI: ',  binascii.hexlify(mac))

# create an OTAA authentication parameters
app_eui = binascii.unhexlify(
                    '00 00 00 00 00 00 00 00'.replace(' ','') )

app_key = binascii.unhexlify(
            '4EAE56D0689F6F8B02C2AFA7E08DADBA'.replace(' ','') )

pycom.heartbeat(False)
pycom.rgbled(0x101010) # white

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key),  timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

pycom.rgbled(0x000000) # black

s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setsockopt(socket.SOL_LORA,  socket.SO_CONFIRMED,  False)

while True:
    pycom.rgbled(0x100000) # red
    s.setblocking(True)
    s.settimeout(10)

    try:
        s.send('Hello LoRa')
    except:
        print ('timeout in sending')

    pycom.rgbled(0x000010) # blue

    try:
        data = s.recv(64)

        print(data)
        pycom.rgbled(0x001000) # green
    except:
        print ('timeout in receive')
        pycom.rgbled(0x000000) # black


    s.setblocking(False)
    time.sleep (29)
