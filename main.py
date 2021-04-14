from udpServer import UdpServer
from serialServer import SerialServer
from main_thread import Main
from multiprocessing import Queue
import time


if __name__ == '__main__':
    queue = Queue(maxsize=1000)
    main = Main()
    udpServer = UdpServer(queue).start()     # 此处可定义使用串口服务器还是udp服务器，具体参考import列表
    while True:
        while not queue.empty():
            main.response(queue.get())
        time.sleep(1)
