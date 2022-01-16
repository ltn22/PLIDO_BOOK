"""
This program runs on Python3 in terminal mode and Lopy4. On LoPy4, it sends
information either on LoRaWAN Networks, Sigfox or Wi-Fi. Selection is done
with the variable SERVER (see below). If a BME280 is connected to the LoPY,
measurement are taken from the sensor, otherwise sensor's behavior is emulated.
On python terminal values are emulated.

Data are sent with CoAP on 4 different URI /temperature, /pressure, /humidity,
/memory. On Sigfox, the SCHC compression of the CoAP header is provided and only
one parameter is sent (it can be changed in the code). On LoRaWAN and Wi-Fi all
the parameters are sent on a full CoAP message. Downlink is limited to error
messages (4.xx and 5.xx) and not taken into account by the program.

"""
#SERVER = "LORAWAN" # change to your server's IP address, or SIGFOX or LORAWAN
#SERVER="SIGFOX"
SERVER = "192.168.1.XX" # change to your server's IP address, or SIGFOX or LORAWAN
PORT   = 5683
destination = (SERVER, PORT)

import CoAP
import socket
import time
import sys
import binascii
upython = (sys.implementation.name == "micropython")
print (upython, sys.implementation.name)
if upython:
    import kpn_senml.cbor_encoder as cbor #pycom
    import pycom
    import gc
    import struct
else:
    import cbor2 as cbor  # terminal on computer
    import psutil

#----- CONNECT TO THE APPROPRIATE NETWORK --------



sigfox = False
if SERVER == "LORAWAN":
    from network import LoRa

    lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
    #
    mac = lora.mac()
    print ('devEUI: ',  binascii.hexlify(mac))

    # create an OTAA authentication parameters
    app_eui = binascii.unhexlify('0000000000000000'.replace(' ',''))
    app_key = binascii.unhexlify('11223344556677881122334455667788'.replace(' ',''))   # Acklio
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key),  timeout=0)

    pycom.heartbeat(False) # turn led to white
    pycom.rgbled(0x101010) # white

    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
        print('Not yet joined...')

    pycom.rgbled(0x000000) # black

    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
    s.setsockopt(socket.SOL_LORA,  socket.SO_CONFIRMED,  False)

    MTU = 200 # Maximun Transmission Unit, for DR 0 should be set to less than 50

elif SERVER == "SIGFOX":
    from network import Sigfox

    # initalise Sigfox for RCZ1 (You may need a different RCZ Region)
    sfx = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
    s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)

    MTU = 12
    print ("SIGFOX", binascii.hexlify(sfx.id()))
    sigfox = True

else: # WIFI with IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MTU = 200 # maximum packet size, could be higher

# ------------------ TRY TO GET BME280 ---------------

if upython: # LOPY
    from machine import I2C
    import BME280

    i2c = I2C(0, I2C.MASTER, baudrate=400000)
    print ("_i2c")
    devices = i2c.scan()
    print (devices)
    if 118 in devices: # found a BME
        bme = BME280.BME280(i2c=i2c)
        use_BME=True

    else: # virtualize sensors
        import virtual_sensor
        use_BME = False

else: # computer
    import virtual_sensor
    use_BME = False

print ("use BME", use_BME)

if not use_BME:
    print ("Send emulated data")
    temperature = virtual_sensor.virtual_sensor(start=20, variation = 0.1)
    pressure    = virtual_sensor.virtual_sensor(start=1000, variation = 1)
    humidity    = virtual_sensor.virtual_sensor(start=30, variation = 3, min=20, max=80)
else:
    print ("Send real measurements")

# the following fonction are able to call either the emulator or the BME to return
# values.

def get_temperature():
    if use_BME:
        return bme.read_temperature()
    else:
        return temperature.read_value()

def get_pressure():
    if use_BME:
        return bme.read_pressure()
    else:
        return pressure.read_value()

def get_humidity():
    if use_BME:
        return bme.read_humidity()
    else:
        return humidity.read_value()

def get_memory():
    if upython:
        gc.collect()
        return gc.mem_free()
    else:
        return psutil.virtual_memory().available


# ------------- SENDING DATA ------------------------

REPORT_PERIOD = 60 # send a frame every 60 sample (1 hour)

# Offset are used to desynchronize sendings, and the value is != form 0
# at the first round, after the first sending offset is set to 0, but since
# buffers have different filling level, the desynchronization is kept. In the
# default configuration, one message is sent every 15 minutes.

temperature_offset = 0
pressure_offset = REPORT_PERIOD // 4 # desynchronize sending
humidity_offset = 2*REPORT_PERIOD // 4
memory_offset = 3*REPORT_PERIOD // 4

print ("OFFSET", temperature_offset, pressure_offset, humidity_offset, memory_offset)

t_prev = 0
p_prev = 0
h_prev = 0
m_prev = 0

temp_ts = []
pres_ts = []
humi_ts = []
memo_ts = []

