import serial
from apscheduler.schedulers.background import BackgroundScheduler
from link import Link
import traceback
from multiprocessing import Process, Queue
from typing import Dict
import time


class SerialServer(Process):
    server_port = 6000
    client_port = 6001
    sh = BackgroundScheduler()
    com = 'com2'
    links: Dict[Link, Link] = {}
    serial = None

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
                    'time': time.time(),
                    'event': 'communication',
                    'message': it.car
                })
            return
        self.queue.put({
            'ip': ip,
            'team': team,
            'car': car,
            'time': time.time(),
            'event': event,
            'message': message
        })

    def run(self):
        self.serial = serial.Serial(self.com, 115200, timeout=1)
        self.sh.start()
        while True:
            addr = 'serial'
            data = self.serial.read(256)
            if addr not in self.links.keys():
                self.links[addr] = Link(addr, self.client_port, self.sh, self.removeLink, self.addQueue)
            try:
                self.links[addr].recv(data)
            except:
                print(traceback.format_exc())


