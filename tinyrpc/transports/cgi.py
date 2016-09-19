#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cgi extends the tinyrpc package.

The CGIServerTransport adds CGI as a supported server protocol that can be used
with the regular HTTP client.

(c) 2016, Leo Noordergraaf, Nextpertise BV
This code is made available under the same license as tinyrpc itself.
"""

from __future__ import print_function

import sys
import json
import urlparse

from . import ServerTransport

class CGIServerTransport(ServerTransport):
    """CGI transport.
    Reading stdin is blocking but, given that we've been called, something is
    waiting.  The transport accepts both GET and POST request.

    A POST request provides the entire JSON-RPC request in the body of the HTTP
    request.

    A GET request provides the elements of the JSON-RPC request in separate query
    parameters and only the params field contains a JSON object or array.
    i.e. curl 'http://server?jsonrpc=2.0&id=1&method="doit"&params={"arg"="something"}'
    """
    def receive_message(self):
        import cgi
        import cgitb
        cgitb.enable()

        request_json = sys.stdin.read()
        if request_json:
            # POST
            request_json = urlparse.unquote(request_json)
        else:
            # GET
            fields = cgi.FieldStorage()
            jsonrpc = fields.getfirst("jsonrpc")
            id = fields.getfirst("id")
            method = fields.getfirst("method")
            params = fields.getfirst("params")
            # Create request string
            request_json = json.dumps({
                'jsonrpc': jsonrpc,
                'id': id,
                'method': method,
                'params': params
            })
        return None, request_json


    def send_reply(self, context, reply):
        # context isn't used with cgi
        print("Content-Type: application/json")
        print("Cache-Control: no-cache")
        print("Pragma: no-cache")
        print("Content-Length: %d" % len(reply))
        print()
        print(reply)

