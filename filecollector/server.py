#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#
import argparse
import sys
import os
import yaml
from pid import PidFile

def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Python script to serve simple file server for collected logs')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to logcollector configuration')
    args = parser.parse_args(args)
    return args

def main(args):
    args = parse_args(args)
    with open(args.config) as file:
        config = yaml.load(file, yaml.SafeLoader)
        if config and "server" in config:
            port = int(config["server"]["port"])
            folder = str(config["server"]["folder"])
            if folder:
                web_dir = os.path.join(os.path.dirname(__file__), folder)
                os.chdir(web_dir)
            try:
                import http.server
                import socketserver
                handler = http.server.SimpleHTTPRequestHandler
                httpd = socketserver.TCPServer(("", port), handler)
                print("serving at port", port)
                httpd.serve_forever()
            except ImportError as error:
                import SimpleHTTPServer
                import SocketServer
                Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
                httpd = SocketServer.TCPServer(("", port), Handler)
                print ("serving at port", port)
                httpd.serve_forever()

if __name__ == "__main__":
    pidfile=os.environ.get('FILECOLLECTOR_PIDFILE', 'filecollector-server.pid')
    with PidFile(pidfile) as p:
        main(sys.argv[1:])