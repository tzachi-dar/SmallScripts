import serial
import time
import datetime
import time
import sys
import socket
from pymongo import MongoClient
import sqlite3
import os
import inspect
import threading
import json
import signal

db_uri = 'mongodb://user:password@ds041673.mlab.com:41673'
db_name = 'nightscout'
transmitter_id = '6FNTM'

HOST = ''  # All interfaces
PORT = 50005  # xdrip standard port

def create_object(port_name, wixel_data):
    # an example to wixel_data is '6FNTM 54880 44800 213 -89 2'
    mongo = dict()
    data = wixel_data.split()
    mongo['TransmitterId'] = data[0]
    if mongo['TransmitterId'] != transmitter_id:
        log(log_file, "rejecting packet with transmision id %s" % mongo['TransmitterId'])
        return None
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

''' ------------------------ sqllite3 functions ---------------------------'''

class sqllite3_wrapper:

    path = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
    file_name = path+os.sep+'example.db'

    def CreateTable(self):
        print(self.file_name)
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
             

    def GetLatestObjects(self, count, only_not_uploaded):
        # gets the latest n non commited objects
        ret = []
        conn = sqlite3.connect(self.file_name)
        with conn:
            if only_not_uploaded:
                cursor = conn.execute("SELECT * FROM G4Readings WHERE Uploaded=:Uploaded ORDER BY CaptureDateTime DESC LIMIT :Limit", 
                    {"Uploaded": 0, "Limit": count})
            else:
                cursor = conn.execute("SELECT * FROM G4Readings ORDER BY CaptureDateTime DESC LIMIT :Limit", 
                    {"Limit": count})
        
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
        for i in range(1, 1000):
            if not i % 1000: print(i)
            obj = create_object('port1', '6FNTM 54880 44800 213 -89 2')
            sqw.InsertReading(obj)

        print("before get")
        lastones = sqw.GetLatestObjects(5, False)
        for ob in lastones:
            sqw.UpdateUploaded(ob['CaptureDateTime'], ob['DebugInfo'])
        sys.exit(0)

#sqw = sqllite3_wrapper ()
#sqw.RunLocalTests()

''' ----------------- threads that respond to tcp requests -----------------------'''

def clientThread(connlocal):
    try:
        connlocal.settimeout(10)
        while True:
            data = connlocal.recv(1024)
            reply = ''
            if not data:
                break
            decoded = json.loads(data)
                        print("type decpded = %s" % type (decoded))
            print json.dumps(decoded, sort_keys=True, indent=4)
                        if decoded['version'] != 1:
                            print("bad version %s" % decoded['version'] )

                        sqw = sqllite3_wrapper()
                        not_uploaded_readings = sqw.GetLatestObjects( decoded['numberOfRecords'],False)
                        for reading_dict in not_uploaded_readings:
                           reading_dict['RelativeTime'] = (int(time.time()*1000) ) - reading_dict['CaptureDateTime']
                           if reading_dict['RelativeTime'] < 0:
                               continue
                           reply = reply + json.dumps(reading_dict) +"\n"

            print ("reply = %s" % reply)
                        reply = reply + "\n"

            connlocal.sendall(reply)
        connlocal.close()

    except Exception, e:
        print "Exception in clientThread: ", e

def CreateListeningSocket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    print 'Socket created'

    # Bind socket to local host and port

    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        return

    s.listen(10)
    print "Waiting for connections"

    while 1:
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])

        threading.Thread(target=clientThread, args=(conn,)).start()

def CreateListeningSocketWrapper():
    while 1:
        try:
            CreateListeningSocket()
        except Exception as exception :  
            #???? log(log_file, 'CreateListeningSocketWrapper caught exception in while loop' + str(exception) + exception.__class__.__name__)
            time.sleep(60)


''' ------------------------------------------------------------------------------'''


def write_log_to_mongo(log_file, port_name, log_message):
    mongo = dict()
    captured_time = int(time.time() * 1000)
    mongo['CaptureDateTime'] = captured_time
    mongo['DebugMessage'] = '%s %s %s %s' % (socket.gethostname(), time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(captured_time / 1000)) , port_name, log_message)
    write_object_to_mongo(log_file, mongo)
    log(log_file, "sent %s to mongo" % log_message)
   


