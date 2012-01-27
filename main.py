import os

from OpenGL.GL import *
from OpenGL.arrays import vbo
from numpy import array
from pygame.locals import *
import gutil
import pygame
import pygame.mouse

from shooter.entities.bullet import BulletSet
from shooter.entities.player import Player


class Image:
    def __init__(self, texname):
        filename = os.path.join('data', texname)
        filename += ".png"

        self.texture, self.width, self.height = gutil.loadImage(filename)
        self.displayList = gutil.createTexDL(self.texture, self.width, self.height)
   

    def __del__(self):
        if self.texture != None:
            gutil.delTexture(self.texture)
            self.texture = None
        if self.displayList != None:
            gutil.delDL(self.displayList)
            self.displayList = None

    def draw(self, pos=None, width = None, height = None, color=(1,1,1,1), rotation=0, rotationCenter=None):
        glColor4fv(color)

        if pos:
            glLoadIdentity()
            glTranslate(pos[0],pos[1],0)

        if rotation != 0:
                if rotationCenter == None:
                    rotationCenter = (self.width / 2, self.height / 2)
                (w,h) = rotationCenter
                glTranslate(rotationCenter[0],rotationCenter[1],0)
                glRotate(rotation,0,0,-1)
                glTranslate(-rotationCenter[0],-rotationCenter[1],0)

        if width or height:
            if not width:
                width = self.width
            elif not height:
                height = self.height

            glScalef(width/(self.width*1.0), height/(self.height*1.0), 1.0)
                

        glCallList(self.displayList)


class Text(Image):

    def __init__(self, text, fontsize = 24, color = (0,0,0,0), font = None, antialias = 1):
        texttexture = gutil.loadText(text, fontsize, color, font, antialias)
        self.texture = texttexture[0]
        self.width = texttexture[1]
        self.height = texttexture[2]
        self.texture_width = texttexture[3]
        self.texture_height = texttexture[4]
        self.displayList = gutil.createTexDL(self.texture, self.texture_width, self.texture_height)

def main():
    player = Player()  # On your own here, but it needs x and y fields.
    bullets = BulletSet.load("test_bullet.xml", (400,600), target=player)

    pygame.init()
    swidth, sheight = 800, 600
    gutil.initializeDisplay(swidth, sheight)

    done = False

    cow = Image('cow')

    while not done:
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1,1,1)
        glPointSize(10)
        glLoadIdentity()
        
        #mx,my = pygame.mouse.get_pos()
        #player.x, player.y = mx, sheight - my

        bullets.step()
        
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

        cow.draw((player.x, player.y))
        pygame.display.flip()
        
        if bullets.collides(player):
            # Handle this less awkwardly
            done = True

        eventlist = pygame.event.get()
        for event in eventlist:
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                done = True

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
