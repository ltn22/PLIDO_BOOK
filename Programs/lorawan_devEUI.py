from network import LoRa
import pycom
import binascii
#
lora = LoRa(mode=LoRa.LORAWAN)
mac = lora.mac()
#
print ('devEUI: ',  binascii.hexlify(mac))
#
