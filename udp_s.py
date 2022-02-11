import socket
import signal

STOP_FLAG = False
def stop(c, d):
    print(c, d)
    global STOP_FLAG
    STOP_FLAG = True
signal.signal(signal.SIGINT, stop)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 50166))

while not STOP_FLAG:
    data, addr = s.recvfrom(1024 * 10)
    print('Received from %s:%s.' % addr )
    print(data)
        