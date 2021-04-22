from udpServer import UdpServer
from main_thread import Main
from multiprocessing import Queue
import queue
from web import Web
import time

if __name__ == '__main__':
    queue1 = Queue(maxsize=1000)
    queue2 = queue.Queue(maxsize=1000)
    carsQueue = queue.Queue(maxsize=2)


    def onChange(data):
        carsQueue.put(data)


    web = Web([queue2, carsQueue])
    time.sleep(1)
    web.start()
    main = Main(onChange)
    udpServer = UdpServer(queue1).start()
    time.sleep(3)
    print('服务启动成功')
    while True:
        while not queue1.empty():
            main.response(queue1.get())
        while not queue2.empty():
            main.response(queue2.get())
        time.sleep(0.1)
