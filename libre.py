from bluepy import btle
import time  
import binascii

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)
        print('Init called.')
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        print ('notifcation called', data)


def foo():     
    print ("Connecting...")
    dev = btle.Peripheral("DB:23:F4:F2:86:62", 'random')
    dev.setDelegate( MyDelegate('paramsi') )
     
    print ("Services...")
    for svc in dev.services:
        print (str(svc))
    
    NRF_UART_SERVICE = btle.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
 
    print ("charterstics...")
    lightService = dev.getServiceByUUID(NRF_UART_SERVICE)
    for ch in lightService.getCharacteristics():
         print (str(ch))

    NRF_UART_TX = btle.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
    NRF_UART_RX = btle.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
    
    lightSensorConfig = lightService.getCharacteristics(NRF_UART_TX)[0]
    # Enable the sensor
    #lightSensorConfig.write(bytes("\xF0"))
    #lightSensorConfig.write(str(bytes(240)))
    #print str(bytes(240))
    #print str([240])
    str1 = "".join(map(chr, [240]))
    print(str1)
    lightSensorConfig.write(str1)
       
    time.sleep(1.0) # Allow sensor to stabilise


    lightSensorValue = lightService.getCharacteristics(NRF_UART_RX)[0]
    # Read the sensor
    
    while True:
        val = lightSensorValue.read()
        print ("Light sensor raw value", binascii.b2a_hex(val), val)
        dev.waitForNotifications(1.0)

foo()

