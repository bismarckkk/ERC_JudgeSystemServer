from server import UdpServer
from multiprocessing import Queue
import time
import os





if __name__ == '__main__':
    queue = Queue(maxsize=1000)
    udpServer = UdpServer(queue).start()
    while True:
        while not queue.empty():
            print(queue.get())
            time.sleep(1)
