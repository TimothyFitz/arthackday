'''
Provides cleaned-up state info on what the DJ's doing.
'''

from config import PORT
from server import OscServer

class Dj(object):
    def __init__(self):
        ''' Connects to the OSC server. '''
        self._server = OscServer(PORT)



