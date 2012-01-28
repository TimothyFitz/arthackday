import socket
import threading
import json

class Joystate(object):
    def __init__(self, state):
        self.axis = state.get('a', [])
        self.buttons = state.get('b', [])
        self.hats = state.get('h', [])


class JoystickServer(threading.Thread):
    state = Joystate({})
    
    def run(self):
        UDP_IP="10.211.55.2"
        UDP_PORT=17171

        sock = socket.socket( socket.AF_INET, # Internet
                              socket.SOCK_DGRAM ) # UDP
        sock.bind( (UDP_IP,UDP_PORT) )

        print "Listening for UDP data (joystickserver)"
        while True:
            data, addr = sock.recvfrom(1024)
            try:
                cooked_data = json.loads(data)
            except:
                pass
            else:
                self.state = Joystate(cooked_data)
            