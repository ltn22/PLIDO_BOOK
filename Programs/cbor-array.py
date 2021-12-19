import cbor2 as cbor

c1 = cbor.dumps([1,2,3,4])
print (c1.hex())
print ()

c2 = cbor.dumps([1,[2, 3], 4])
print (c2.hex())
print()

c3 = cbor.dumps([1000, +20, -10, +100, -30, -50, 12])
print (c3.hex())


