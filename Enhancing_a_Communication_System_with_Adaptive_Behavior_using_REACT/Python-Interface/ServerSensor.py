import socket
import Ice
import Manta
import json
import time
import sys


class ServerSensor:

    arred = lambda x, n: x * (10 ** n) // 1 / (10 ** n)  # Function for limiting a float to two decimal places
    interval = 15

    def __init__(self):
        if len(sys.argv) is 0:
            print("You have to pass the server id as command line parameter")
            exit(1)

        self.server_id = sys.argv[0]

        while True:
            try:
                self.socket = socket.create_connection(('localhost', 4242))
                self.sendCommand('get_dimmer\n')
            except Exception as e:
                print("Retry establishing connection")
                time.sleep(1)
                continue
            break

        with Ice.initialize as communicator:
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

        while True:
            try:
                print("Waiting", self.interval)
                time.sleep(self.interval)

                try:
                    utilization = int(self.arred(self.getUtilization(), 2) * 100)
                    data = {
                        "Srv" + str(self.server_id) : {
                            "type": "Server",
                            "utilization": utilization
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

    def getUtilization(self):
        return float(self.sendCommand('get_utilization server' + str(self.server_id) + "\n"))