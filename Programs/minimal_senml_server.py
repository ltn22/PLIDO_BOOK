import socket
import pprint
import binascii
import pprint
import cbor2 as cbor

import beebotte
import config_bbt #secret keys

naming_map = {'bn': -2, 'bt': -3, 'bu': -4, 'bv': -5, 'bs': -16,
                      'n': 0, 'u': 1, 'v': 2, 'vs': 3, 'vb': 4, 
                      'vd': 8, 's': 5, 't': 6, 'ut': 7}

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 33033))

bbt = beebotte.BBT(config_bbt.API_KEY, config_bbt.SECRET_KEY)


while True:
    data, addr = s.recvfrom(1500)

    sml_data = cbor.loads(data)

    sml_record = {}
    bbt_record = []

    for e in sml_data:
        sml_record = {**sml_record, **e} # merge dict
        print (sml_record)

        ts =  sml_record[naming_map["t"]]
        if naming_map["bt"] in sml_record:
            ts += sml_record[naming_map["bt"]]

        res = sml_record[naming_map["n"]]

        data = sml_record[naming_map["v"]]
        if naming_map["bv"] in sml_record:
            data += sml_record[naming_map["bv"]]


        bbt_record.append({"resource" : res, "data": data, "ts": ts*1000})

    pprint.pprint (bbt_record)
    channel = sml_record[naming_map["bn"]]
    bbt.writeBulk(channel, bbt_record)




