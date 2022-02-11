import socket
import signal
import time
import selectors

sel = selectors.DefaultSelector()

STOP_FLAG = False
def stop(c, d):
    print(c, d)
    global STOP_FLAG
    STOP_FLAG = True
signal.signal(signal.SIGINT, stop)





def accept(sock, mask):
    conn, addr = sock.accept()
    print('accept ', conn, 'from ', addr, 'mask', mask)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(sock, mask):
    msg = ''
    while True:
        data = sock.recv(4)
        sock.shutdown(1)
        break
        print('mask ', mask)
        if len(data) == 4:
            print(data)
            msg += data.decode('utf-8')
        else:
            print('recv all::: ', msg)
            break
            # sel.unregister(sock)
            # sock.close()




s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 8000))
s.listen(5)
s.setblocking(False)
sel.register(s, selectors.EVENT_READ, accept)
while not STOP_FLAG:
    events = sel.select(1)
    for e, mask in events:
        callback = e.data
        callback(e.fileobj, mask)
# while not STOP_FLAG:
#     try:
#         s1, addr = s.accept()
#         s1.send(("aabbccdd" ).encode("utf-8"))
#         while True:
#             ff = s1.recv(100)
#             print(ff)
#             if len(ff) < 100:
#                 s1.send(("aabbccdd" * 10000).encode("utf-8"))
#                 break
#     except Exception as e:
#         print(e)
#     time.sleep(1)