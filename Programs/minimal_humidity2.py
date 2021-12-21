from virtual_sensor import virtual_sensor 
import time
import socket
import cbor2 as cbor

humidity = virtual_sensor(start=30, variation = 3, min=20, max=80) 
 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
NB_ELEMENT = 30
h_history = []

while True:

    h = int(humidity.read_value()*100)

    # No more room to store value, send it.
    if len(h_history) == 0:
        h_history = [h]
    elif len(h_history) >= NB_ELEMENT:
        print ("send")
        s.sendto (cbor.dumps(h_history), ("127.0.0.1", 33033))
        h_history = [h]
    else:
        h_history.append(h-prev)

    prev = h

    print (len(h_history), len(cbor.dumps(h_history)), h_history)

    time.sleep(10)