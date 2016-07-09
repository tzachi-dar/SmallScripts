import serial
import time
import datetime
import sys
import re
import subprocess

# This function is needed for linux in order to convert names like
# 02-5F-76-2F to names like /dev/ttyACM0
# on windows it is not needed because a wixel will always be connected to
# the same com port
def get_com_from_name(serial):

    for i in range(0, 5):
        device = '/dev/ttyACM%d' % i
        #print device 
 
	process = subprocess.Popen(['udevadm', 'info', device], stdout=subprocess.PIPE,universal_newlines=True)
	for line in iter(process.stdout.readline,''):
            #print line.rstrip()
	    cl = re.search(r'E: ID_SERIAL_SHORT=(.*)', line.rstrip())
            if cl and cl.group(1) == serial:
                print "found " +  cl.group(1)
                return device
    # We did not find such a device.
    print 'Device %s not found.' % serial
    print 'Example to device name is \'02-5F-76-2F\''
    print 'run udevadm info /dev/ttyACM0 to find devices'
    print 'Exiting'
    sys.exit()


if len(sys.argv) != 2:
  print ("Need to supply port")
  sys.exit()

if sys.argv[1].startswith('com'):
    # this is windows
    port_name = sys.argv[1]
    file = open('%s_hist.txt' % port_name , 'a', 1)
else:
    # this is linux
    port_name = get_com_from_name(sys.argv[1])
    file = open('hist-%s.txt' % sys.argv[1] , 'a', 1)


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
    
