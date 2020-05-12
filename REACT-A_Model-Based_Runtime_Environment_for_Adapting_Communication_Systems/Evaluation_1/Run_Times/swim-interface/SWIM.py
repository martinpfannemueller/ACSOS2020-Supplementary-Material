import socket
import sys
import Ice
import Manta
import json
import time
import _thread
import threading
import re

from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser

skips = 0
current_dimmer_value = 0

def sendCommand(c):
    c = c.encode()
    sock.sendall(c)
    data = sock.recv(4096)
    data = data.decode()
    data = data.strip()
    return data

def getDimmer():
    return float(sendCommand('get_dimmer\n'))

def getServers():
    return int(sendCommand('get_servers\n'))

def getActiveServers():
    return int(sendCommand('get_active_servers\n'))

def getMaxServers():
    return int(sendCommand('get_max_servers\n'))

def getUtilization(serverId):
    return float(sendCommand('get_utilization server' + str(serverId) + "\n"))

def getBasicResponseTime():
    return float(sendCommand('get_basic_rt\n'))

def getOptionalResponseTime():
    return float(sendCommand('get_opt_rt\n'))

def getBasicThroughput():
    return float(sendCommand('get_basic_throughput\n'))

def getOptionalThroughput():
    return float(sendCommand('get_opt_throughput\n'))

def getArrivalRate():
    return float(sendCommand('get_arrival_rate\n'))

def addServer():
    result = sendCommand('add_server\n')
    return result == 'OK'

def removeServer():
    result = sendCommand('remove_server\n')
    return result == 'OK'

def setDimmer(dimmer):
    result = sendCommand('set_dimmer ' + str(dimmer) + '\n')
    return result == 'OK'

def getTotalUtilization():
    utilization = 0
    numActiveServers = getActiveServers()
    for i in range(1, numActiveServers+1):
        utilization += getUtilization(i)
    return utilization

def getAverageUtilization():
    utilization = 0
    numActiveServers = getActiveServers()
    for i in range(1, numActiveServers+1):
        utilization += getUtilization(i)
    return utilization/numActiveServers


def getAverageResponseTime():
    basicTput = getBasicThroughput()
    optTput = getOptionalThroughput()
    avgResponseTime = basicTput * getBasicResponseTime() + optTput * getOptionalResponseTime() / (basicTput + optTput)
    return avgResponseTime


# Helper method
def get(key):
    if key is "averageUtilization":
        return getAverageUtilization()
    elif key is "basicResponseTime":
        return getBasicResponseTime()
    elif key is "optResponseTime":
        return getOptionalResponseTime()
    else:
        print("NOT IMPLEMENTED YET")
        return None


def wait_and_run(command, delay, parameter=None, condition=None):
    time.sleep(delay)

    if condition is not None:
        averageUtilization = get("averageUtilization")
        basicResponseTime = get("basicResponseTime")
        optResponseTime = get("optResponseTime")
        should_continue = eval(condition)
        if not should_continue:
            return

    if parameter is None:
        command()
    else:
        command(parameter)


class ManagedResource(Manta.Effecting.ManagedResource):
    def sendParameterChanges(self, parameterChanges, current):
        # Not used in this case
        return

    def sendComponentChanges(self, components, current):

        if len(components.components)>0:
            for component in components.components:
                className = component.className
                print(component)

                condition = None

                for p in component.parameters:
                    if p.key == "waitingTime":
                        waitingTime = int(p.value)
                    elif p.key == "condition":
                        condition = p.value
                        condition = condition.replace(".", " ")
                        condition = condition.replace("||", "or")
                        condition = re.sub('(\d+)', r'0.\1', condition)

                global skips
                skips = skips + waitingTime

                print(condition)

                if className == 'RemoveServer':
                    _thread.start_new_thread(wait_and_run, (removeServer, waitingTime))
                elif className == 'AddServer':
                    _thread.start_new_thread(wait_and_run, (addServer, waitingTime))
                elif className == 'SetDimmer':
                    dimmerValue = int(component.parameters[0].value) / 100
                    _thread.start_new_thread(wait_and_run, (setDimmer, waitingTime, dimmerValue, condition))
                elif className == 'IncreaseDimmer':
                    dimmerValue = current_dimmer_value+0.2
                    _thread.start_new_thread(wait_and_run, (setDimmer, waitingTime, dimmerValue, condition))
                elif className == 'DecreaseDimmer':
                    dimmerValue = current_dimmer_value-0.2
                    _thread.start_new_thread(wait_and_run, (setDimmer, waitingTime, dimmerValue, condition))


