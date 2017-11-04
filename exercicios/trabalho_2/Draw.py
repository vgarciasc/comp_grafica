#-*- coding: utf-8 -*-
from Structures import Polygon, Point, Line
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def drawPolygon(polygon):
    glLineWidth(2.5)
    glColor3f(polygon.color[0], polygon.color[1], polygon.color[2])

    tess = gluNewTess()
    gluTessCallback(tess, GLU_BEGIN, glBegin)
    gluTessCallback(tess, GLU_VERTEX, glVertex3dv)
    gluTessCallback(tess, GLU_END, glEnd)
    gluBeginPolygon(tess)
    for point in polygon.global_pts:
        pt = worldToScreenPoint(point)
        aux = [pt.x, pt.y, 0]
        gluTessVertex(tess, aux, aux)
    gluEndPolygon(tess)

    gluDeleteTess(tess)

#utiliza métodos do PyOpenGL para desenhar um ponto na tela
def drawPoint(Point):
    # print(str(Point))
    point = worldToScreenPoint(Point)
    glPointSize(10.0)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_POINTS)
    glVertex2f(point.x, point.y)
    glEnd()

#utiliza métodos do PyOpenGL para desenhar uma linha na tela
def drawLine(line):
    origin = worldToScreenPoint(line.src)
    destination = worldToScreenPoint(line.dst)
    
    glLineWidth(2.5)
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex2f(origin.x, origin.y)
    glVertex2f(destination.x, destination.y)
    glEnd()

#converte as coordenadas do viewport do mouse (x=[0, w], y=[0, h])
#para o viewport da tela (x=[-1, 1], y=[-1, 1])
def worldToScreenPoint(coord):
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)

    return Point(
        (float((width / float(2))) - coord.x) / float(((- width) / 2)),
        (float((height / float(2))) - coord.y) / float((height / float(2)))
    )