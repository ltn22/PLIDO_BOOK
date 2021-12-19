import cbor2 as cbor

c1 = {"type" : "hamster",
      "taille" : 300,
      2 : "test",
      0x0F: 0b01110001,
      2 : "program"};

print (cbor.dumps(c1).hex())


