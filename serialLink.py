from link import Link
from apscheduler.schedulers.background import BackgroundScheduler
from serial import Serial


class SerialLink(Link):
    def __init__(self, ip, port, sh: BackgroundScheduler, rm, add, serial: Serial):
        super().__init__(ip, port, sh, rm, add)
        self.serial = serial

    def send(self, data):
        self.serial.write(data)