sigfox_MID = 1 # when SCHC is used for Sigfox
def send_coap_message(sock, destination, uri_path, message):
    if destination[0] == "SIGFOX": # do SCHC compression
        global sigfox_MID

        """ SCHC compression for Sigfox, use rule ID 0 stored on 2 bits,
        followed by MID on 4 bits and 2 bits for an index on Uri-path.

        the SCHC header is RRMMMMUU
        """
        uri_idx = ['temperature', 'pressure', 'humidity', 'memory'].index(uri_path)

        schc_residue = 0x00 # ruleID in 2 bits RR
        schc_residue |= (sigfox_MID << 2) | uri_idx # MMMM and UU

        sigfox_MID += 1
        sigfox_MID &= 0x0F # on 4 bits
        if sigfox_MID == 0: sigfox_MID = 1 # never use MID = 0

        msg = struct.pack("!B", schc_residue) # add SCHC header to the message
        msg += cbor.dumps(message)

        print ("length", len(msg), binascii.hexlify(msg))

        s.send(msg)
        return None # don't use downlink

    # for other technologies we wend a regular CoAP message
    coap = CoAP.Message()
    coap.new_header(type=CoAP.NON, code=CoAP.POST)
    coap.add_option (CoAP.Uri_path, uri_path)
    coap.add_option (CoAP.Content_format, CoAP.Content_format_CBOR)
    coap.add_option (CoAP.No_Response, 0b00000010) # block 2.xx notification
    coap.add_payload(cbor.dumps(message))
    coap.dump(hexa=True)
    answer = CoAP.send_ack(s, destination, coap)

    return answer

if destination[0] == "SIGFOX":
    coap_header_size = 1 # SCHC header size
else:
    coap_header_size = 25 #  coap header size approximated

print ("MTU size is", MTU, "Payload size is", MTU-coap_header_size, "samples ", REPORT_PERIOD)

# lets run it forever
while True:
    t = int(get_temperature()*100)
    p = int(get_pressure()*100)
    h = int(get_humidity()*100)
    m = get_memory()

    print (t, p, h, m)

    # if the array is empty store the value, otherwise store the delta

    # for sigfox, we just measure temperature, other array will stay empty and
    # never sent
    if len(temp_ts) == 0:
        temp_ts.append(t)
    else:
        temp_ts.append(t - t_prev)
    t_prev = t

    if not sigfox:
        if len(pres_ts) == 0:
            pres_ts.append(p)
        else:
            pres_ts.append(p - p_prev)
        p_prev = p

        if len(humi_ts) == 0:
            humi_ts.append(h)
        else:
            humi_ts.append(h - h_prev)
        h_prev = h

        if len(memo_ts) == 0:
            memo_ts.append(m)
        else:
            memo_ts.append(m - m_prev)
        m_prev = m

    print ("temperature", len(cbor.dumps(temp_ts)), len(temp_ts), temp_ts)
    print ("pressure   ", len(cbor.dumps(humi_ts)), len(humi_ts), humi_ts)
    print ("humidity   ", len(cbor.dumps(pres_ts)), len(pres_ts), pres_ts)
    print ("memory     ", len(cbor.dumps(memo_ts)), len(memo_ts), memo_ts)

    answer = False

    # if we exceed the MTU size, then remove the last item, send and generate
    # a new list with the value we have removed. This is used mainly by SIGFOX
    # since the MTU is too short to store 60 samples.
    if len(cbor.dumps(temp_ts)) > MTU-coap_header_size: # room for CoAP header
        answer = send_coap_message(s, destination, "temperature", temp_ts[:-1])
        temp_ts=[t]

    if len(cbor.dumps(pres_ts)) > MTU-coap_header_size: # room for CoAP header
        answer = send_coap_message(s, destination, "pressure", pres_ts[:-1])
        pres_ts=[p]

    if len(cbor.dumps(humi_ts)) > MTU-coap_header_size:
        answer = send_coap_message(s, destination, "humidity", humi_ts[:-1])
        humi_ts=[h]

    if len(cbor.dumps(memo_ts)) > MTU-coap_header_size:
        answer = send_coap_message(s, destination, "memory", memo_ts[:-1])
        memo_ts=[m]

    # if the number of sample exceed the limit we defined, send the full
    # array and start again with an empty one.

    if len(temp_ts) + temperature_offset > REPORT_PERIOD:
        answer = send_coap_message(s, destination, "temperature", temp_ts)
        temp_ts = []
        temperature_offset = 0

    if len(pres_ts) + pressure_offset > REPORT_PERIOD:
        answer = send_coap_message(s, destination, "pressure", pres_ts)
        pres_ts = []
        pressure_offset = 0

    if len(humi_ts) + humidity_offset > REPORT_PERIOD:
        answer = send_coap_message(s, destination, "humidity", humi_ts)
        humi_ts = []
        humidity_offset = 0

    if len(memo_ts) + memory_offset > REPORT_PERIOD:
        answer = send_coap_message(s, destination, "memory", memo_ts)
        memo_ts = []
        memory_offset = 0

    time.sleep (60) # wait for 1 minute.
