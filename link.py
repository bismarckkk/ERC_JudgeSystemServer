import socket
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import binascii


class Link:
    def __init__(self, ip, port, sh: BackgroundScheduler, rm):
        self.ip = ip
        self.cache = b''
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.alive = True
        self.sh = sh
        self.team = '123456'
        self.rm = rm
        self.sh.add_job(self.lostConnect, 'date', run_date=datetime.datetime.now()+datetime.timedelta(seconds=6),
                        id=self.ip+'-refresh')

    def lostConnect(self):
        self.alive = False
        self.sh.add_job(self.rm, 'date', run_date=datetime.datetime.now() + datetime.timedelta(minutes=3),
                        id=self.ip + '-delete', args=self.ip)

    def refreshAlive(self):
        self.sh.reschedule_job(self.ip+'-refresh', 'date',
                               run_date=datetime.datetime.now()+datetime.timedelta(seconds=6))

    @staticmethod
    def getCRC(data):
        return (sum(data) - data[-3]) % 255

    @staticmethod
    def bytes2str(data):
        return binascii.b2a_hex(data).decode()

    def recv(self, data):
        self.refreshAlive()
        nowIter = 0
        data = self.cache + data
        for i in range(1, len(data)):
            if len(data) - i <= 6:
                break
            if i < nowIter:
                continue
            if data[i - 1] != 0xaa or data[i] != 0:
                continue
            length = data[i + 1]
            if len(data) < i + length - 1:
                break
            if length < 8:
                continue
            if data[i + length - 2] != 0xaa or data[i + length - 3] != 0:
                continue
            crc = self.getCRC(data[i - 1: i + length - 1])
            if data[i + length - 4] != crc:
                continue
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
        print(self.ip, self.bytes2str(order), self.bytes2str(args))
        if order == 0x80:
            self.team = args.decode()
            print('Team %s register at %s' % (self.team, self.ip))
        if self.team == '123456':
            raise NameError('IP %s not register' % self.ip)

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
        frameEnd = b'\x00\xaa'
        crc = self.getCRC(frameHead + length + order + args + self.toBytes(0) + frameEnd)
        frame = frameHead + length + order + args + self.toBytes(crc) + frameEnd
        print(frame)

    def ack(self):
        self.sendOrder(0xa0, 2)
