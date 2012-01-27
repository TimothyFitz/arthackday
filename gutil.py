
import pygame

from OpenGL.GL import *
from OpenGL.GLU import *

def initializeDisplay(w, h):
    pygame.display.set_mode((w,h), pygame.OPENGL|pygame.DOUBLEBUF)

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluOrtho2D(0, w, 0, h);
    glMatrixMode(GL_MODELVIEW);

    #set up texturing
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def loadImage(image):
    textureSurface = pygame.image.load(image)

    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)

    width = textureSurface.get_width()
    height = textureSurface.get_height()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData )

    return texture, width, height


def delTexture(texture):
    glDeleteTextures(texture)


def createTexDL(texture, width, height):
    newList = glGenLists(1)
    glNewList(newList,GL_COMPILE);
    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(0, 0)    # Bottom Left Of The Texture and Quad
    glTexCoord2f(0, 1); glVertex2f(0, height)    # Top Left Of The Texture and Quad
    glTexCoord2f(1, 1); glVertex2f( width,  height)    # Top Right Of The Texture and Quad
    glTexCoord2f(1, 0); glVertex2f(width, 0)    # Bottom Right Of The Texture and Quad
    glEnd()
    glEndList()

    return newList


def delDL(list):
    glDeleteLists(list, 1)


def loadText(text, size = 12, color = (0,0,0), font = None, antialias = 1):

    fontObj = pygame.font.Font(font, size)
    image = fontObj.render(text, antialias, color)
    height = image.get_height()
    width = image.get_width()
    h = 16
    while(h < height):
        h = h*2
    w = 16
    while(w < width):
        w = w*2

    label_texture= glGenTextures(1) 
    glBindTexture(GL_TEXTURE_2D, label_texture)
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
    glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
    
    emptyList = "\x00" * w*h*4
    glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, emptyList )
    
    textureData = pygame.image.tostring(image, "RGBA", 1)
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, image.get_width(), image.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    return label_texture, width, height, w, h

