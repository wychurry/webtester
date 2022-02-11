import time
import threading


def createTimer():
    t = threading.Timer(2, repeat)
    t.start()
    

def repeat():
    createTimer()
    print('Now-1:', time.strftime('%H:%M:%S',time.localtime()))
    
createTimer()