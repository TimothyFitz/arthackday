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
from shooter.entities.player import Player
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

def main():
    pygame.init()
    swidth, sheight = 446*2, 240*2
    gutil.initializeDisplay(swidth, sheight)

    live_dj = Dj()

    player = Player()  # On your own here, but it needs x and y fields.
    player.x = 50
    player.y = 300
    bullets = BulletSet.load("gravity_attack.xml", (750,300), target=player)


    joy = JoystickServer()
    joy.daemon = True
    joy.start()
    
    done = False

    cow = Texture('cow')
    blue_round = Texture('bullets/12px-blue-round')

    
    last_dj = live_dj.snapshot()
    last_time = time.time()

    while not done:
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1,1,1)
        glPointSize(10)
        glLoadIdentity()

        current_dj = live_dj.snapshot()
        current_time = time.time()

        V = 1000 # pixels / s

        td = (current_dj.right.pos - last_dj.right.pos).total_seconds() # - (current_time - last_time)
        d = td * V

        print td, d
        
        bullets.root.x += d
        if bullets.root.x < 0:
            bullets.root.x = 0
        if bullets.root.x > swidth:
            bullets.root.x = swidth
        bullets.step()

        last_dj = current_dj
        last_time = current_time

        # Health etc text
        player.health_text.draw(pos=(100,20), width=200,height=36)
        
        rp = RenderPass()
        for bullet in bullets:
            rp.mark_for_draw(bullet)
        
        rp.mark_for_draw(player)
        rp.render()
        pygame.display.flip()

        if bullets.collides(player):
            # Handle this less awkwardly
            #done = True
            player.health -= 1

        bullets.cull(swidth, sheight, 100)

        eventlist = pygame.event.get()
        for event in eventlist:
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                done = True
                
        if joy.state.hats:
            hx, hy = joy.state.hats[0]
            player.x += hx*4
            player.y += hy*4

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            player.x += 1
        elif keys[pygame.K_LEFT]:
            player.x -= 1
        elif keys[pygame.K_UP]:
            player.y += 1
        elif keys[pygame.K_DOWN]:
            player.y -= 1

if __name__ == '__main__':
    main()
