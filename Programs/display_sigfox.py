import requests
import os
from requests.auth import HTTPBasicAuth
import pprint
import json
from config_sigfox import API_USER, API_PASSWORD, DEVICEID
import binascii
import time
import datetime
import cbor2 as cbor
import beebotte
import config_bbt

bbt = beebotte.BBT(config_bbt.API_KEY, config_bbt.SECRET_KEY)

def to_bbt(channel, res_name, cbor_msg, factor=1, period=10, epoch=None):
    global bbt
    
    prev_value = 0
    data_list = []
    if epoch:
        back_time = epoch
    else:
        back_time = time.mktime(datetime.datetime.now().timetuple())*1000
    
    back_time -= len(cbor_msg)*period

    for e in cbor_msg:
        prev_value += e
        
        back_time += period

        data_list.append({"resource": res_name,
                          "data" : prev_value*factor,
                          "ts": back_time} )

    pprint.pprint (data_list)
    
    bbt.writeBulk(channel, data_list)

url = 'https://backend.sigfox.com/api/v2/devices/'+DEVICEID+'/messages'
last_epoch = 0

# get the last message to find the starting epoch
parameters = {'limit': 1 }
r = requests.get(url, auth=HTTPBasicAuth(API_USER, API_PASSWORD), 
                    params=parameters)

print (r.status_code)
if r.status_code != 200:
    exit

j = json.loads(r.text)
last_epoch = j["data"][0]["time"]

# delay next request to avoid 429 status error
time.sleep(10)

# look periodically if new data arrived. 
while True:
    if last_epoch > 0:
        parameters = {"since": last_epoch+1}
    else:
        parameters = None

    print (parameters)

    r = requests.get(url, auth=HTTPBasicAuth(API_USER, API_PASSWORD), 
                        params=parameters)

    print (r.status_code)
    if r.status_code != 200:
        break

    resp = json.loads(r.text)

    for v in resp["data"]:
        if last_epoch < v["time"]:
            last_epoch = v["time"] 

        print ("{:10d}: {:2d} {:25} {:20} received {}".format(
            v["time"], v["seqNumber"], 
            v["data"], "["+str(binascii.unhexlify(v["data"]))+"]",
            len(v["rinfos"])
            ))

        measure = cbor.loads(binascii.unhexlify(v["data"]))
        sending_time = v["time"]
        print (sending_time, measure)
        to_bbt("capteurs", "temperature", measure, factor=0.01, 
                    period=10, epoch=sending_time)

    time.sleep(60)