#!/bin/bash
while [ 1 ];
do
    wget www.google.co.il>> /home/pi/SmallScripts/systemstatus.log 2>&1
    ping -c 1 192.168.0.1 >> /home/pi/SmallScripts/systemstatus.log
    ps -ef | grep python >> /home/pi/SmallScripts/systemstatus.log
    sleep 60
done

