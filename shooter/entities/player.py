from shooter.images import Text
from shooter.texture import Texture

class Character(object):
    def __init__(self):
        self.health = 100

class Player(Character):
    def __init__(self):
        super(Player, self).__init__()
        self.x = 50
        self.y = 300
        self.vx = 4
        self.vy = 4
        
        self.z = 0.99
        
        self.radius = 16
        self.texture = Texture("player_ship")

        self._health_text = None
        #self._last_health = self.health

    #@property
    #def health_text(self):
    #    if not self._health_text or self._last_health != self.health:
    #        self._health_text = Text("Health: {0}%".format(self.health).ljust(12),
    #                                 fontsize=256,
    #                                 color=(255,255,255,255))
    #    return self._health_text

class Boss(Character):
    def __init__(self):
        super(Boss, self).__init__()
        self.x = 750
        self.y = 330
        self.z = 0.5
        self.texture = Texture('boss')
