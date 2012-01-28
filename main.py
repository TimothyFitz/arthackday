import os
import time
import copy
import collections
import math

from OpenGL.GL import *
from OpenGL.arrays import vbo
from numpy import array
from pygame.locals import *
import gutil
import pygame
import pygame.mouse

from shooter.entities.bullet import BulletSet
from shooter.entities.player import Player, Boss, MuzzleFlash, Flame
from shooter.osc.dj import Dj
from shooter.images import Image, Text
from shooter.controller import JoystickServer
from shooter.texture import Texture
from shooter.sms import MessagePoll, TWILIO_MSG_DURATION
from shooter.hitboxes import hitboxes

PLAYER_ATTACK = .03
BOSS_ATTACK = .7
TWILIO_ATTACK = 10.

SHOT_EFFECT_FRAMES = 10

HIT_EFFECT_FRAMES = 1

GAME_OVER_FRAMES = 240

swidth, sheight = 848, 480

#global last_boss_hit_step = None
#global last_player_hit_step = None

class RenderPass(object):
    def __init__(self):
        self.draw_by_texture = collections.defaultdict(set)
    
    def mark_for_draw(self, thing):
        # thing has .x, .y, .texture
        if thing.texture:
            self.draw_by_texture[thing.texture].add(thing)
    
    def render(self):
        for texture, things in sorted(self.draw_by_texture.items(),
                                      key=lambda (texture, things): texture.z):
            glLoadIdentity()
            points = []
            hw, hh = texture.width // 2, texture.height // 2
            for thing in things:
                colors = (1., 1., 1.,)
                global steps
                if hasattr(thing, 'last_hit_step') and steps - HIT_EFFECT_FRAMES <= thing.last_hit_step and steps % 5:
                    colors = (1., .2, .2,)
                points += [
                    [thing.x - hw, thing.y - hh, thing.z,  0,0, colors[0], colors[1], colors[2]],
                    [thing.x + hw, thing.y - hh, thing.z,  1,0, colors[0], colors[1], colors[2]],
                    [thing.x + hw, thing.y + hh, thing.z,  1,1, colors[0], colors[1], colors[2]],
                    [thing.x - hw, thing.y + hh, thing.z,  0,1, colors[0], colors[1], colors[2]],
                ]

            stride = 8*4
            points_vbo = vbo.VBO(array(points, 'f'))

            points_vbo.bind()
            glBindTexture(GL_TEXTURE_2D, texture.id)

            glEnableClientState(GL_COLOR_ARRAY)
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glVertexPointer(3, GL_FLOAT, stride, points_vbo)
            glTexCoordPointer(2, GL_FLOAT, stride, points_vbo + 3*4)
            glColorPointer(3, GL_FLOAT, stride, points_vbo + 5*4)
            glDrawArrays(GL_QUADS, 0, len(points))
            points_vbo.unbind()
            glDisableClientState(GL_TEXTURE_COORD_ARRAY)
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_COLOR_ARRAY)

class Debounce(object):
    def __init__(self, cooldown):
        self.cooldown = cooldown
        self.current = 0
    
    def fire(self):
        if not self.current:
            self.current = self.cooldown
            return True

    def step(self):
        if self.current:
            self.current -= 1

def draw_health_bar(health, y, color):
    glBindTexture(GL_TEXTURE_2D, 0)
    glColor4f(*(color + (0.5,)))
    glRectf(10, y, (swidth - 10) * health, y + 20)
    glColor3f(1,1,1)

_texts = {}
def draw_label(label, x, y, width, height, rotation=0):
    if label not in _texts:
        _texts[label] = Text(label, fontsize=256, color=(255,255,255,255))
    _texts[label].draw(pos=(x, y), width=width, height=height, rotation=rotation)

    
def move_player(player, x, y):
    _test_x = player.x + (x*player.vx)
    _test_y = player.y + (y*player.vy)
    if (_test_x > 0 and _test_x < swidth - 200):
        player.x = _test_x
    if (_test_y > 0 and _test_y < sheight):
        player.y = _test_y

class HitBox(object):
    def __init__(self, entity, json):
        self.x = entity.x + json['offset']['x']
        self.y = entity.y + json['offset']['y']
        self.radius = json['radius']

steps = 0



