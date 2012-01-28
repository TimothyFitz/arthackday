from shooter.images import Image, Text

class Player(object):
    def __init__(self):
        self.x = 400
        self.y = 20
        self.radius = 16

        self.health = 100
        self._last_health = self.health
        self._health_text = None

    @property
    def health_text(self):
        if not self._health_text or self._last_health != self.health:
            self._health_text = Text("Health: {0}%".format(self.health).ljust(12),
                                     fontsize=256,
                                     color=(255,255,255,255))
        return self._health_text

