import serial
import time
import datetime
import sys

db_uri = 'mongodb://user:password@ds041673.mlab.com:41673'
db_name = 'nightscout'

from pymongo import MongoClient

def create_object(wixel_data):
    # an example to wixel_data is '6ABW4 54880 44800 213 -89 2'
    mongo = dict()
    data = wixel_data.split()
    mongo['TransmitterId'] = data[0]
    mongo['RawValue'] = int(data[1])
    mongo['FilteredValue'] = int(data[2])
    mongo['BatteryLife'] = int(data[3])
    mongo['ReceivedSignalStrength'] = int(data[4])
    mongo['TransmissionId'] = int(data[5])
    mongo['UploaderBatteryLife'] = 100
    captured_time = int(time.time() * 1000)
    mongo['CaptureDateTime'] = captured_time
    mongo['DebugInfo'] = 'pc %s' % time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(captured_time / 1000))

    return mongo
   

def write_object(log_file, wixel_data):
    mongo = create_object(wixel_data)

    client = MongoClient(db_uri+ '/'+db_name + '?socketTimeoutMS=180000&connectTimeoutMS=60000')
    db = client[db_name]
    collection = db['SnirData']
    post_id = collection.insert_one(mongo).inserted_id
    log(log_file, "succesfully uploaded object to mongo")

def log(file, string):
    i = datetime.datetime.now()
    now = "%s" %i 
    print (now[:-3]+ ':  ' +string)
    file.write(now[:-3]+ ':  ' + string)
    file.write('\r\n')


def comport_loop(log_file, port_name):
    ser = serial.Serial(port_name, 9600, timeout=0)
    log_file.write('Starting loop\r\n')
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
            for line in lines:
                log(log_file, line)
                try:
                    write_object(log_file, line)
                except ValueError as value_error:
                    log(log_file, 'caught exception ' + str(value_error))
        
        except ser.SerialTimeoutException:
                  print('Data could not be read')
                  file.write('caught exception\r\n')


if len(sys.argv) != 2:
  print ("Need to supply port")
  sys.exit()

port_name = sys.argv[1]
log_file = open('%s_hist.txt' % port_name , 'a', 1)

while 1:
    try:
        comport_loop(log_file, port_name)
    except Exception as exception :  
        log(log_file, 'caught exception ' + str(exception))

    