import socket
import Ice
import Manta
import json
import time


class ManagerSensor:

    interval = 15

    def __init__(self):
        self.sensorName = "Sensor-1"
        self.sensorHost = "127.0.0.1"
        self.sensorPort = 10001

        while True:
            try:
                self.socket = socket.create_connection(('localhost', 4242))
                self.getDimmer()
            except Exception as e:
                print("Retry establishing connection")
                time.sleep(1)
                continue
            break

        with Ice.initialize() as communicator:
            while True:
                try:
                    proxy_string = self.sensorName + ":default -h " + self.sensorHost + " -p " + str(self.sensorPort)
                    base = communicator.stringToProxy(proxy_string)
                    self.sensor = Manta.Sensing.ISensorPrx.checkedCast(base)
                    break
                except Exception as exception:
                    print("SensorProxy not ready")
                    time.sleep(1)
                    continue

        while 1:
            try:
                print("Waiting", self.interval)
                time.sleep(self.interval)

                try:
                    activeServers = self.getActiveServers()
                    maxServers = self.getMaxServers()
                    basicResponseTime = int(round(self.getBasicResponseTime(), 2))
                    data = {
                        "Mngr": {
                            "type": "Manager",
                            "activeServers": activeServers,
                            "maxServers": maxServers,
                            "responseTime": basicResponseTime
                        }
                    }

                    print(data)
                    self.sensor.receiveSensorData(json.dumps(data))
                except Exception as e:
                    print(e)
                    print("Error fetching data. Restart...")
                    break
            except ValueError as e:
                break

    def sendCommand(self, command):
        command = command.encode()
        self.socket.sendall(command)
        data = self.socket.recv(4096)
        data = data.decode()
        data = data.strip()
        return data

    def getActiveServers(self):
        return int(self.sendCommand('get_active_servers\n'))

    def getMaxServers(self):
        return int(self.sendCommand('get_max_servers\n'))

    def getBasicThroughput(self):
        return float(self.sendCommand('get_basic_throughput\n'))

    def getDimmer(self):
        return float(self.sendCommand('get_dimmer\n'))


if __name__ == '__main__':
    ManagerSensor()