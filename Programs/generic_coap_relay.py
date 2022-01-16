#!/usr/bin/env python3

import sys
import argparse
from flask import Flask
from flask import request
from flask import Response
import pprint
import json
import binascii

import socket
import select
import time
import base64
import struct

import requests

import aiocoap.message
from aiocoap.numbers import POST, NON



app = Flask(__name__)
app.debug = True

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

defPort = 9999

def forward_data(payload):
    global verbose

    inputs = [sock]
    outputs = []

    if verbose:
        print ("--UP->", binascii.hexlify(payload))
    sock.sendto(payload, ("127.0.0.1", 5683))

    readable, writable, exceptional = select.select(inputs, outputs, inputs, 0.1)

    if readable == []:
        if verbose:
            print ("no DW")
        return None   

    for s in readable:
            replyStr = s.recv(1000)
            if verbose:
                print ("<-DW--", binascii.hexlify(replyStr))
            return replyStr

    return None


@app.route('/sigfox', methods=['POST'])
def get_from_sigfox():

    fromGW = request.get_json(force=True)
    print ("SIGFOX POST RECEIVED")
    pprint.pprint(fromGW)

    downlink = None
    if "data" in fromGW:
        payload = binascii.unhexlify(fromGW["data"])

        # Sigfox use SCHC compression, first byte is CoAP compressed header
        SCHC_byte = payload[0]

        ruleID = SCHC_byte >> 6
        mID = (SCHC_byte & 0b00111100) >> 2
        uri_idx = SCHC_byte & 0b0000_0011
        
        m = aiocoap.message.Message(
            mtype=NON,
            code=POST,
            mid=mID,
            payload=payload[1:]
            )
        m.opt.uri_path = (
            ["temperature", "pressure", "humidity", "memory"][uri_idx],
        )

        m.opt.content_format = 60
        m.opt.no_response = 0b0000_0010

        downlink = forward_data(m.encode())

    resp = Response(status=200)
    return resp                                    

@app.route('/TTN', methods=['POST'])
def get_from_TTN():
    fromGW = request.get_json(force=True)
    pprint.pprint(fromGW)

    downlink = None
    if "payload_raw" in fromGW:
        payload = base64.b64decode(fromGW["payload_raw"])
        downlink = forward_data(payload)

    if downlink != None:
        downlink_msg = {
            "dev_id": fromGW["dev_id"],    # The device ID
            "port":   fromGW["port"],      # LoRaWAN FPort
            "confirmed": False,            # Whether the downlink should be confirmed by the device
            "payload_raw": base64.b64encode(downlink).decode()     # Base64 encoded payload: [0x01, 0x02, 0x03, 0x04]
        }
        print (downlink_msg)
        x = requests.post(fromGW["downlink_url"], data = json.dumps(downlink_msg))

        print(x) 

    resp = Response(status=200)
    print (resp)
    return resp 

@app.route('/lns', methods=['POST'])
def get_from_acklio():

    fromGW = request.get_json(force=True)

    downlink = None
    if "data" in fromGW:
        payload = base64.b64decode(fromGW["data"])
        downlink = forward_data(payload)

    if downlink == None:
        resp = Response(status=200)
    else:
        answer = {
            "fPort" : fromGW["fPort"],
            "devEUI": fromGW["devEUI"],
            "data"  : base64.b64encode(downlink).decode('utf-8')
        }
        resp = Response(response=json.dumps(answer), 
                        status=200, 
                        mimetype="application/json")
    return resp

@app.route('/chirpstack', methods=['POST'])
def get_from_chirpstack():
    import chirpstack_secrets as secret

    fromGW = request.get_json(force=True)
    print (request.environ.get('REMOTE_PORT'))
    pprint.pprint (fromGW)

    downlink = None
    if "data" in fromGW:
        payload = base64.b64decode(fromGW["data"])
        downlink = forward_data(payload)

        print (fromGW["fPort"])
    if downlink != None:
        answer = {
            "deviceQueueItem": {
		            "data": base64.b64encode(downlink).decode('utf-8'),
                    "fPort": fromGW["fPort"],
            }
        }
        pprint.pprint (answer)
        device = binascii.hexlify(base64.b64decode(fromGW["devEUI"])).decode()
        downlink_url = secret.server+'/api/devices/'+device+'/queue'
        print (downlink_url)
        headers = {
            "content-type": "application/json",
            "grpc-metadata-authorization" : "Bearer "+ secret.key
        }
        print (headers)
        x = requests.post(downlink_url, data = json.dumps(answer), headers=headers)

        print(x) 


    resp = Response(status=200)         
    return resp


parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", 
                    action="store_true",
                    help="show uplink and downlink messages")

args = parser.parse_args()
verbose = args.verbose


app.run(host="0.0.0.0", port=defPort)



