import cbor2 as cbor

v = -1

for i in range (0, 19):
    c = cbor.dumps(v)
    print ("{0:3} {1:30} {2}".format(i, v, c.hex()))

    v *= 10
