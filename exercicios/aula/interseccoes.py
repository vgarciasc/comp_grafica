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

class Line:
    src = Vector2(0, 0)
    dst = Vector2(0, 0)

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def __str__(self):
        return "[" + str(self.src) + ", " + str(self.dst) + "]"

createdLines = []

def displayCallback():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    for line in createdLines:
        drawLine(line)

    renderIntersections()
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
    createdLines.append(Line(origin, destination))

def worldToScreenPoint(coord):
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)

    return Vector2(
        ((width / 2) - coord.x) / ((- width) / 2),
        ((height / 2) - coord.y) / (height / 2)
    )

def renderIntersections():
    for i in range(0, len(createdLines)):
        for j in range(i + 1, len(createdLines)):
            line_1 = createdLines[i]
            line_2 = createdLines[j]

            drawIntersection(line_1, line_2)

def drawIntersection(line_1, line_2):
    a_1 = (line_1.dst.y - line_1.src.y) / (line_1.dst.x - line_1.src.x)
    a_2 = (line_2.dst.y - line_2.src.y) / (line_2.dst.x - line_2.src.x)
    b_1 = ((line_1.dst.x * line_1.src.y) - (line_1.src.x * line_1.dst.y)) / (line_1.dst.x - line_1.src.x)
    b_2 = ((line_2.dst.x * line_2.src.y) - (line_2.src.x * line_2.dst.y)) / (line_2.dst.x - line_2.src.x)
    
    if a_1 == a_2:
        print("Lines are parallel.")
        return

    x = (b_2 - b_1) / (a_1 - a_2)
    y = a_2 * x + b_2

    print ("line_1: " + str(line_1) + ", line_2: " + str(line_2))
    print ("x: " + str(x) + ", y: " + str(y))

    small_x = [x]
    small_x.append(min(line_1.src.x, line_1.dst.x))
    small_x.append(min(line_2.src.x, line_2.dst.x))

    large_x = [x]
    large_x.append(max(line_1.src.x, line_1.dst.x))
    large_x.append(max(line_2.src.x, line_2.dst.x))

    small_y = [y]
    small_y.append(min(line_1.src.y, line_1.dst.y))
    small_y.append(min(line_2.src.y, line_2.dst.y))

    large_y = [y]
    large_y.append(max(line_1.src.y, line_1.dst.y))
    large_y.append(max(line_2.src.y, line_2.dst.y))

    if max(small_x) == x and min(large_x) == x and max(small_y) == y and min(large_y) == y:
        drawPoint(Vector2(x, y))

def drawPoint(vector2):
    print(str(vector2))
    point = worldToScreenPoint(vector2)
    glPointSize(10.0)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_POINTS)
    glVertex2f(point.x, point.y)
    glEnd()

def drawLine(line):
    origin = worldToScreenPoint(line.src)
    destination = worldToScreenPoint(line.dst)
    
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