import socket
from apscheduler.schedulers.background import BackgroundScheduler
from link import Link
import traceback


class UdpServer:
    server_port = 6000
    client_port = 6001
    sh = BackgroundScheduler()
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("0.0.0.0", server_port))
    links = {}

    def removeLink(self, ip):
        if ip in self.links.keys():
            del self.links[ip]

    def run(self):
        while True:
            data, (addr, _) = self.server.recvfrom(1024)
            if addr not in self.links.keys():
                self.links[addr] = Link(addr, self.client_port, self.sh, self.removeLink)
            try:
                self.links[addr].recv(data)
            except:
                print(traceback.format_exc())


s = UdpServer()
s.run()

