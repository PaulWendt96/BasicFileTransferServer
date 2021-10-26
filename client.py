import argparse
import socket
import sys
import struct
import logging

'''
Simple async file transfer client

Usage: python client.py [-h] [-addr ADDR] [-port PORT] [-size SIZE]
                        [--log LOG] [--http_trailer HTTP_TRAILER] infile

While client.py is intended to be used with its brother, server.py, it can 
in fact be leveraged to send HTTP requests. For instance, 

  python client.py -addr 142.250.65.228 -port 80 --http_trailer True "GET / HTTP/1.0"

sends an HTTP GET request to www.google.com
'''

def send_request(infile, addr, port, size=4096):
    '''
    Send a request to the server and receive a reply. 
    The call to shutdown() indicates to the server that the request is fully sent.

    Similar to HTTP, the connection will break once the server sends the 
    requested file. As a result, send_request() leverages a while loop
    to read in bytes until the connection closes. This avoids thorny 
    networking issues that would crop up if the connection was persistent.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info('client.py: socket connecting to address {}, port {}'.format(addr, port))
    s.connect((addr, port))
    logging.info('client.py: sending message {} to server'.format(infile))
    s.send(infile.encode('utf-8'))
    s.shutdown(1)

    bytestring = b''
    while (response := s.recv(size)):
        logging.info('client.py: got {} bytes of data'.format(len(response)))
        logging.debug('client.py: received {}'.format(response))
        bytestring += response

    logging.debug('client.py: breaking')

    return bytestring


if __name__ == '__main__':
        parser = argparse.ArgumentParser(
                description='Client script for basic file transfer over host or local network')
        parser.add_argument('infile', type=str)
        parser.add_argument('-addr', help='IPv4 address of server', default='localnet')
        parser.add_argument('-port', type=int, help='Port of server', default=5000)
        parser.add_argument('-size', help='max buffer size for socket.recv()', type=int, default=8092)
        parser.add_argument('--log', type=str, help='Logging mode', default='WARNING')
        parser.add_argument('--http_trailer', type=bool, help='Add newline trailer for HTTP requests', default=False)
        args = parser.parse_args()
        args = vars(args)

        if not args['infile']:
            raise ValueError("Error -- client.py needs at least one file to request")

        infile = args['infile']
        ADDR = args['addr']
        if ADDR == 'localhost':
            ADDR = '127.0.0.1'
        elif ADDR == 'localnet':
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            ADDR = local_ip
        PORT = args['port']

        loglevel = args['log']
        level = getattr(logging, loglevel.upper())
        logging.basicConfig(level=level)

        size = args['size']

        logging.info('client.py: got arguments {}'.format(args))
        if args['http_trailer']:
            logging.info('client.py: adding HTTP trailer')
            infile += '\r\n\r\n'

        bytestring = send_request(infile, ADDR, PORT, size)
        sys.stdout.buffer.write(bytestring)
