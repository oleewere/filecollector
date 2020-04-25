import argparse
import sys
import os
import yaml
import SimpleHTTPServer
import SocketServer

def parse_args():
    parser = argparse.ArgumentParser(
        description='Python script to serve simple file server for collected logs')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to logcollector configuration')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    with open(args.config) as file:
        config = yaml.load(file, yaml.SafeLoader)
        if "server" in config:
            port = int(config["server"]["port"])
            folder = str(config["server"]["folder"])
            if folder:
                web_dir = os.path.join(os.path.dirname(__file__), folder)
                os.chdir(web_dir)
            Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
            httpd = SocketServer.TCPServer(("", port), Handler)
            print "serving at port", port
            httpd.serve_forever()

if __name__ == "__main__":
    main()