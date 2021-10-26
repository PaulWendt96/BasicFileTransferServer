import argparse
import logging
import socket
import selectors
from collections import deque
import os
import types
from stream import break_stream
from tar import get_tar_bytes

'''
Basic async file transfer server

Usage:

    python server.py [-h] [-host HOST] [-port PORT] 
                     [--log DEBUG|INFO|WARNING|ERROR|CRITICAL] 

'''

class EventLoop:
    def __init__(self):
        self.tasks = deque([])
        self.sel = selectors.DefaultSelector()
        self.stop = False

    def create_task(self, coro):
        self.tasks.append(coro)

    def run(self):
        '''
        Run the event loop

        The event loop maintains a FIFO queue to track tasks it needs
        to run. If there are tasks in its FIFO, the event loop will 
        pop the oldest task, run it, and dispatch on its result. 

        If there are no tasks left in the FIFO, the event loop will 
        wait for select(). In this case, select() is used to determine
        when a socket is ready to be read or written. When select()
        returns, the task corresponding to the select() will be added
        to the FIFO for further processing. 
        '''
        while not self.stop:
            if self.tasks:
                task = self.tasks.popleft()
                try:
                    op, arg = task.send(None)
                except StopIteration:
                    continue

                if op == 'wait_read':
                    self.sel.register(arg, selectors.EVENT_READ, task)
                elif op == 'wait_write':
                    self.sel.register(arg, selectors.EVENT_WRITE, task)
                elif op == 'stop':
                    self.stop = True
                else:
                    raise ValueError('Unknown event loop operation')
            else:
                for key, _ in self.sel.select():
                    task = key.data
                    sock = key.fileobj
                    self.sel.unregister(sock)
                    self.create_task(task)

async def run_server(host, port, size=4096):
    '''
    Run the server. Wait for incoming connections and defer them
    to handle_client() for further handling
    '''
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen()
    while True:
        client_sock, addr = await async_accept(sock)
        logging.info('Connection from {}'.format(addr))
        loop.create_task(handle_client(client_sock, size))

@types.coroutine
def async_accept(sock):
    '''
    Yield wait_read here, since we expect the client to send its request first
    '''
    yield 'wait_read', sock
    return sock.accept()

@types.coroutine
def async_recv(sock, bytes):
    yield 'wait_read', sock
    return sock.recv(bytes)

@types.coroutine
def async_send(sock, data):
    yield 'wait_write', sock
    logging.info('server.py: sending {} bytes of data'.format(len(data)))
    logging.debug('server.py: sending {}'.format(data))
    sock.sendall(data)

@types.coroutine
def async_send_stop():
    yield 'stop', None

async def handle_client(sock, size=4096):
    '''
    Per-client handling loop

    The server begins by awaiting the client's request. The loop
    dispatches on this request. 

    As this is a file transfer server, the request will most often involve
    a transfer of a file or folder. In the case of a file, the loop
    will read the requested file's data as bytes, break those bytes
    up into a stream via break_stream(), and send the data

    Folders are a little trickier. In order to make things as straightforward
    as possible, folders are sent as a tarball (obtained via a call to 
    get_tar_bytes()). The tarball created via get_tar_bytes() is represented
    as bytes in memory; no temporary files are involved. Once the loop 
    has the tarball, it is sent in the same way as a file

    In the case of an error, the loop sends a basic error message
    '''
    while True:
        data = await async_recv(sock, size)
        if not data:
            break
        elif data == b'stop':
            logging.info('stopping...')
            loop.stop = True
        else:
            logging.debug('server.py: client requested file')
            path = data.decode('utf-8')
            if os.path.isfile(path):
                with open(path, 'rb') as file:
                    contents = file.read()
                packets = break_stream(contents, size)
                for packet_contents, packet_size, packets_remaining in packets:
                    await async_send(sock, packet_contents)
            elif os.path.isdir(path):
                logging.debug('server.py: client requested directory')
                contents = get_tar_bytes(path)
                packets = break_stream(contents, size)
                for packet_contents, packet_size, packets_remaining in packets:
                    await async_send(sock, packet_contents)
            else:
                error_message = 'error -- file {} not found'.format(path)
                await async_send(sock, error_message.encode('utf-8'))

    logging.info('client at {} disconnected'.format(sock.getpeername()))
    sock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Server script for basic file ' \
                         'transfer over host or local network')
    parser.add_argument('-host', help='IPv4 host address of server',
                                 type=str, 
                                 default='localnet')
    parser.add_argument('-port', type=int, 
                                 help='Port', 
                                 default=5000)
    parser.add_argument('--log', type=str, 
                                 help='Logging mode', 
                                 default='info')
    args = parser.parse_args()
    args = vars(args)

    HOST = args['host']
    if HOST == 'localhost':
        HOST = '127.0.0.1'
    elif HOST == 'localnet':
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        HOST = local_ip

    PORT = args['port']

    loglevel = args['log']
    level = getattr(logging, loglevel.upper())
    logging.basicConfig(level=level)

    logging.info('Running server on {}, port {}'.format(HOST, PORT))
    loop = EventLoop()
    loop.create_task(run_server(HOST, PORT))
    loop.run()
