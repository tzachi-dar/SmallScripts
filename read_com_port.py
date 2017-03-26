import serial
import time
import datetime
import time
import sys
import socket
from pymongo import MongoClient
import sqlite3


db_uri = 'mongodb://user:password@ds041673.mlab.com:41673'
db_name = 'nightscout'
transmitter_id = '6FNTM'


''' ------------------------ sqllite3 functions ---------------------------'''

class sqllite3_wrapper:

    file_name = 'example.db'

    def CreateTable(self):
        conn = sqlite3.connect(self.file_name)
        cursor=conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS G4Readings (
                                    TransmitterId text NOT NULL,
                                    RawValue integer NOT NULL,
                                    FilteredValue integer NOT NULL,
                                    BatteryLife integer,
                                    ReceivedSignalStrength integer,
                                    TransmissionId integer,
                                    UploaderBatteryLife integer,
                                    CaptureDateTime BIGINT,
                                    DebugInfo text NOT NULL,
                                    Uploaded int,
                                    PRIMARY KEY (CaptureDateTime, DebugInfo))''')
        conn.commit()
        conn.close()

    def InsertReading(self, reading):
        #expects a dict like the one created in create_object
        conn = sqlite3.connect(self.file_name)
        with conn:
            cursor=conn.cursor()
            cursor.execute("INSERT INTO G4Readings  values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (reading['TransmitterId'], 
                 reading['RawValue'],
                 reading['FilteredValue'],
                 reading['BatteryLife'],
                 reading['ReceivedSignalStrength'],
                 reading['TransmissionId'],
                 reading['UploaderBatteryLife'],
                 reading['CaptureDateTime'],
                 reading['DebugInfo'],
                 reading['Uploaded']))
             

    def GetLatestNotUploadedObjects(self, count):
        # gets the latest n non commited objects
        ret = []
        conn = sqlite3.connect(self.file_name)
        with conn:
            cursor = conn.execute("SELECT * FROM G4Readings WHERE Uploaded=:Uploaded ORDER BY CaptureDateTime DESC LIMIT :Limit", 
                 {"Uploaded": 0, "Limit": count})
        
        
            for raw in cursor:
                raw_dict = dict()
                raw_dict['TransmitterId'] = raw[0]
                raw_dict['RawValue'] = raw[1]
                raw_dict['FilteredValue'] = raw[2]
                raw_dict['BatteryLife'] = raw[3]
                raw_dict['ReceivedSignalStrength'] = raw[4]
                raw_dict['TransmissionId'] = raw[5]
                raw_dict['UploaderBatteryLife'] = raw[6]
                raw_dict['CaptureDateTime'] = raw[7]
                raw_dict['DebugInfo'] = raw[8]
                raw_dict['Uploaded'] = raw[9]
                ret.insert(0,raw_dict)
                print(raw)
        for raw in ret:
            print(raw)
            print (type (raw))
        return ret
    
    def UpdateUploaded(self, CaptureDateTime, DebugInfo):
        conn = sqlite3.connect(self.file_name)
        with conn:
            cur = conn.cursor()    
            cur.execute("UPDATE G4Readings SET Uploaded=? WHERE CaptureDateTime=? and DebugInfo=?", (1, CaptureDateTime, DebugInfo))        
            conn.commit()
            print ("Number of rows updated: %d" % cur.rowcount)

    def RunLocalTests(self):
        sqw = sqllite3_wrapper ()
        sqw.CreateTable()
         for i in range(1, 10000):
         if not i % 1000: print(i)
         obj = create_object('port1', '6ABW4 54880 44800 213 -89 2')
         sqw.InsertReading(obj)

         print("before get")
         lastones = sqw.GetLatestNotUploadedObjects(5)
         for ob in lastones:
             sqw.UpdateUploaded(ob['CaptureDateTime'], ob['DebugInfo'])
         sys.exit(0)

''' ------------------------ end of sqllite3 functions ---------------------------'''


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
    mongo['DebugInfo'] = '%s %s %s' % (socket.gethostname(), time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(captured_time / 1000)), port_name)
    mongo['Uploaded'] = 0

    return mongo

def write_log_to_mongo(log_file, port_name, log_message):
    mongo = dict()
    captured_time = int(time.time() * 1000)
    mongo['CaptureDateTime'] = captured_time
    mongo['DebugMessage'] = '%s %s %s %s' % (socket.gethostname(), time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(captured_time / 1000)) , port_name, log_message)
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
        if port_name.startswith( 'tty' ):
            real_port_name = '/dev/' + port_name
        else:
            real_port_name = port_name
        ser = serial.Serial(real_port_name, 9600, timeout=0)
    except serial.serialutil.SerialException as exception:
        log(log_file, 'caught serial exception ' + str(exception) + " " + exception.__class__.__name__ + " exiting :-(")
        return
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
                    log(log_file, 'caught ValueError exception ' + str(value_error))


if len(sys.argv) != 2:
  print ("Need to supply port")
  sys.exit()

port_name = sys.argv[1]
log_file = open('%s_hist.txt' % port_name , 'a', 1)

# sleep for 30 seconds to let the system connect to the network
time.sleep(30)

try:
    write_log_to_mongo(log_file, port_name, "starting program")
except Exception as exception :  
    log(log_file, 'caught exception in first write' + str(exception) + exception.__class__.__name__)

while 1:
    try:
        comport_loop(log_file, port_name)
    except KeyboardInterrupt as keyboardInterrupt :
        log(log_file, 'caught exception KeyboardInterrupt:' + str(keyboardInterrupt))
        sys.exit(0)
    except Exception as exception :  
        log(log_file, 'caught exception in while loop' + str(exception) + exception.__class__.__name__)
        time.sleep(60)

    
