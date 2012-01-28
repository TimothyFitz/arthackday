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
            for thing in things:
                points += [
                [thing.x, thing.y, 0,  0,0],
                [thing.x+texture.width,thing.y,0,  1,0],
                [thing.x+texture.width,thing.y+texture.height,0,  1,1],
                [thing.x,thing.y+texture.height,0,  0,1]
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

def main():
    pygame.init()
    swidth, sheight = 446*2, 240*2
    gutil.initializeDisplay(swidth, sheight)

    live_dj = Dj()

    player = Player()  # On your own here, but it needs x and y fields.
    boss = Boss()
    enemy_bullets = BulletSet()
    enemy_bullets.load("gravity_attack.xml", source=boss, target=player)
    
    player_bullets = BulletSet()
    
    steps = 0
    start = time.time()

    joy = JoystickServer()
    joy.daemon = True
    joy.start()

    done = False

    gun = Debounce(15)

    while not done:
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1,1,1)
        glPointSize(10)
        glLoadIdentity()

        enemy_bullets.step()
        player_bullets.step()

        # Health etc text
        player.health_text.draw(pos=(100,20), width=200,height=36)

        rp = RenderPass()
        map(rp.mark_for_draw, enemy_bullets)
        map(rp.mark_for_draw, player_bullets)

        rp.mark_for_draw(player)
        rp.mark_for_draw(boss)

        rp.render()

        pygame.display.flip()

        if enemy_bullets.collides(player):
            # Handle this less awkwardly
            #done = True
            player.health -= 1

        enemy_bullets.cull(swidth, sheight, 100)
        player_bullets.cull(swidth, sheight, 100)

        eventlist = pygame.event.get()
        for event in eventlist:
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                done = True
                
        if joy.state.hats:
            hx, hy = joy.state.hats[0]
            player.x += hx*4
            player.y += hy*4
        
        if any(joy.state.buttons):
            if gun.fire():
                player_bullets.load("player_basic_attack.xml", source=player, target=boss)

        gun.step()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            player.x += 1
        elif keys[pygame.K_LEFT]:
            player.x -= 1
        elif keys[pygame.K_UP]:
            player.y += 1
        elif keys[pygame.K_DOWN]:
            player.y -= 1
        
        steps += 1
    
    print "FPS:", steps / (time.time() - start)

if __name__ == '__main__':
    main()
