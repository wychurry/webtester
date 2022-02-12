import argparse
import socket
import threading
import selectors
import time
import hashlib

# 上报cpu/mem/disk
# 完成server端事件存储
# 完成线程池控制


SHOTOR_ID = '123123'
SELF_IP = '123123'

class ShooterWorker(threading.Thread):
    pass

class MonitorClient:

    def __init__(self, server_ip: str, server_port: int) -> None:
        self.server_ip = server_ip
        self.server_port = server_port
        self.sel = selectors.DefaultSelector()
        
        self.try_connect()
        self.timer = threading.Timer(5, self.report_status)
        self.timer.start()

    def try_connect(self):
        print('try connect-------')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = self.sock.connect_ex((self.server_ip, self.server_port))
        self.sock.setblocking(False)
        print(res)
        self.connect_success = res == 0
        print(self.connect_success)
        if self.connect_success:
            self.sel.register(self.sock, selectors.EVENT_WRITE, None)
        else:
            time.sleep(1)
        
    def report_status(self):
        self.timer = threading.Timer(5, self.report_status)
        self.timer.start()
        header = 'V01|REP|%d|fringe_id123' % int(time.time())
        sign = hashlib.md5((header + "123123").encode('utf-8')).hexdigest()
        self.sock.send(('%s|%s|%s\r\n' % (header, sign, "{}")).encode("utf-8"))
        

    def say_hello(self):
        print('---------')
        # for i in range(3):
        header = 'V01|SBY|%d|fringe_id123' % int(time.time())
        sign = hashlib.md5((header + "123123").encode('utf-8')).hexdigest()
        self.sock.send(('%s|%s|%s\r\n' % (header, sign, "{}")).encode("utf-8"))
        self.sel.modify(self.sock, selectors.EVENT_READ)

    def recv_msg(self) -> None:
        # conn, addr = sock.read(100)
        data = self.sock.recv(1000)
        if data:
            print("收到:" + data.decode("utf-8"))
        else:
            self.sel.unregister(self.sock)
            self.sock.close()
            self.connect_success = False


    def run_forever(self) -> None:
        while True:
            if self.connect_success:
                events = self.sel.select(1)
                for e, mask in events:
                    # print(e, mask)
                    if mask == selectors.EVENT_WRITE:
                        self.say_hello()
                    else:
                        self.recv_msg()
            else:
                self.try_connect()
                # callback = e.data
                # callback(e.fileobj, mask)

def start_shooter(server_addr):
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_addr)
        while True:
            sock.send(SHOTOR_ID + ':' + SELF_IP)
            sock.recv()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='device shooter version: 0.1')
    parser.add_argument('-s', dest='addr',type=str, help='server ip and port like x.x.x.x:port')
    parser.add_argument('-d', dest='deamon', action='store_true', help='run as deamon')
    args = parser.parse_args()
    server_ip, server_port = args.addr.split(':')
    print(server_ip, server_port)
    MonitorClient(server_ip, int(server_port)).run_forever()
    # start_shooter((args.addr.split(':')[0], int(args.addr.split(':')[1])))