def main():
    pygame.init()
    gutil.initializeDisplay(swidth, sheight)

    from pygame import display
    print display.list_modes()

    live_dj = Dj()

    player = Player()  # On your own here, but it needs x and y fields.
    boss = Boss()
    muzzle_flash = MuzzleFlash()
    flame = Flame()
    enemy_bullets = BulletSet()

    player_bullets = BulletSet()
    
    space = [Texture("bg/space_%s" % n, z=-100) for n in range(1, 32)]
    start_screens = [Texture("start_screen_%s" % n, z=-100) for n in range(1, 3)]

    class Background(object):
        def __init__(self):
            self.x = swidth // 2
            self.y = sheight // 2
            self.z = 0

        @property
        def texture(self):
            return space[(steps//15) % len(space)]
            
    bg = Background()

    class StartScreen(object):
        def __init__(self):
            self.x = swidth // 2
            self.y = sheight // 2
            self.z = 0
            self.current_texture_index = 0

        @property
        def texture(self):
            return start_screens[(steps//30) % len(start_screens)]

    start_screen = StartScreen()

    boss_weapons = [
        'easy_attack_1.xml',
        'spread_attack.xml',
        'laser_attack.xml',
        'gravity_attack.xml',
        'homing_laser.xml',
        'sweep_attack.xml',
        'flower_attack.xml',
    ]

    global steps
    start = time.time()

    joy = JoystickServer()
    joy.daemon = True
    joy.start()

    done = False

    gun = Debounce(15)
    laser = Debounce(60*5)
    
    last_time = time.time()
    game_tick = 1.0 / 60.0
    time_left = 0.0

    # Start twilio polling
    twilio = MessagePoll()
    twilio.start()
    last_twilio_msg = None
    last_twilio_msg_step = 0

    last_shot_step = None
    last_game_over = -GAME_OVER_FRAMES - 1

    last_boss_break_step = None

    def start_screen_visible():
        return last_game_over is not None and steps - last_game_over > GAME_OVER_FRAMES

    while not done:
        if joy.state.hats:
            hx, hy = joy.state.hats[0]
            move_player(player, hx, hy)

        keys = pygame.key.get_pressed()
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glColor3f(1,1,1)
        glPointSize(10)
        glLoadIdentity()

        rp = RenderPass()

        if not start_screen_visible() and (joy.state.buttons and joy.state.buttons[0]) or keys[pygame.K_z]:
            #if steps % 3:
            muzzle_flash.x = player.x + 85
            muzzle_flash.y = player.y + 6
            if steps % 2 == 0:
                muzzle_flash.current_texture_index += 1
                if muzzle_flash.current_texture_index >= len(muzzle_flash.textures):
                    muzzle_flash.current_texture_index = 0
            muzzle_flash.texture = muzzle_flash.textures[muzzle_flash.current_texture_index]
            rp.mark_for_draw(muzzle_flash)
        else:
            last_shot_step = None

        # Flame.
        flame.x = player.x - 8
        flame.y = player.y
        if steps % 4 == 0:
            flame.current_texture_index += 1
            if flame.current_texture_index >= len(flame.textures):
                flame.current_texture_index = 0
        flame.texture = flame.textures[flame.current_texture_index]

        if start_screen_visible():
            rp.mark_for_draw(start_screen)
        else:
            if boss.health > 0:
                map(rp.mark_for_draw, enemy_bullets)
                rp.mark_for_draw(boss)

            if player.health > 0:
                map(rp.mark_for_draw, player_bullets)
                rp.mark_for_draw(player)
                rp.mark_for_draw(flame)
            rp.mark_for_draw(bg)

        glLoadIdentity()
        rp.render()

        if start_screen_visible():
            pass
        elif boss.health <= 0:
            draw_label('YOU KILLED THE DJ', swidth / 2 - 150, sheight / 2, 300, 40)
            if last_game_over is None:
                last_game_over = steps
        elif player.health <= 0:
            draw_label('GAME OVER', swidth / 2 - 100, sheight / 2, 200, 50)
            if last_game_over is None:
                last_game_over = steps
        else:
            # Health bars.
            draw_health_bar(player.health / 100., sheight - 30, (0., 0.8, 0.))
            draw_health_bar(boss.health / 100., 10, (0.8, 0., 0.))
            draw_label("PLAYER", 15, sheight - 29, 52, 16)
            draw_label("BOSS", 15, 11, 35, 16)

        # Twilio.
        if not start_screen_visible():
            TWILIO_WIDTH = (210, 260,)
            draw_label("Tired of this DJ? Shoot him.",
                    swidth - TWILIO_WIDTH[0] - 10, 60, TWILIO_WIDTH[0], 16)
            draw_label("TEXT  (503) 8-CANVAS", swidth - TWILIO_WIDTH[1] - 10, 34, TWILIO_WIDTH[1], 23)        

        if ((steps - last_twilio_msg_step) % (TWILIO_MSG_DURATION * 60)
                and last_twilio_msg is not None):
            #parts = msg[]
            offset = 0
            line_len = 40
            char_w = 12
            #for m in msg[offset:offset + line_len]:
            while True:
                if offset > len(msg):
                    break
                end = min(len(msg), offset + line_len)
                m = msg[offset:offset + line_len]
                w = len(m) * char_w
                h = 23
                rot = math.sin(steps / 6.) * (50 / len(m))
                x = swidth - ((line_len * char_w) + (250 - (steps - last_twilio_msg_step)))
                y = (sheight / 2) + 30
                y -= (h + 3) * (offset / line_len)
                draw_label(m, x, y, w, 23, rotation=rot)
                offset += line_len
        else:
            if last_twilio_msg is not None:
                boss.health -= TWILIO_ATTACK
            last_twilio_msg_step = 0
            last_twilio_msg = None
        if steps % 60 == 0 and twilio.messages:
            msg = twilio.messages.pop()
            last_twilio_msg_step = steps
            last_twilio_msg = msg

        # Boss movement.
        #print live_dj.activity_level()
        #print 75. / (live_dj.activity_level() + 1)
        if live_dj.activity_level() > 2 or abs(boss.x - boss.starting_x) > 3:
            if last_boss_break_step is None:
                last_boss_break_step = steps
            boss.x = int(math.cos((steps - last_boss_break_step + 30) / 30.) * 50 + boss.starting_x)
        else:
            last_boss_break_step = None

        boss.y = math.sin(steps / 75.) * 110 + (sheight / 2)

        pygame.display.flip()

        curtime = time.time()
        time_left += curtime - last_time
        last_time = curtime

        while time_left >= game_tick:
            time_left -= game_tick

            for hitbox in hitboxes['player_ship'].values():
                hitbox = HitBox(player, hitbox)
                if boss.health > 0 and enemy_bullets.collides(hitbox):
                    player.health -= BOSS_ATTACK
                    player.last_hit_step = steps

            for hitbox in hitboxes['boss_ship'].values():
                hitbox = HitBox(boss, hitbox)
                if player.health > 0 and player_bullets.collides(hitbox):
                    boss.health -= PLAYER_ATTACK
                    boss.last_hit_step = steps

            enemy_bullets.step(swidth, sheight, 100)
            player_bullets.step(swidth, sheight, 100)

            eventlist = pygame.event.get()
            for event in eventlist:
                if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                    done = True
        
            if player.health > 0 and (joy.state.buttons and joy.state.buttons[0]) or keys[pygame.K_z]:
                if gun.fire():
                    player_bullets.load("player_shot.xml", source=player, target=boss)
                    last_shot_step = steps
        
            if player.health > 0 and (joy.state.buttons and joy.state.buttons[1]) or keys[pygame.K_x]:
                if laser.fire():
                    player_bullets.load("player_laser.xml", source=player, target=boss)

            player_bullets.update_roots(player.x + 30,
                                        player.y + 2)

            gun.step()
            laser.step()

            if keys[pygame.K_RIGHT]:
                move_player(player, 1, 0)
            elif keys[pygame.K_LEFT]:
                move_player(player, -1, 0)
            
            if keys[pygame.K_UP]:
                move_player(player, 0, 1)
            elif keys[pygame.K_DOWN]:
                move_player(player, 0, -1)

            if start_screen_visible() and keys[pygame.K_RETURN] and (player.health <= 0 or boss.health <= 0):
                player.health = 100.
                boss.health = 100.
                last_game_over = None

            if keys[pygame.K_q]:
                time.sleep(1)

            steps += 1
        
            if not start_screen_visible() and steps % 15 == 0:
                activity_level = live_dj.activity_level()
                if activity_level:
                    enemy_bullets.load(boss_weapons[activity_level], source=boss, target=player)
    
    print "FPS:", steps / (time.time() - start)

if __name__ == '__main__':
    main()

