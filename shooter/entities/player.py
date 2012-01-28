from shooter.images import Text
from shooter.texture import Texture

class Character(object):
    def __init__(self):
        self.health = 0.
        self.last_hit_step = None

class Flame(object):
    def __init__(self):
        self.x, self.y = 0, 0
        self.z = .1
        self.texture = Texture('player_flame_1', z=.5)
        self.textures = [Texture('player_flame_1', z=.5), Texture('player_flame_2', z=.5), Texture('player_flame_3', z=.5)]
        self.current_texture_index = 0

class MuzzleFlash(object):
    def __init__(self):
        self.x, self.y = 0, 0
        self.z = .6
        self.texture = Texture("player_shot_effect_1", z=.6)
        self.textures = [Texture('player_shot_effect_1', z=.6), Texture('player_shot_effect_2', z=.6), Texture('player_shot_effect_3', z=.6)]
        self.current_texture_index = 0

class Player(Character):
    def __init__(self):
        super(Player, self).__init__()
        self.x = 50
        self.y = 300
        self.vx = 4
        self.vy = 4

        self.z = .99

        self.radius = 16
        self.texture = Texture("player_ship", z=.8)

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
        self.starting_x = 770
        self.x = self.starting_x
        self.y = 330
        self.z = .5
        self.texture = Texture("boss")

