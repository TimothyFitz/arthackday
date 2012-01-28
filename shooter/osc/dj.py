'''
Provides cleaned-up state info on what the DJ's doing.
'''
from shooter.osc import config
from shooter.osc.server import BaseOscServer, FaderPropertiesMixin
from datetime import timedelta
import time
from copy import copy


def td_to_microseconds(td):
    return td.microseconds + (td.seconds + td.days * 86400) * 1000000


class OscServer(BaseOscServer):
    def __init__(self, dj, port):
        super(OscServer, self).__init__(port)
        self.dj = dj

    def left(self, pos):
        self.dj.left.update(pos)

    def right(self, pos):
        self.dj.right.update(pos)

    def fader(self, pos):
        self.dj.fader.update(pos)


class Device(object):
    def __init__(self, dj):
        super(Device, self).__init__(dj)
        self.dj = dj

    def update(self, pos):
        self._last_pos = self.pos
        self.pos = pos


class DirChangeMixin(object):
    def __init__(self, *args, **kwargs):
        super(DirChangeMixin, self).__init__()
        self._dir_changes = []
        self._last_dir = True

    def _cull_dir_changes(self):
        ts = time.time()
        # Cull them.
        for i, e in enumerate(self._dir_changes):
            if e[0] < ts - config.DIR_CHANGE_SECONDS: # last N seconds only
                break
        else:
            i = None
        if i is not None:
            try:
                self._dir_changes = self._dir_changes[i + 1:]
            except IndexError:
                self._dir_changes = []

    def _update_dir(self, pos):
        ts = time.time()
        direction = self._last_pos < pos
        if direction != self._last_dir:
            self._dir_changes.append((ts, direction,))
        self._last_dir = direction
        self._cull_dir_changes()

    def dir_changes(self):
        ''' returns the # of direction changes in the last N seconds. '''
        self._cull_dir_changes()
        return len(self._dir_changes)

    def activity_level(self):
        #print self, self.dir_changes()
        for level, changes_per_s in enumerate([v*config.DJ_DIFFICULTY for v in config.DIR_CHANGE_BUCKETS]):
            if self.dir_changes() / float(config.DIR_CHANGE_SECONDS) < changes_per_s:
                print level
                return level
        print level+1
        return level + 1


class Fader(Device, FaderPropertiesMixin, DirChangeMixin):
    def __init__(self, dj):
        super(Fader, self).__init__(dj)
        self.pos = 0.
        self._last_pos = 0.
        self._last_dir = True

    def update(self, pos):
        super(Fader, self,).update(pos)
        self._update_dir(pos)


class Record(Device, DirChangeMixin):
    def __init__(self, dj, side):
        super(Record, self).__init__(dj)
        self.pos = timedelta(0)
        self._last_pos = timedelta(0)
        self.side = side
        #self._last_sample_ts = None

    def update(self, pos):
        super(Record, self,).update(pos)
        # Direction changes.
        # Skip if fader is off.
        if (config.FADER_THRESHOLD is None
                or getattr(self.dj.fader, self.side) > config.FADER_THRESHOLD):
            self._update_dir(pos)

        #velocity = self._last_pos
        #self._last_sample_ts = ts


class DjSnapshot(object):
    def __init__(self, dj):
        self.left  = copy(dj.left)
        self.right = copy(dj.right)
        self.fader = copy(dj.fader)
        self.level = dj.activity_level()

class Dj(object):
    def __init__(self):
        ''' Connects to the OSC server. Provides state info. '''
        self._server = OscServer(self, config.PORT)

        self.left  = Record(self, 'left')
        self.right = Record(self, 'right')
        self.fader = Fader(self)

    def snapshot(self):
        return DjSnapshot(self)

    def activity_level(self):
        level = self.right.activity_level() # + self.fader.activity_level()
        return int(level)


def main():
    dj = Dj()
    while True:
        print 'L:{0}\tR:{1}\tF_L:{2}\tF_R:{3}'.format(
            dj.left.pos, dj.right.pos, dj.fader.left, dj.fader.right)
        time.sleep(1)

    raw_input("ctrl-c to quit\n")

if __name__ == '__main__':
    main()

