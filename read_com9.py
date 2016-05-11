import serial
import time
import datetime

port_name = 'com9'
file = open('%s_hist.txt' % port_name , 'a')


ser = serial.Serial(port_name, 9600, timeout=0)
while 1:
    try:
        data = ser.read(ser.inWaiting()).decode("utf-8")

        if not data:
          time.sleep(50.0/1000.0)
          continue
        lines =data.splitlines()
        i = datetime.datetime.now()
        now = "%s" %i 
        
        for line in lines:
          print (now[:-3]+ line)
          file.write(now[:-3]+ line)
          file.write('\r\n')
        
    except ser.SerialTimeoutException:
        print('Data could not be read')
    