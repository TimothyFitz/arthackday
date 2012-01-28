from shooter.images import Text
from shooter.texture import Texture

class Player(object):
    def __init__(self):
        self.x = 50
        self.y = 300
        self.vx = 4
        self.vy = 4
        self.radius = 16
        self.texture = Texture("player_ship")

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

class Boss(object):
    def __init__(self):
        self.x = 750
        self.y = 330
        self.texture = None