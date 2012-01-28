import os
import time
import copy
import collections

from OpenGL.GL import *
from OpenGL.arrays import vbo
from numpy import array
from pygame.locals import *
import gutil
import pygame
import pygame.mouse

from shooter.entities.bullet import BulletSet
from shooter.entities.player import Player, Boss
from shooter.osc.dj import Dj
from shooter.images import Image, Text
from shooter.controller import JoystickServer
from shooter.texture import Texture

swidth, sheight = 446*2, 240*2

class RenderPass(object):
    def __init__(self):
        self.draw_by_texture = collections.defaultdict(set)
    
    def mark_for_draw(self, thing):
        # thing has .x, .y, .texture
        if thing.texture:
            self.draw_by_texture[thing.texture].add(thing)
    
    def render(self):
        for texture, things in self.draw_by_texture.items():
            glLoadIdentity()
            points = []
            hw, hh = texture.width // 2, texture.height // 2
            for thing in things:
                points += [
                    [thing.x - hw, thing.y - hh, thing.z,  0,0],
                    [thing.x + hw, thing.y - hh, thing.z,  1,0],
                    [thing.x + hw, thing.y + hh, thing.z,  1,1],
                    [thing.x - hw, thing.y + hh, thing.z,  0,1]
                ]

            stride = 5*4
            points_vbo = vbo.VBO(array(points, 'f'))

            points_vbo.bind()
            glBindTexture(GL_TEXTURE_2D, texture.id)
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glVertexPointer(3, GL_FLOAT, stride, points_vbo)
            glTexCoordPointer(2, GL_FLOAT, stride, points_vbo + 3*4)
            glDrawArrays(GL_QUADS, 0, len(points))
            points_vbo.unbind()
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_TEXTURE_COORD_ARRAY)

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
def draw_label(label, x, y, width, height):
    if label not in _texts:
        _texts[label] = Text(label, fontsize=256, color=(255,255,255,255))
    _texts[label].draw(pos=(x, y), width=width, height=height)

def main():
    pygame.init()
    gutil.initializeDisplay(swidth, sheight)

    from pygame import display
    print display.list_modes()

    live_dj = Dj()

    player = Player()  # On your own here, but it needs x and y fields.
    boss = Boss()
    enemy_bullets = BulletSet()
    enemy_bullets.load("homing_laser.xml", source=boss, target=player)
    
    player_bullets = BulletSet()

    steps = 0
    start = time.time()

    joy = JoystickServer()
    joy.daemon = True
    joy.start()

    done = False

    gun = Debounce(15)
    laser = Debounce(60*5)

    while not done:
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glColor3f(1,1,1)
        glPointSize(10)
        glLoadIdentity()

        # Health bars.
        draw_health_bar(player.health / 100., sheight - 30, (0., 0.8, 0.))
        draw_health_bar(boss.health / 100., 10, (0.8, 0., 0.))
        draw_label("PLAYER", 15, sheight - 29, 52, 16)
        draw_label("BOSS", 15, 11, 35, 16)

        # Twilio.
        TWILIO_WIDTH = (210, 260,)
        draw_label("Tired of this DJ? Shoot him.",
                   swidth - TWILIO_WIDTH[0] - 10, 60, TWILIO_WIDTH[0], 16)
        draw_label("TEXT  (503) 8-CANVAS", swidth - TWILIO_WIDTH[1] - 10, 34, TWILIO_WIDTH[1], 23)

        rp = RenderPass()
        map(rp.mark_for_draw, enemy_bullets)
        map(rp.mark_for_draw, player_bullets)

        rp.mark_for_draw(player)
        rp.mark_for_draw(boss)

        rp.render()

        pygame.display.flip()

        if enemy_bullets.collides(player):
            player.health -= 0.5

        if player_bullets.collides(boss):
            boss.health -= 1

        enemy_bullets.step(swidth, sheight, 100)
        player_bullets.step(swidth, sheight, 100)

        eventlist = pygame.event.get()
        for event in eventlist:
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                done = True
                
        if joy.state.hats:
            hx, hy = joy.state.hats[0]
            player.x += hx*player.vx
            player.y += hy*player.vy

        keys = pygame.key.get_pressed()
        
        if (joy.state.buttons and joy.state.buttons[0]) or keys[pygame.K_z]:
            if gun.fire():
                player_bullets.load("player_shot.xml", source=player, target=boss)
        
        if (joy.state.buttons and joy.state.buttons[1]) or keys[pygame.K_x]:
            if laser.fire():
                player_bullets.load("player_laser.xml", source=player, target=boss)

        player_bullets.update_roots(player)

        gun.step()
        laser.step()

        if keys[pygame.K_RIGHT]:
            player.x += player.vx
        elif keys[pygame.K_LEFT]:
            player.x -= player.vx
            
        if keys[pygame.K_UP]:
            player.y += player.vy
        elif keys[pygame.K_DOWN]:
            player.y -= player.vy
        
        if keys[pygame.K_q]:
            time.sleep(1)
        
        steps += 1
        
        if steps % 120 == 0:
            print "Bullets:", len(enemy_bullets), len(player_bullets)
    
    print "FPS:", steps / (time.time() - start)

if __name__ == '__main__':
    main()
