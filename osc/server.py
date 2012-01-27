import sys
from functools import wraps
import liblo
from liblo import make_method
from datetime import timedelta
import logger

log = logger.logger('osc')


def transform(transformer):
    def decorator(fn):
        @wraps(fn)
        def wrapper(self, args):
            (pos,) = args
            pos = transformer(pos)
            fn(self, pos)
        return wrapper
    return decorator

def ms_transform(pos):
    return timedelta(ms=pos)


class Fader(object):
    def __init__(self, pos):
        ''' `pos` is between 0. and 1. '''
        if pos < 0 or pos > 1:
            raise ValueError('fader pos is out of range')
        self._pos = pos

    @property
    def left(self):
        return 1. - self._pos

    @property
    def right(self):
        return self._pos
 

class OscServer(object):
    def __init__(self, port):
        self._port = port

        try:
            self._server = liblo.Server(port)
        except liblo.ServerError, err:
            print unicode(err)
            sys.exit(1)

        for device, name in [('record', 'left',), 
                             ('record', 'right',),
                             ('mixer', 'fader',),]:
            path = '/scratch/{0}/{1}'.format(device, name)
            method = getattr(self, '_' + name)
            server.add_method(path, 'f', method)

    @transform(ms_transform)
    def _left(self, pos):
        self.left(pos)

    @transform(ms_transform)
    def _right(self, pos):
        self.right(pos)

    @transform(Fader)
    def _fader(self, pos):
        self.fader(pos)

    def left(self, pos):
        ''' Absolute position in ms. '''
        log.info('left: ' + str(pos))

    def right(self, pos):
        ''' Absolute position in ms. '''
        log.info('right: ' + str(pos))

    def fader(self, fader):
        ''' Between 0. and 1. '''
        log.info('fader: {0}, {1}'.format(fader.left, fader.right))

