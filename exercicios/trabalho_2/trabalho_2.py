#-*- coding: utf-8 -*-
from __future__ import division
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *
import random

class ApplicationState:
    NONE = 0
    DRAWING_POLYGON = 1
    MOVING_POLYGON = 2
    ROTATING_POLYGON = 3

def str_application_state(state):
    if state == ApplicationState.NONE:
        return "NONE"
    elif state == ApplicationState.DRAWING_POLYGON:
        return "DRAWING_POLYGON"
    elif state == ApplicationState.MOVING_POLYGON:
        return "MOVING_POLYGON"
    elif state == ApplicationState.ROTATING_POLYGON:
        return "ROTATING_POLYGON"
    else:
        return "????"

#classe utilizada para definir pontos (vetores 2D)
class Point:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def equals(self, point):
        return self.x == point.x and self.y == point.y

    def distance(self, point):
        return sqrt(pow(self.x - point.x, 2) + pow(self.y - point.y, 2))

#classe utilizada para definir linhas (pares de pontos)
class Line:
    src = Point(0, 0)
    dst = Point(0, 0)

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def __str__(self):
        return "[" + str(self.src) + ", " + str(self.dst) + "]"

class Polygon:
    local_points = []
    global_points = []
    lines = []
    p_id = -1
    color = []

    def __init__(self, lines):
        self.lines = list(lines)
        self.local_points = []
        self.global_points = []
        self.p_id = len(polygons)
        self.color = [random.randrange(0, 255) / float(255), random.randrange(0, 255) / float(255), random.randrange(0, 255) / float(255)]

        for i in range(1, len(lines)):
            self.global_points.append(lines[i].src)

        self.update_offset(lines[0].src)

    def update_offset(self, point):
        self.local_points = []
        for op in self.global_points:
            self.local_points.append(Point(op.x - point.x, op.y - point.y))

    def center_around(self, point):
        self.global_points = []
        for op in self.local_points:
            self.global_points.append(Point(op.x + point.x, op.y + point.y))

        self.lines = []
        for i in range(1, len(self.global_points)):
            self.lines.append(Line(self.global_points[i-1], self.global_points[i]))
        self.lines.append(Line(self.global_points[0], self.global_points[len(self.global_points) - 1]))

class Joint:
    polygon_curr = None
    polygon_next = None
    local_position = Point(0, 0)
    global_position = Point(0, 0)

    def __init__(self, point, p_curr, p_next):
        self.global_position = point
        self.polygon_curr = p_curr
        self.polygon_next = p_next
        self.local_position = Point(self.global_position.x - self.polygon_curr.lines[0].src.x, self.global_position.y - self.polygon_curr.lines[0].src.y)

    def center_around(self, point):
        self.global_position = Point(self.local_position.x + point.x, self.local_position.y + point.y)

    def update_offset(self, point):
        self.local_position = Point(self.global_position.x - point.x, self.global_position.y - point.y)

#vetor que armazena todas as linhas criadas
currentState = ApplicationState.NONE
previewLines = []
polygons = []
joints = []

selected_polygon = -1
holding_m1 = False

lastPoint = Point(0, 0)
currentMousePoint = Point(0, 0)

#desenha todas as linhas e intersecoes
def displayCallback():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # print("State: " + str_application_state(currentState))

    for polygon in polygons:
        angle = 0
        if currentState == ApplicationState.ROTATING_POLYGON:
            u = Point(polygon.lines[0].src.x - lastPoint.x, polygon.lines[0].src.y - lastPoint.y)
            v = Point(polygon.lines[0].src.x - currentMousePoint.x, polygon.lines[0].src.y - currentMousePoint.y)

            length_u = sqrt(u.x * u.x + u.y * u.y)
            length_v = sqrt(v.x * v.x + v.y * v.y)
            dot = u.x * v.x + u.y * v.y
            aux = dot / float(length_u * length_v)
            angle = degrees(acos(aux))
        drawPolygon(polygon, angle)

    for line in previewLines:
        drawLine(line)

    if currentState == ApplicationState.DRAWING_POLYGON:
        drawLine(Line(lastPoint, currentMousePoint))
    elif currentState == ApplicationState.MOVING_POLYGON:
        pl = polygons[selected_polygon]
        pl.center_around(currentMousePoint)
        p, j = getConnectedPolygons(pl)
        for poly in p:
            poly.center_around(currentMousePoint)
        for join in j:
            join.center_around(currentMousePoint)

    for joint in joints:
        drawPoint(joint.global_position)

    glutSwapBuffers()

