import asyncio
import threading
import queue

import logging
import logging.handlers

logger = logging.getLogger('tcp_socket_server')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch_formatter = logging.Formatter(
    '[%(asctime)s - %(name)s - %(levelname)s - %(lineno)s] %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)


class TcpProtocol(asyncio.Protocol):
    def __init__(self, server):
        self.__server = server

    def connection_made(self, transport):
        self.transport = transport

        peername = self.transport.get_extra_info('peername')
        logger.info('Connection from {}'.format(peername))
        self.__server.add_client(self)

    def connection_lost(self, exc):
        peername = self.transport.get_extra_info('peername')
        logger.info('Close from {}'.format(peername))
        self.transport.close()
        self.__server.remove_client(self)

    def data_received(self, data):
        peername = self.transport.get_extra_info('peername')
        logger.info('Recv: {0} from {1}'.format(data, peername))
        self.__server.recv_data(data)

    def send_data(self, data):
        logger.info('Send: {}'.format(data))
        self.transport.write(data)


class TcpSocketServer():
    def __init__(self, host, port, send_queue, recv_queue):
        logger.info('Server start')

        self.__host = host
        self.__port = port
        self.__send_queue = send_queue
        self.__recv_queue = recv_queue
        self.__clients = []

        self.__ev_loop = asyncio.get_event_loop()
        self.__coroutine = self.__ev_loop.create_server(
            lambda: TcpProtocol(self), host, port)

        self.__tcp_protocol_thread = threading.Thread(
            target=self.__tcp_protocol_woker, args=())
        self.__tcp_protocol_thread.daemon = True
        self.__tcp_protocol_thread.start()

        self.__send_woker_thread = threading.Thread(
            target=self.__send_woker, args=())
        self.__send_woker_thread.daemon = True
        self.__send_woker_thread.start()

    def add_client(self, client):
        self.__clients.append(client)

    def remove_client(self, client):
        self.__clients.remove(client)

    def recv_data(self, data):
        if self.__recv_queue is not None:
            self.__recv_queue.put(data)

    def __send_woker(self):
        while True:
            data = self.__send_queue.get()
            for client in self.__clients:
                client.send_data(data)

    def __tcp_protocol_woker(self):
        self.__ev_loop.run_until_complete(self.__coroutine)
        self.__ev_loop.run_forever()
        self.__ev_loop.close()


if __name__ == '__main__':
    def test_send_woker(send_q):
        while True:
            message = input()
            send_data = message.encode('utf-8')
            send_q.put(send_data)

    def test_recv_woker(recv_q):
        while True:
            try:
                recv_data = recv_q.get()
                print(recv_data.decode('utf-8'))
            except queue.Empty:
                pass

    import time

    host = 'localhost'
    port = 5000

    send_q = queue.Queue()
    recv_q = queue.Queue()

    tcp_server = TcpSocketServer(host, port, send_q, recv_q)

    send_thread = threading.Thread(target=test_send_woker, args=(send_q,))
    send_thread.daemon = True
    send_thread.start()

    recv_thread = threading.Thread(target=test_recv_woker, args=(recv_q,))
    recv_thread.daemon = True
    recv_thread.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print('\n')
