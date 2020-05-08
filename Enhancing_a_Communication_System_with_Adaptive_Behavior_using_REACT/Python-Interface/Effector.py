import socket
import Ice
import Manta
import time


class Effector(Manta.Effecting.ManagedResource):

    name = "SWIM-Effector"
    port = 10006

    def __init__(self):
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
            adapter = communicator.createObjectAdapterWithEndpoints(self.name, "default -p " + str(self.port))
            managed_resource = self
            adapter.add(managed_resource, communicator.stringToIdentity(self.name))
            adapter.activate()
            print(self.name + " started")

    def sendCommand(self, command):
        command = command.encode()
        self.socket.sendall(command)
        data = self.socket.recv(4096)
        data = data.decode()
        data = data.strip()
        return data

    def addServer(self):
        result = self.sendCommand('add_server\n')
        return result == 'OK'

    def removeServer(self):
        result = self.sendCommand('remove_server\n')
        return result == 'OK'

    def setDimmer(self, dimmer):
        result = self.sendCommand('set_dimmer ' + str(dimmer) + '\n')
        return result == 'OK'

    def sendParameterChanges(self, parameterChanges, current):
        # Not used in this case
        return

    def sendComponentChanges(self, components, current):
        if len(components.components)>0:
            for component in components.components:
                className = component.className
                print(component)

                if className == 'ServerRemover':
                    self.removeServer()
                elif className == 'ServerLauncher':
                    self.addServer()
                elif className == 'Attributes':
                    dimmerValue = int(component.parameters[0].value) / 100
                    self.setDimmer(dimmerValue)

