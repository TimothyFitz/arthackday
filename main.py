import os
import time
import copy

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


def main():
    live_dj = Dj()

    player = Player(live_dj)  # On your own here, but it needs x and y fields.
    player.x = 50
    player.y = 300
    bullets = BulletSet.load("gravity_attack.xml", (750,300), target=player)

    pygame.init()
    swidth, sheight = 800, 600
    gutil.initializeDisplay(swidth, sheight)

    joy = JoystickServer()
    joy.daemon = True
    joy.start()
    
    done = False

    cow = Image('cow')

    step = 1

    
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

        bp = []
        width = height = 16
        for b in bullets:
            bp += [[b.x, b.y, 0,  0,0], [b.x+width,b.y,0,  1,0], [b.x+width,b.y+height,0,  1,1], [b.x,b.y+height,0,  0,1]]
        
        stride = 5*4
        bullets_vbo = vbo.VBO(array(bp, 'f'))

        bullets_vbo.bind()
        # Bind to texture id here (for now just cow)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glVertexPointer(3, GL_FLOAT, stride, bullets_vbo)
        glTexCoordPointer(2, GL_FLOAT, stride, bullets_vbo + 3*4)
        glDrawArrays(GL_QUADS, 0, len(bp))
        bullets_vbo.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        # Health etc text
        player.health_text.draw(pos=(100,20), width=200,height=36)

        cow.draw((player.x, player.y))
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
