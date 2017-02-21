import serial
import time
import datetime
import time
import sys

db_uri = 'mongodb://user:password@ds041673.mlab.com:41673'
db_name = 'nightscout'
transmitter_id = '6FNTM'

from pymongo import MongoClient

def create_object(port_name, wixel_data):
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
    mongo['DebugInfo'] = 'pc %s %s' % (time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(captured_time / 1000)), port_name)

    return mongo

def write_log_to_mongo(log_file, port_name, log_message):
    mongo = dict()
    captured_time = int(time.time() * 1000)
    mongo['CaptureDateTime'] = captured_time
    mongo['DebugMessage'] = 'pc %s %s %s' % (time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(captured_time / 1000)) , port_name, log_message)
    write_object(log_file, mongo)
    log(log_file, "sent %s to mongo" % log_message)
   
def write_data_to_mongo(log_file, port_name, wixel_data):
    mongo = create_object(port_name, wixel_data)
    if mongo['TransmitterId'] != transmitter_id:
        log(log_file, "rejecting packet with transmision id %s" % mongo['TransmitterId'])
        return
    write_object(log_file, mongo)

def write_object(log_file, mongo_dict):
    client = MongoClient(db_uri+ '/'+db_name + '?socketTimeoutMS=180000&connectTimeoutMS=60000')
    db = client[db_name]
    collection = db['SnirData']
    post_id = collection.insert_one(mongo_dict).inserted_id
    log(log_file, "succesfully uploaded object to mongo")

def log(file, string):
    i = datetime.datetime.now()
    now = "%s" %i 
    print (now[:-3]+ ':  ' +string)
    file.write(now[:-3]+ ':  ' + string)
    file.write('\r\n')


def comport_loop(log_file, port_name):
    write_log_to_mongo(log_file, port_name, "starting loop")
    try:
        ser = serial.Serial(port_name, 9600, timeout=0)
    except serial.serialutil.SerialException as exception:
        log(log_file, 'caught exception ' + str(exception) + " " + exception.__class__.__name__ + " exiting :-(")
        sys.exit(1)
    log_file.write('Starting loop\r\n')
    while 1:
        
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
                    write_data_to_mongo(log_file, port_name, line)
                except ValueError as value_error:
                    log(log_file, 'caught exception ' + str(value_error))


if len(sys.argv) != 2:
  print ("Need to supply port")
  sys.exit()

port_name = sys.argv[1]
log_file = open('%s_hist.txt' % port_name , 'a', 1)

write_log_to_mongo(log_file, port_name, "starting program")

while 1:
    try:
        comport_loop(log_file, port_name)
    except KeyboardInterrupt as keyboardInterrupt :
        log(log_file, 'caught exception KeyboardInterrupt:' + str(keyboardInterrupt))
        sys.exit(0)
    except Exception as exception :  
        log(log_file, 'caught exception ' + str(exception) + exception.__class__.__name__)
        time.sleep(1)

    