#!/usr/bin/env python3

# This file is part of the Python aiocoap library project.
#
# Copyright (c) 2012-2014 Maciej Wasilak <http://sixpinetrees.blogspot.com/>,
#               2013-2014 Christian Amsüss <c.amsuess@energyharvesting.at>
#
# aiocoap is free software, this file is published under the MIT license as
# described in the accompanying LICENSE file.

"""This is a usage example of aiocoap that demonstrates how to implement a
simple server. See the "Usage Examples" section in the aiocoap documentation
for some more information."""

import datetime
import logging
import socket

import asyncio

import aiocoap.resource as resource
import aiocoap

class TimeResource(resource.Resource):

    async def render_get(self, request):
        await asyncio.sleep(5)

        payload = datetime.datetime.now().\
                strftime("%Y-%m-%d %H:%M").encode('ascii')
        return aiocoap.Message(payload=payload)

# logging setup

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

def main():
    # Resource tree creation
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80)) # connect outside to get local IP address
        ip_addr = s.getsockname()[0]

    port = 5683
    print ("server running on ", ip_addr, "at port", port)

    root = resource.Site()

    root.add_resource(['time'], TimeResource())

    asyncio.Task(
        aiocoap.Context.create_server_context(root, 
                                    bind=(ip_addr, port)))

    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