def write_object_to_mongo(log_file, mongo_dict):
    client = MongoClient(db_uri+ '/'+db_name + '?socketTimeoutMS=180000&connectTimeoutMS=60000')
    db = client[db_name]
    collection = db['SnirData']
    insertion_result = collection.insert_one(mongo_dict)
    log(log_file, "succesfully uploaded object to mongo insertion_result = %s" % insertion_result.acknowledged)

def log(file, string):
    i = datetime.datetime.now()
    now = "%s" %i 
    print (now[:-3]+ ':  ' +string)
    file.write(now[:-3]+ ':  ' + string)
    file.write('\r\n')


def comport_loop(log_file, port_name, mongo_wrapper):
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
            # In order to create fake data, uncomment the next two lines, and add a comment to continue above
            #data = '6FNTM 54880 44800 213 -89 2'
            #time.sleep(10)

        
            lines =data.splitlines()
            for line in lines:
                log(log_file, line)
                try:
                    mongo_dict = create_object(port_name, line)
                    if mongo_dict is None:
                        continue
                    sqw = sqllite3_wrapper()
                    sqw.InsertReading(mongo_dict)
                    mongo_wrapper.SetEvent()
                except ValueError as value_error:
                    log(log_file, 'caught ValueError exception ' + str(value_error))



class MongoWrapper(threading.Thread):

    event = None
    log_file = None
    

    def __init__(self, log_file):
        self.event = threading.Event()
        self.log_file =log_file
        threading.Thread.__init__(self)

    def SetEvent(self):
        self.event.set()

    def run(self):
        #This threads loop and reads data from the sql, and uploads it to the mongo DB.
        #It starts to work based on the event or based on 1 minutes timeout.
        log(log_file, "Starting mongo thread")
        while True:
            try:
                ret = self.event.wait(1*60)
                log(log_file, "event wait ended, ret = %s" % ret)
                # The next line introduces many races that are only fixed by the timeout on wait.
                self.event.clear()
                sqw = sqllite3_wrapper ()
                not_uploaded_readings = sqw.GetLatestObjects(12 * 8, True)
                for reading_dict in not_uploaded_readings:
                    write_object_to_mongo(log_file, reading_dict)
                    sqw.UpdateUploaded(reading_dict['CaptureDateTime'], reading_dict['DebugInfo'])
            except Exception as exception :  
               log(log_file, 'caught exception in MongoThread, will soon continue' + str(exception) + exception.__class__.__name__)
               time.sleep(60)


if len(sys.argv) != 2:
  print ("Need to supply port")
  sys.exit()

port_name = sys.argv[1]
log_file = open('%s_hist.txt' % port_name , 'a', 1)

# sleep for 30 seconds to let the system connect to the network
time.sleep(30)

#Create the sqllite table.
sqw = sqllite3_wrapper ()
sqw.CreateTable()


try:
    write_log_to_mongo(log_file, port_name, "starting program")
except Exception as exception :  
    log(log_file, 'caught exception in first write ' + str(exception) + exception.__class__.__name__)

try:
    mongo_wrapper = MongoWrapper(log_file)
    mongo_wrapper.start()
except Exception as exception :  
    # This is a critical failure, we will continue going up, but in a very bad state. Consider quiting the program
    log(log_file, 'WTF, caught exception in MongoWrapper cration ' + str(exception) + exception.__class__.__name__)

    
# start the listner thread
try:
    threading.Thread(target= CreateListeningSocketWrapper).start()
except Exception as exception :  
    # This is a critical failure, we will continue going up, but in a very bad state. Consider quiting the program
    log(log_file, 'WTF, caught exception in opening listening socket ' + str(exception) + exception.__class__.__name__)


while 1:
    try:
        comport_loop(log_file, port_name, mongo_wrapper)
    except KeyboardInterrupt as keyboardInterrupt :
        log(log_file, 'caught exception KeyboardInterrupt:' + str(keyboardInterrupt))
    os.kill(os.getpid(), signal.SIGKILL)
        sys.exit(0)
    except Exception as exception :  
        log(log_file, 'caught exception in while loop' + str(exception) + exception.__class__.__name__)
        time.sleep(60)

    
