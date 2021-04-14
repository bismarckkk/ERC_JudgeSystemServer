import socket
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import binascii


class Link:
    def __init__(self, ip, port, sh: BackgroundScheduler, rm, add):
        self.ip = ip
        self.cache = b''
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.alive = True
        self.sh = sh
        self.team = '123456'
        self.car = -1
        self.rm = rm
        self.seq = 0
        self._add = add
        self.sh.add_job(self.lostConnect, 'date', run_date=datetime.datetime.now()+datetime.timedelta(seconds=6),
                        id=self.ip+'-refresh', replace_existing=True)

    def add(self, event, message=None):
        self._add(self.ip, self.team, self.car, event, message)

    def lostConnect(self):
        self.alive = False
        self.add('lost')
        self.sh.add_job(self.rm, 'date', run_date=datetime.datetime.now() + datetime.timedelta(minutes=3),
                        id=self.ip + '-delete', args=(self.ip,))

    def refreshAlive(self):
        if not self.alive:
            self.alive = True
            self.add('reconnect')
            self.sh.remove_job(self.ip + '-delete')
        self.sh.add_job(self.lostConnect, 'date', run_date=datetime.datetime.now() + datetime.timedelta(seconds=6),
                        id=self.ip + '-refresh', replace_existing=True)

    @staticmethod
    def getCRC(data):
        return (sum(data) - data[-3]) % 255

    @staticmethod
    def bytes2str(data):
        return binascii.b2a_hex(data).decode()

    def recv(self, data):
        if len(data) == 0:
            return
        self.refreshAlive()
        nowIter = 0
        data = self.cache + data
        for i in range(6, len(data)):
            if len(data) - i <= 6:
                break
            if i < nowIter:
                continue
            if data[i - 6] != 0x41 or data[i - 5] != 0x41 or data[i - 4] != 0x41 or data[i - 3] != 0x41:
                continue
            seq = data[i - 2]
            if data[i - 1] != 0xaa or data[i] != 0:
                continue
            length = data[i + 1]
            if len(data) < i + length - 1:
                break
            if length < 8:
                continue
            if data[i + length - 2] != 0xbb or data[i + length - 3] != 0x11:
                continue
            crc = self.getCRC(data[i - 1: i + length - 1])
            if data[i + length - 4] != crc:
                continue
            if seq == self.seq - 1:
                continue
            if seq > self.seq:
                self.add('lost_pkg')
            self.seq = 1 + seq
            if self.seq == 256:
                self.seq = 0
            order = data[i + 2]
            args = data[i + 3: i + length - 4]
            self.cache = b''
            nowIter = i + length
            self.processOrder(order, args)
        cacheLength = len(data) - nowIter
        if 0 < cacheLength < 255:
            self.cache = data[nowIter:]
        if cacheLength >= 255:
            self.cache = data[-255:]

    def processOrder(self, order, args: bytes):
        if order == 0x80:
            self.team = args[:6].decode()
            self.car = args[6]
            self.add('register')
            self.sendOrder(0xa0, 1)
            self.ack()
        if self.team == '123456' or self.car == -1:
            raise NameError('IP %s not register' % self.ip)
        if order == 0x03:
            self.add('communication', args)
            self.ack()
        if order == 0x01:
            if args[0] == self.car:
                self.add('start')
                self.ack()
            else:
                raise NameError('Car id not match')
        if order == 0x02:
            if args[0] == self.car:
                self.add('stop')
                self.ack()
            else:
                raise NameError('Car id not match')

    def send(self, data):
        self.s.sendto(data, (self.ip, self.port))

    @staticmethod
    def toBytes(data):
        if isinstance(data, int):
            return data.to_bytes(1, 'big', signed=False)
        elif isinstance(data, str):
            return data.encode()
        elif isinstance(data, bytes):
            return data
        else:
            raise TypeError('Not support transform')

    def sendOrder(self, order, args):
        order = self.toBytes(order)
        args = self.toBytes(args)
        if len(args) > 248:
            raise BufferError('Args is too long')
        frameHead = b'\xaa\x00'
        length = self.toBytes(7 + len(args))
        frameEnd = b'\x11\xbb'
        crc = self.getCRC(frameHead + length + order + args + self.toBytes(0) + frameEnd)
        frame = frameHead + length + order + args + self.toBytes(crc) + frameEnd
        self.send(frame)

    def ack(self):
        self.sendOrder(0xa0, 2)