def getConnectedPolygons(polygon):
    k = 0
    output_pl = [polygon]
    output_j = []
    while k < len(output_pl):
        for j in joints:
            if j.polygon_curr == output_pl[k]:
                if j.polygon_next not in output_pl:
                    output_pl.append(j.polygon_next)
                if j not in output_j:
                    output_j.append(j)
            elif j.polygon_next == output_pl[k]:
                if j.polygon_curr not in output_pl:
                    output_pl.append(j.polygon_curr)
                if j not in output_j:
                    output_j.append(j)
        k += 1
    return output_pl, output_j

def mousePosUpdater(x, y):
    global currentMousePoint
    currentMousePoint = Point(x, y)

#chama os métodos apropriados mediante eventos do mouse
def mouseHandler(b, s, x, y):
    if b == GLUT_LEFT_BUTTON:
        if s == GLUT_DOWN:
            onMouse1Down(x, y)
        elif s == GLUT_UP:
            onMouse1Up(x, y)
    if b == GLUT_RIGHT_BUTTON:
        if s == GLUT_DOWN:
            onMouse2Down(x, y)
        # elif s == GLUT_UP:
        #     onMouse2Up(x, y)

def onMouse2Down(x, y):
    #if drawing polygon, cancel 
    global currentState
    global previewLines

    if currentState == ApplicationState.DRAWING_POLYGON:
        currentState = ApplicationState.NONE
        previewLines = []
    elif currentState == ApplicationState.NONE:
        poly = hasClickedOnPolygonPair()
        if poly is not None:
            joints.append(Joint(currentMousePoint, poly[0], poly[1]))

def hasClickedOnPolygonPair():
    output = []
    for polygon in polygons:
        if pointInsidePolygon(currentMousePoint, polygon):
           output.append(polygon)
           if len(output) == 2:
               return output
    return None    

def hasClickedOnPolygon():
    for polygon in polygons:
        if pointInsidePolygon(currentMousePoint, polygon):
            return polygon
    return None

def pointInsidePolygon(point, polygon):
    line = Line(point, Point(0, 0))
    intersections = 0
    for l in polygon.lines:
        if getIntersection(line, l):
            intersections += 1
    
    # print str(intersections) + " intersections"
    return intersections % 2 == 1

#quando o botão esquerdo do mouse é pressionado, coordenadas são armazenadas
def onMouse1Down(x, y):
    global currentState
    global lastPoint
    global selected_polygon
    global holding_m1

    holding_m1 = True

    if currentState == ApplicationState.NONE:
        polygonClicked = hasClickedOnPolygon()
        lastPoint = Point(x, y)
        if polygonClicked is not None:
            currentState = ApplicationState.MOVING_POLYGON
            selected_polygon = polygonClicked.p_id
            polygonClicked.update_offset(currentMousePoint)

            p, j = getConnectedPolygons(polygonClicked)
            for poly in p:
                poly.update_offset(currentMousePoint)
            for joint in j:
                joint.update_offset(currentMousePoint)
        else:
            currentState = ApplicationState.DRAWING_POLYGON
    elif currentState == ApplicationState.ROTATING_POLYGON:
        currentState = ApplicationState.NONE
        selected_polygon = -1

