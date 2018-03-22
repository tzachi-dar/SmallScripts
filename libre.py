from bluepy import btle
import time  
import binascii
import struct
from time import gmtime, strftime

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)
        print('Init called.')
        # ... initialise here
        self.count = 0

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        #print ('notifcation calledi count = ', self.count , strftime("%Y-%m-%d %H:%M:%S", gmtime()),binascii.b2a_hex(data))
        self.count +=1
        if self.count % 10 != 0:
            print self.count



def foo():     
    print ("Connecting...")
    dev = btle.Peripheral("DB:23:F4:F2:86:62", 'random')
    dev.setDelegate( MyDelegate('paramsi') )
     
    print ("Services...")
    for svc in dev.services:
        print (str(svc))
    
    NRF_UART_SERVICE = btle.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E") # nrfDataService
 
    print ("charterstics...")
    nrfGattService = dev.getServiceByUUID(NRF_UART_SERVICE)
    for ch in nrfGattService.getCharacteristics():
         print (str(ch))

    NRF_UART_RX = btle.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
    NRF_UART_TX = btle.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
    CLIENT_CHARACTERISTIC_CONFIG =  btle.UUID("00002902-0000-1000-8000-00805f9b34fb")
    
    nrfGattCharacteristic = nrfGattService.getCharacteristics(NRF_UART_TX)
    print "nrfGattCharacteristic = ", nrfGattCharacteristic
    #print  nrfGattCharacteristic.supportsRead()
    print nrfGattCharacteristic[0].propertiesToString()
    #???nrfGattCharacteristic[0].write(struct.pack('<bb', 0x01, 0x00), False)
    bdescriptor =  nrfGattCharacteristic[0].getDescriptors(CLIENT_CHARACTERISTIC_CONFIG)
    bdescriptor[0].write(struct.pack('<bb', 0x01, 0x00), False)
    mCharacteristicSend = nrfGattService.getCharacteristics(NRF_UART_RX)[0]

    #charaProp = nrfGattCharacteristic.

    #lightSensorConfig = lightService.getCharacteristics(NRF_UART_TX)[0]
    # Enable the sensor
    #lightSensorConfig.write(bytes("\xF0"))
    #lightSensorConfig.write(str(bytes(240)))
    #print str(bytes(240))
    #print str([240])
    str1 = "".join(map(chr, [240]))
    print(str1)
    mCharacteristicSend.write(str1)
       
    time.sleep(1.0) # Allow sensor to stabilise


    #lightSensorValue = lightService.getCharacteristics(NRF_UART_RX)[0]
    # Read the sensor
    
    while True:
        #val = lightSensorValue.read()
        #print ("Light sensor raw value", binascii.b2a_hex(val), val)
        dev.waitForNotifications(1.0)

foo()
