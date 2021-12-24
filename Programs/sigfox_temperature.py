import BME280
import time
import socket
import kpn_senml.cbor_encoder as cbor
from machine import I2C
from network import Sigfox
import binascii
import socket

# initalise Sigfox for RCZ1 (You may need a different RCZ Region)
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)

FRAME_MAX = 12
t_history = []

i2c = I2C(0, I2C.MASTER, baudrate=400000)
print (i2c.scan())
bme = BME280.BME280(i2c=i2c)

while True:

    t = int(bme.read_temperature()*100)

    # No more room to store value, send it.
    if len(t_history) == 0:
        t_history = [t]
    else:
        t_history.append(t-prev)

    print (t_history, len(cbor.dumps(t_history)))


    if len(cbor.dumps(t_history)) > FRAME_MAX:
        # oops too big for Sigfox
        t_history = t_history[:-1] # remove last item
        s.send (cbor.dumps(t_history))
        t_history = [t]

    prev = t

    time.sleep(10)
