import socket
import threading

import Ice
import Manta
import json
import time

# SWIM only allows a single socket connection, thus we use one shared synchronized socket
def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


class SocketManager():
    def __init__(self, host):
        self.host = host
        while True:
            try:
                self.socket = socket.create_connection((host, 4242))
                self.getDimmer()
            except Exception as e:
                print("Retry establishing connection")
                time.sleep(1)
                continue
            break

    @synchronized
    def sendCommand(self, command):
        try:
            command = command.encode()
            self.socket.sendall(command)
            data = self.socket.recv(4096)
            data = data.decode()
            data = data.strip()
            return data
        except Exception as exception:
            print(exception)

    # Manager Sensor
    def getActiveServers(self):
        return int(self.sendCommand('get_active_servers\n'))

    def getMaxServers(self):
        return int(self.sendCommand('get_max_servers\n'))

    def getBasicResponseTime(self):
        return float(self.sendCommand('get_basic_rt\n'))

    def getOptionalResponseTime(self):
        return float(self.sendCommand('get_opt_rt\n'))

    def getBasicThroughput(self):
        return float(self.sendCommand('get_basic_throughput\n'))

    def getOptionalThroughput(self):
        return float(self.sendCommand('get_opt_throughput\n'))

    def getDimmer(self):
        return float(self.sendCommand('get_dimmer\n'))

    def getAverageResponseTime(self):
        basicTput = self.getBasicThroughput()
        optTput = self.getOptionalThroughput()
        avgResponseTime = basicTput * self.getBasicResponseTime() + optTput * self.getOptionalResponseTime() / (
                    basicTput + optTput)
        return avgResponseTime
    # Manager Sensor

    # ServerSensor

    def getUtilization(self, server_id):
        return float(self.sendCommand('get_utilization server' + str(server_id) + "\n"))

    # ServerSensor

    # Effector

    def addServer(self):
        result = self.sendCommand('add_server\n')
        return result == 'OK'

    def removeServer(self):
        result = self.sendCommand('remove_server\n')
        return result == 'OK'

    def setDimmer(self, dimmer):
        result = self.sendCommand('set_dimmer ' + str(dimmer) + '\n')
        return result == 'OK'

    # Effector

class ManagerSensor:

    interval = 15
    communicator = Ice.initialize()

    def __init__(self, socket_manager):
        self.socketManager = socket_manager
        self.sensorName = "Sensor-1"
        self.sensorHost = self.socketManager.host
        self.sensorPort = 10001

    def start(self):
        while True:
            try:
                proxy_string = self.sensorName + ":default -h " + self.sensorHost + " -p " + str(self.sensorPort)
                base = self.communicator.stringToProxy(proxy_string)
                self.sensor = Manta.Sensing.ISensorPrx.checkedCast(base)
                break
            except Exception as exception:
                print("SensorProxy not ready")
                time.sleep(1)
                continue

        while True:
            try:
                try:
                    activeServers = self.socketManager.getActiveServers()
                    maxServers = self.socketManager.getMaxServers()
                    responseTime = int(round(self.socketManager.getAverageResponseTime()*100, 2))
                    data = {
                        "Mngr": {
                            "type": "Manager",
                            "activeServers": activeServers,
                            "maxServers": maxServers,
                            "responseTime": responseTime
                        }
                    }

                    print(data)
                    self.sensor.receiveSensorData(json.dumps(data))
                except Exception as e:
                    print(e)
                    print("Error fetching data. Restart...")
                    break

                print("Waiting", self.interval)
                time.sleep(self.interval)
            except ValueError as e:
                break


class ServerSensor:

    interval = 15
    communicator = Ice.initialize()

    def __init__(self, socket_manager, server_id):
        self.socketManager = socket_manager
        self.sensorName = "Sensor-1"
        self.sensorHost = self.socketManager.host
        self.sensorPort = 10001
        self.server_id = server_id

    def start(self):
        while True:
            try:
                proxy_string = self.sensorName + ":default -h " + self.sensorHost + " -p " + str(self.sensorPort)
                base = self.communicator.stringToProxy(proxy_string)
                self.sensor = Manta.Sensing.ISensorPrx.checkedCast(base)
                break
            except Exception as exception:
                print("SensorProxy not ready")
                time.sleep(1)
                continue

        while True:
            arred = lambda x, n: x * (10 ** n) // 1 / (10 ** n)  # Function for limiting a float to two decimal places
            try:
                try:
                    utilization = int(arred(self.socketManager.getUtilization(self.server_id), 2) * 100)
                    data = {
                        "Srv" + str(self.server_id) : {
                            "type": "Server",
                            "utilization": utilization
                        }
                    }

                    print(data)
                    self.sensor.receiveSensorData(json.dumps(data))

                    print("Waiting", self.interval)
                    time.sleep(self.interval)
                except Exception as e:
                    print(e)
                    print("Error fetching data. Restart...")
                    break
            except ValueError as e:
                break


class Effector(Manta.Effecting.ManagedResource):
    name = "SWIM-Effector"
    port = 10006
    communicator = Ice.initialize()

    def __init__(self, socketManager):
        self.socketManager = socketManager

    def start(self):
        adapter = self.communicator.createObjectAdapterWithEndpoints(self.name, "default -p " + str(self.port))
        managed_resource = self
        adapter.add(managed_resource, self.communicator.stringToIdentity(self.name))
        adapter.activate()
        print(self.name + " started")

    def sendParameterChanges(self, parameterChanges, current):
        # Not used in this case
        return

    def sendComponentChanges(self, components, current):
        if len(components.components) > 0:
            for component in components.components:
                className = component.className
                print(component)

                if className == 'ServerRemover':
                    self.socketManager.removeServer()
                elif className == 'ServerLauncher':
                    self.socketManager.addServer()
                elif className == 'Attributes':
                    dimmerValue = int(component.parameters[0].value) / 100
                    self.socketManager.setDimmer(dimmerValue)


if __name__ == '__main__':
    socketManager = SocketManager("172.16.191.129")

    effector = Effector(socketManager)

    managerSensor = ManagerSensor(socketManager)

    serverSensor1 = ServerSensor(socketManager, 1) # Sensor of Server 1

    effectorThread = threading.Thread(target=effector.start)
    managerSensorThread = threading.Thread(target=managerSensor.start)
    serverSensor1Thread = threading.Thread(target=serverSensor1.start)

    effectorThread.start()
    managerSensorThread.start()
    serverSensor1Thread.start()

    effectorThread.join()
    managerSensorThread.join()
    serverSensor1Thread.join()