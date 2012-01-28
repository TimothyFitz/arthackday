import sys
from functools import wraps
import liblo
from liblo import make_method
from datetime import timedelta
from shooter import logger

log = logger.logger('osc')


def transform(transformer):
    def decorator(fn):
        @wraps(fn)
        def wrapper(self, path, args):
            (pos,) = args
            pos = transformer(pos)
            fn(self, pos)
        return wrapper
    return decorator

def ms_transform(pos):
    return timedelta(milliseconds=pos)

class FaderPropertiesMixin(object):
    @property
    def left(self):
        return 1. - self.pos

    @property
    def right(self):
        return self.pos

class Fader(FaderPropertiesMixin):
    def __init__(self, pos):
        ''' `pos` is between 0. and 1. '''
        if pos < 0 or pos > 1:
            raise ValueError('fader pos is out of range: ' + str(pos))
        self.pos = pos


class BaseOscServer(object):
    def __init__(self, port):
        self._port = port

        try:
            self._server = liblo.ServerThread(port)
        except liblo.ServerError, err:
            print unicode(err)
            sys.exit(1)

        for device, name in [('record', 'left',), 
                             ('record', 'right',),
                             ('mixer',  'fader',),]:
            path = '/scratch/{0}/{1}'.format(device, name)
            method = getattr(self, '_' + name)
            self._server.add_method(path, 'f', method)

        self._server.start()

    @transform(ms_transform)
    def _left(self, pos):
        #log.info('left: ' + str(pos))
        self.left(pos)

    @transform(ms_transform)
    def _right(self, pos):
        #log.info('right: ' + str(pos))
        self.right(pos)

    @transform(Fader)
    def _fader(self, fader):
        log.info('fader: {0}, {1}'.format(fader.left, fader.right))
        self.fader(fader)

    def left(self, pos):
        ''' Absolute position in ms. '''

    def right(self, pos):
        ''' Absolute position in ms. '''

    def fader(self, fader):
        ''' Between 0. and 1. '''


def main():
    from shooter.osc.config import PORT
    server = BaseOscServer(PORT)
    raw_input("ctrl-c to quit\n")

if __name__ == '__main__':
    main()

