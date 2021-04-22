import socket
from apscheduler.schedulers.background import BackgroundScheduler
from link import Link
import traceback
from multiprocessing import Process, Queue
from typing import Dict
import datetime


class UdpServer(Process):
    server_port = 6666
    client_port = 2333
    sh = BackgroundScheduler()
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    links: Dict[Link, Link] = {}

    def __init__(self, queue: Queue):
        Process.__init__(self, daemon=True)
        self.queue = queue

    def removeLink(self, ip):
        if ip in self.links.keys():
            self.addQueue(ip, self.links[ip].team, self.links[ip].car, 'remove', {})
            del self.links[ip]

    def addQueue(self, ip, team, car, event, message):
        if team == '123456':
            return
        if event == 'communication':
            for it in self.links:
                if it.team != team or it.car == car:
                    continue
                it.sendOrder(0xa1, message)
                self.queue.put({
                    'ip': ip,
                    'team': team,
                    'car': car,
                    'time': datetime.datetime.now(),
                    'event': 'communication',
                    'message': it.car
                })
            return
        self.queue.put({
            'ip': ip,
            'team': team,
            'car': car,
            'time': datetime.datetime.now(),
            'event': event,
            'message': message
        })

    def run(self):
        self.server.bind(("0.0.0.0", self.server_port))
        self.sh.start()
        print('UDP模块上线')
        while True:
            data, (addr, _) = self.server.recvfrom(256)
            if addr not in self.links.keys():
                self.links[addr] = Link(addr, self.client_port, self.sh, self.removeLink, self.addQueue)
            try:
                self.links[addr].recv(data)
            except:
                print(traceback.format_exc())


