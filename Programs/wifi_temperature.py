import BME280
import time
import socket
import kpn_senml.cbor_encoder as cbor
from machine import I2C


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
NB_ELEMENT = 30
t_history = []

i2c = I2C(0, I2C.MASTER, baudrate=400000)
print (i2c.scan())

bme = BME280.BME280(i2c=i2c)

while True:

    t = int(bme.read_temperature()*100)

    # No more room to store value, send it.
    if len(t_history) == 0:
        t_history = [t]
    elif len(t_history) >= NB_ELEMENT:
        print ("send")
        s.sendto (cbor.dumps(t_history), ("192.168.1.47", 33033))
        t_history = [t]
    else:
        t_history.append(t-prev)

    prev = t

    print (len(t_history), len(cbor.dumps(t_history)), t_history)

    time.sleep(10)
