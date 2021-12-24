import requests
import os
from requests.auth import HTTPBasicAuth
import pprint
import json
from config_sigfox import API_USER, API_PASSWORD, DEVICEID
import binascii

url = 'https://backend.sigfox.com/api/v2/devices/'+DEVICEID+'/messages'

print(url)

r = requests.get(url, auth=HTTPBasicAuth(API_USER, API_PASSWORD))
print (r.status_code)

if r.status_code != 200:
    exit

resp = json.loads(r.text)
pprint.pprint(resp)
for v in resp["data"]:
    print ("{:10d}: {:2d} {:25} {:20} received {}".format(
        v["time"], v["seqNumber"], 
        v["data"], "["+str(binascii.unhexlify(v["data"]))+"]",
        len(v["rinfos"])
        ))
