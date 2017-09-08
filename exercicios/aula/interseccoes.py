from __future__ import division
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class Vector2:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

createdLines = []

def displayCallback():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    for pair in createdLines:
        drawLine(
            worldToScreenPoint(pair[0]), 
            worldToScreenPoint(pair[1])
        )

    glutSwapBuffers()

def mouseHandler(b, s, x, y):
    if b == GLUT_LEFT_BUTTON:
        if s == GLUT_DOWN:
            onMouseDown(x, y)
        elif s == GLUT_UP:
            onMouseUp(x, y)

def onMouseDown(x, y):
    global mouseClickOrigin
    mouseClickOrigin = Vector2(x, y)

def onMouseUp(x, y):
    mouseClickDestination = Vector2(x, y)
    addLine(mouseClickOrigin, mouseClickDestination)    

def addLine(origin, destination):
    createdLines.append([origin, destination])

def worldToScreenPoint(coord):
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)

    return Vector2(
        ((width / 2) - coord.x) / ((- width) / 2),
        ((height / 2) - coord.y) / (height / 2)
    )

def drawLine(origin, destination):
    print(str(origin) + ", " + str(destination))
    glLineWidth(2.5)
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex2f(origin.x, origin.y)
    glVertex2f(destination.x, destination.y)
    glEnd()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE)

    glutInitWindowPosition(0, 0)
    glutInitWindowSize(420, 420)
    window = glutCreateWindow("Intersec")
    
    glutDisplayFunc(displayCallback)
    glutMouseFunc(mouseHandler)

    glutMainLoop()

main()