#quando o botão esquerdo do mouse é solto, é adicionada uma linha que vai do
#ponto em que o mouse foi pressionado até o ponto em que o mouse foi solto
def onMouse1Up(x, y):
    global drawingPolygon
    global lastPoint
    global previewLines
    global currentState
    global holding_m1

    holding_m1 = False

    if currentState == ApplicationState.DRAWING_POLYGON:
        #created point in polygon, check if point closes polygon
        if len(previewLines) > 0 and currentMousePoint.distance(previewLines[0].src) < 10:
            currentState = ApplicationState.NONE
            previewLines.append(Line(lastPoint, previewLines[0].src))
            polygons.append(Polygon(previewLines))
            previewLines = []
            return

        #else, check if line is valid
        #if valid, add to preview
        lines = list(previewLines)
        lines.append(Line(lastPoint, currentMousePoint))

        if not hasIntersection(lines):
            previewLines.append(Line(lastPoint, currentMousePoint))
            lastPoint = Point(currentMousePoint.x, currentMousePoint.y)
    elif currentState == ApplicationState.MOVING_POLYGON:
        currentState = ApplicationState.NONE
        selected_polygon = -1

def drawPolygon(polygon, angle):
    glLineWidth(2.5)
    glColor3f(polygon.color[0], polygon.color[1], polygon.color[2])

    tess = gluNewTess()
    gluTessCallback(tess, GLU_BEGIN, glBegin)
    gluTessCallback(tess, GLU_VERTEX, glVertex3dv)
    gluTessCallback(tess, GLU_END, glEnd)
    gluBeginPolygon(tess)
    for point in polygon.global_points:
    
        pt = worldToScreenPoint(point)
        aux = [pt.x, pt.y, 0]
        gluTessVertex(tess, aux, aux)
    gluEndPolygon(tess)

    gluDeleteTess(tess)

#renderiza todas as interseções pareando todas as linhas (O(n²))
def hasIntersection(lines):
    for i in range(0, len(lines)):
        for j in range(i + 1, len(lines)):
            line_1 = lines[i]
            line_2 = lines[j]

            intersec = getIntersection(line_1, line_2)
            if intersec is not None:
                return True

    return False

#checa se há uma interseção entre os dois segmentos
def getIntersection(line_1, line_2):
    #calcula o coeficiente angular das retas
    if (line_1.dst.x == line_1.src.x) or (line_2.dst.x == line_2.src.x):
        return None

    if (line_1.dst.x == line_2.dst.x and line_1.dst.y == line_2.dst.y) or\
        (line_1.src.x == line_2.dst.x and line_1.src.y == line_2.dst.y) or\
        (line_1.dst.x == line_2.src.x and line_1.dst.y == line_2.src.y) or\
        (line_1.src.x == line_2.src.x and line_1.src.y == line_2.src.y):
        return None

    a_1 = (line_1.dst.y - line_1.src.y) / (line_1.dst.x - line_1.src.x)
    a_2 = (line_2.dst.y - line_2.src.y) / (line_2.dst.x - line_2.src.x)
    #calcula o coeficiente linear das retas
    b_1 = ((line_1.dst.x * line_1.src.y) - (line_1.src.x * line_1.dst.y)) / (line_1.dst.x - line_1.src.x)
    b_2 = ((line_2.dst.x * line_2.src.y) - (line_2.src.x * line_2.dst.y)) / (line_2.dst.x - line_2.src.x)
    
    #se coeficiente angular das duas é igual,
    #linhas são paralelas, não há interseção
    if a_1 == a_2:
        # print("Lines are parallel.")
        return None

    #encontra as coordenadas (x,y) da interseção entre as duas retas
    x = (b_2 - b_1) / (a_1 - a_2)
    y = a_2 * x + b_2

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
        return Point(x, y)

    return None

#converte as coordenadas do viewport do mouse (x=[0, w], y=[0, h])
#para o viewport da tela (x=[-1, 1], y=[-1, 1])
def worldToScreenPoint(coord):
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)

    return Point(
        ((width / 2) - coord.x) / ((- width) / 2),
        ((height / 2) - coord.y) / (height / 2)
    )

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

#utiliza métodos do PyOpenGL para realizar as ações básicas
#(abrir tela, chamar callbacks de display, etc)
def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE)

    glutInitWindowPosition(150, 150)
    glutInitWindowSize(420, 420)
    window = glutCreateWindow("Intersec")
    
    glutDisplayFunc(displayCallback)
    glutMouseFunc(mouseHandler)
    glutPassiveMotionFunc(mousePosUpdater)
    glutMotionFunc(mousePosUpdater)
    glutIdleFunc(displayCallback)

    glutMainLoop()

main()