import sys
import socket
import threading
import time
import queue

import logging
import logging.handlers

logger = logging.getLogger('tcp_socket_client')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch_formatter = logging.Formatter(
    '[%(asctime)s - %(name)s - %(levelname)s - %(lineno)s] %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

RECV_BUF_SIZE = 2048    # set socket buffer size


class TcpSocketClient():
    def __init__(self, host, port, send_queue, recv_queue):
        logger.info('Client start')

        self.__host = host
        self.__port = port
        self.__send_queue = send_queue
        self.__recv_queue = recv_queue

        self.__send_thread = threading.Thread(
            target=self.__send_woker, args=())
        self.__send_thread.daemon = True
        self.__send_thread.start()

        self.__recv_thread = threading.Thread(
            target=self.__recv_woker, args=())
        self.__recv_thread.daemon = True
        self.__recv_thread.start()

    def __make_connection(self):
        logger.info('Make connection to {0}:{1}'.format(
            self.__host, self.__port))
        while True:
            try:
                soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                soc.connect((self.__host, self.__port))
                logger.info('Connect to {0}:{1}'.format(
                    self.__host, self.__port))
                return soc
            except socket.error:
                time.sleep(0.5)

    def __send_woker(self):
        while True:
            data = self.__send_queue.get()
            try:
                self.__soc.send(data)
                logger.info('Send: {}'.format(data))
            except:
                logger.info(sys.exc_info())

    def __recv_woker(self):
        self.__soc = self.__make_connection()
        while True:
            try:
                split_data = self.__soc.recv(RECV_BUF_SIZE).splitlines()
                for data in split_data:
                    if len(data) != 0:
                        self.__recv_queue.put(data)
                        logger.info('Recv: {0} from {1}:{2}'.format(
                            data, self.__host, self.__port))
                    else:
                        self.__soc.close()
                        self.__soc = self.__make_connection()
            except:
                logger.info(sys.exc_info())


if __name__ == '__main__':
    def test_send_woker(send_q):
        while True:
            msg = input()
            send_data = msg.encode('utf-8')
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

    tcp_client = TcpSocketClient(host, port, send_q, recv_q)

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
