'''
Provides cleaned-up state info on what the DJ's doing.
'''
from shooter.osc.config import PORT
from shooter.osc.server import BaseOscServer, Fader as OscFader
from datetime import timedelta

from copy import copy


class OscServer(BaseOscServer):
    def __init__(self, dj, port):
        super(OscServer, self).__init__(port)
        self.dj = dj

    def left(self, pos):
        #print 'left callback!'
        self.dj.left.pos = pos

    def right(self, pos):
        #print 'right callback!',
        self.dj.right.pos = pos
        #print self.dj.right.pos

    def fader(self, pos):
        self.dj.fader.pos = pos


class Device(object):
    def __init__(self, dj):
        self.dj = dj


class Fader(Device, OscFader):
    def __init__(self, dj):
        super(Fader, self).__init__(dj)
        self.pos = 0.


class Record(Device):
    def __init__(self, dj):
        super(Record, self).__init__(dj)
        self.pos = timedelta(0)

class DjSnapshot(object):
    def __init__(self, dj):
        self.left = copy(dj.left)
        self.right = copy(dj.right)
        self.fader = copy(dj.fader)

class Dj(object):
    def __init__(self):
        ''' Connects to the OSC server. Provides state info. '''
        self._server = OscServer(self, PORT)
        
        self.left  = Record(self)
        self.right = Record(self)
        self.fader = Fader(self)

    def snapshot(self):
        return DjSnapshot(self)

def main():
    import time
    from shooter.osc.config import PORT
    dj = Dj()
    while True:
        print 'L:{0}\tR:{1}\tF_L:{2}\tF_R:{3}'.format(
            dj.left.pos, dj.right.pos, dj.fader.left, dj.fader.right)
        time.sleep(1)

    raw_input("ctrl-c to quit\n")

if __name__ == '__main__':
    main()