class Listener:
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info is not None and info.properties[b'type'] == b'Sensor':
            global sensorName
            global sensorHost
            global sensorPort
            sensorName = info.name.replace("._manta._tcp.local.", "")
            sensorHost = socket.gethostbyname(info.server[0:-1])
            sensorPort = info.port


sock = ""

sensorName = ""
sensorHost = ""
sensorPort = 0

zeroconf = Zeroconf()
listener = Listener()
ServiceBrowser(zeroconf, "_manta._tcp.local.", listener)


def sensor_thread():

    while True:
        try:
            global sock
            sock = socket.create_connection(('localhost', 4242))
            getDimmer()
        except Exception as e:
            print("Retry establishing connection")
            time.sleep(1)
            continue
        break

    try:
        arred = lambda x, n: x*(10**n)//1/(10**n)

        with Ice.initialize(sys.argv) as communicator:
            adapter = communicator.createObjectAdapterWithEndpoints("Effector-1", "default -p 10007")
            managed_resource = ManagedResource()
            adapter.add(managed_resource, communicator.stringToIdentity("Effector-1"))
            adapter.activate()

            info = ServiceInfo(
                "_manta._tcp.local.",
                "Effector-1._manta._tcp.local.",
                port=10007,
                properties={'type': 'Effector'},
                server=socket.gethostname().replace(".", "-")+".local."
            )

            global zeroconf
            print("Registering service with info:")
            print(info)
            zeroconf.register_service(info)

            while True:
                try:
                    proxy_string = sensorName + ":default -h " + sensorHost + " -p " + str(sensorPort)
                    base = communicator.stringToProxy(proxy_string)
                    sensor = Manta.Sensing.ISensorPrx.checkedCast(base)
                    break
                except Exception as exception:
                    print("SensorProxy not ready")
                    time.sleep(1)
                    continue

            interval = 15
            while 1:
                try:
                    global skips

                    print("Waiting", interval+skips)
                    time.sleep(interval+skips)

                    if skips is not 0:
                        print("Waiting additional", skips)
                        time.sleep(interval+skips)
                        skips = 0

                    try:
                        dimmer_raw = getDimmer()
                        dimmer = int(round(dimmer_raw, 2) * 100)
                        servers = getServers()
                        activeServers = getActiveServers()
                        optResponseTime = int(round(getOptionalResponseTime(), 2) * 100)
                        maxServers = getMaxServers()
                        totalUtilization = int(arred(getTotalUtilization(), 2) * 100)
                        averageUtilization = int(arred(getAverageUtilization(), 2) * 100)
                        basicResponseTime = int(round(getBasicResponseTime(), 2))
                        data = {
                            "Ctx": {
                                "type": "Context",
                                "dimmer": dimmer,
                                "servers": servers,
                                "activeServers": activeServers,
                                "maxServers": maxServers,
                                "totalUtilization": totalUtilization,
                                "averageUtilization": averageUtilization,
                                "basicResponseTime": basicResponseTime,
                                "optResponseTime": optResponseTime
                            }
                        }

                        global current_dimmer_value
                        current_dimmer_value = dimmer_raw

                        print(data)
                        sensor.receiveSensorData(json.dumps(data))
                    except Exception as e:
                        print(e)
                        print("Error fetching data. Restart...")
                        break
                except ValueError as e:
                    break
    finally:
        print("Closing socket")
        sock.close()
        zeroconf.close()


while True:
    print("Starting sensor thread")
    thread = threading.Thread(target=sensor_thread)
    thread.start()
    thread.join()
