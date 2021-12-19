import cbor2 as cbor

for i in range (1, 10):
    c = cbor.dumps("LoRaWAN"*i)

    print ("{0:3} {1}".format(i, c.hex()))

bs = cbor.dumps(b"\x01\x02\x03")
print (bs.hex())


