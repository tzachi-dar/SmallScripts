import serial
import time
import datetime
import sys

if len(sys.argv) != 2:
  print ("Need to supply port")
  sys.exit()

port_name = sys.argv[1]
file = open('%s_hist.txt' % port_name , 'a', 1)


ser = serial.Serial(port_name, 9600, timeout=0)
while 1:
    try:
        bytes = ser.read(ser.inWaiting())
        if len(bytes) < 1:
          time.sleep(50.0/1000.0)
          continue
        print(bytes)
        data = bytes.decode("ASCII")

        #if not data:
        #  time.sleep(50.0/1000.0)
        #  continue
        
        lines =data.splitlines()
        i = datetime.datetime.now()
        now = "%s" %i 
        
        for line in lines:
          print (now[:-3]+ line)
          file.write(now[:-3]+ line)
          file.write('\r\n')
        
    except ser.SerialTimeoutException:
        print('Data could not be read')
    