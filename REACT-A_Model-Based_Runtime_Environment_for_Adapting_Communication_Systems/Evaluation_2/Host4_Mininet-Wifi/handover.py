#!/usr/bin/python

'SDN Handover Evaluation'

from mininet.node import Controller
from mininet.node import RemoteController
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
import time
from time import sleep
import os
import argparse

import sys, Ice
import Manta
import json
import threading

def sendSensorData(sensor, distance, current_ap):
    data = {
        "DestHost": {
            "type": "DestinationHost",
            "distance": distance
        }
    }
    jsonString = json.dumps(data)
    info("***Send " + str(jsonString) + "\n")
    sensor.receiveSensorData(jsonString)
    info("*** sta1 associated to " + str(current_ap) + " with distance " + str(distance) + "\n")


def thread(startupTime, mobilityTime, sta1):
    with Ice.initialize() as communicator:
        base = communicator.stringToProxy("Sensor-1:default -h 10.0.1.4 -p 10002")
        sensor = Manta.Sensing.ISensorPrx.checkedCast(base)
        if not sensor:
            raise RuntimeError("Invalid proxy")
        t_start = time.time()
        t_end = time.time() + startupTime + mobilityTime
        previous_ap = "ap1"
        while time.time() < t_end:
            if time.time() < t_start + startupTime:
                continue
            try:
                distance = int(sta1.get_distance_to(sta1.params['associatedTo'][0]))
                current_ap = str(sta1.params['associatedTo'][0])
            except Exception as e:
                distance = 0
                current_ap = previous_ap
                info(e)
                pass
            if current_ap is not previous_ap:
                previous_ap = current_ap
                info("*** Car switched AP\n")
                while(distance > 20):
                    sleep(0.1)
                    distance = int(sta1.get_distance_to(sta1.params['associatedTo'][0]))
                
                sendSensorData(sensor, distance, current_ap)
            else:
                sendSensorData(sensor, distance, current_ap)
                sleep(1.0)


def topology():
    "Create network."
    net = Mininet_wifi(controller=RemoteController)

    if args.evaluation == True:
        workingDir = os.path.dirname(__file__)
        folderName = str(args.overlapping) + '_' + str(args.mobility)
        folderPath = os.path.join(workingDir,folderName)

        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

    if args.overlapping:
        range = 75
    else:
        range = 50

    info("*** Creating nodes\n")
    
    if args.network_only == False:
        sta1 = net.addStation('sta1', mac='00:00:00:00:00:02', ip='10.0.0.1/8', range=range, position='100,30,0')
        h1 = net.addHost('h1', mac='00:00:00:00:00:10', ip='10.0.0.100/8')
    
    ap1 = net.addAccessPoint('ap1', ssid='ssid', mode='g', channel='1', position='100,30,0', range=range)
    ap2 = net.addAccessPoint('ap2', ssid='ssid', mode='g', channel='5', position='200,30,0', range=range)
    ap3 = net.addAccessPoint('ap3', ssid='ssid', mode='g', channel='1', position='300,30,0', range=range)
    ap4 = net.addAccessPoint('ap4', ssid='ssid', mode='g', channel='5', position='400,30,0', range=range)
    ap5 = net.addAccessPoint('ap5', ssid='ssid', mode='g', channel='1', position='500,30,0', range=range)
    s1 = net.addSwitch('s1')
    c1 = net.addController('c1', controller=RemoteController, ip=str(args.controller_ip))

    net.setPropagationModel(model="logDistance", exp=5)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Creating links\n")
    net.addLink(ap1, s1, bw=100, delay='1ms')
    net.addLink(ap2, s1, bw=100, delay='1ms')
    net.addLink(ap3, s1, bw=100, delay='1ms')
    net.addLink(ap4, s1, bw=100, delay='1ms')
    net.addLink(ap5, s1, bw=100, delay='1ms')

    if args.network_only == False:
        net.addLink(h1, s1, bw=100, delay='1ms')

    if args.gui:
        net.plotGraph(max_x=600, max_y=100)

    mobilityTime = int(args.mobility)

    if args.network_only == False:
        info("*** Setting up mobility\n")
        startupTime = 5
        net.startMobility(time=0)
        net.mobility(sta1, 'start', time=startupTime, position='100,30,0')
        net.mobility(sta1, 'stop', time=mobilityTime+startupTime, position='400,30,0')
        net.stopMobility(time=mobilityTime+startupTime)

    info("*** Starting network\n")
    net.build()
    c1.start()
    s1.start([c1])
    ap1.start([c1])
    ap2.start([c1])
    ap3.start([c1])
    ap4.start([c1])
    ap5.start([c1])

    if args.network_only == False:
        # Keep ONOS ARPProxy proxying
        info("*** Starting arping\n")
        sta1.cmd('while sleep 0.25; do arping 10.0.0.100 -c 1 -q; done &')

    if args.evaluation == True:
        if args.sensor_thread == True:
            info("*** Run car sensor thread\n")
            x = threading.Thread(target=thread, args=(startupTime,mobilityTime,sta1,))
            x.start()
        info("*** Run iperf server on sta1\n")
        sta1.cmd('sleep ' + str(startupTime) + ' && iperf -u -s -i 1 > ' + folderPath + '/' + 'iperf_server' + str(args.run) + '&')
        info("*** Run iperf client on h1\n")
        h1.cmd('sleep ' + str(startupTime) + ' && iperf -u -b 25m -c 10.0.0.1 -t ' + str(mobilityTime) + ' > ' + folderPath + '/' + 'iperf_client' + str(args.run))
        

    if args.evaluation == False:
        info("*** Running CLI\n")
        CLI_wifi(net)

    if args.evaluation == True:
        sleep(3)
        os.system('pkill -f \'iperf\'')
    
    info("*** Stopping network\n")
    net.stop()

    if args.evaluation == True:
        sleep(1)

if __name__ == '__main__':
    setLogLevel('info')
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--overlapping", help="If there should be a 50 percent overlap between the APs", default=False, type=lambda x: (str(x).lower() in ['true','1','yes']))
    parser.add_argument("-e", "--evaluation", help="Evalmode using iperf", default=False, type=lambda x: (str(x).lower() in ['true','1','yes']))
    parser.add_argument("-r", "--run", help="Run number for evaluation", default=0)
    parser.add_argument("-m", "--mobility", help="Mobility Time", default=20)
    parser.add_argument("-g", "--gui", help="GUI", default=False, type=lambda x: (str(x).lower() in ['true','1','yes']))
    parser.add_argument("-ip", "--controller-ip", help="IP address of remote SDN controller", default="127.0.0.1")
    parser.add_argument("-n", "--network-only", help="Create only the network without hosts", default=False, type=lambda x: (str(x).lower() in ['true','1','yes']))
    parser.add_argument("-s", "--sensor-thread", help="Create car sensor thread", default=True, type=lambda x: (str(x).lower() in ['true','1','yes']))
    args = parser.parse_args()
    info("*** Run with arguments\n")
    info(args)
    topology()
