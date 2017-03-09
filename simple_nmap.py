import socket
import threading
import logging
import sys

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

def IsAlive(host):
  PORT = 22              # The same port as used by the server
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(3)
  try:
    s.connect((host, PORT))
  except socket.error as msg:
    #print 'Received socket exception:', msg
    return
  s.close()
  print ('host %s has ssh port opened' % host)

class HostThread(threading.Thread):

    def __init__(self, host):
       self.host = host
       threading.Thread.__init__(self)

    def run(self):
        # logging.debug('running %s' % self.host)
        IsAlive(self.host)
        return

def ScanSubnet(subnet):
    for i in range(1,255):
        addr = '%s.%d' % (subnet ,i)
        t = HostThread(addr)
        t.start()

ScanSubnet(sys.argv[1])

#IsAlive('100.104.193.56')