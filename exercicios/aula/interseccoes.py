#-*- coding: utf-8 -*-
from __future__ import division
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

#classe utilizada para definir pontos (vetores 2D)
class Point:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

#classe utilizada para definir linhas (pares de pontos)
class Line:
    src = Point(0, 0)
    dst = Point(0, 0)

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def __str__(self):
        return "[" + str(self.src) + ", " + str(self.dst) + "]"

    def getLeftPoint(self):
        if self.src.x < self.dst.x:
            return self.src
        return self.dst

    def getRightPoint(self):
        if self.src.x > self.dst.x:
            return self.src
        return self.dst

    def getTopPoint(self):
        if self.src.y > self.dst.y:
            return self.src
        return self.dst
        
    def getBottomPoint(self):
        if self.src.y < self.dst.y:
            return self.src
        return self.dst

#vetor que armazena todas as linhas criadas
createdLines = []

#desenha todas as linhas e intersecoes
def displayCallback():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    for line in createdLines:
        drawLine(line)
    renderIntersections()

    glutSwapBuffers()

#chama os métodos apropriados mediante eventos do mouse
def mouseHandler(b, s, x, y):
    if b == GLUT_LEFT_BUTTON:
        if s == GLUT_DOWN:
            onMouseDown(x, y)
        elif s == GLUT_UP:
            onMouseUp(x, y)

#quando o botão esquerdo do mouse é pressionado, coordenadas são armazenadas
def onMouseDown(x, y):
    global mouseClickOrigin
    mouseClickOrigin = Point(x, y)

#quando o botão esquerdo do mouse é solto, é adicionada uma linha que vai do
#ponto em que o mouse foi pressionado até o ponto em que o mouse foi solto
def onMouseUp(x, y):
    mouseClickDestination = Point(x, y)
    addLine(mouseClickOrigin, mouseClickDestination)    

#adiciona uma linha ao vetor global de linhas criadas
def addLine(origin, destination):
    createdLines.append(Line(origin, destination))

#renderiza todas as interseções pareando todas as linhas (O(n²))
def renderIntersections():
    for i in range(0, len(createdLines)):
        for j in range(i + 1, len(createdLines)):
            line_1 = createdLines[i]
            line_2 = createdLines[j]

            intersec = getIntersection(line_1, line_2)
            if intersec is not None:
                drawPoint(intersec)

#checa se há uma interseção entre os dois segmentos
def getIntersection(line_1, line_2):
    #calcula o coeficiente angular das retas
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

    #precisamos verificar se essas coordenadas estão dentro dos dois segmentos delimitados
    #seu 'x' deve estar à direita do 'x' esquerdo de cada segmento
    #e à esquerda do 'x' direito de cada segmento
    #e seu 'y' deve estar abaixo do 'y' superior de cada segmento
    #e abaixo do 'y' inferior de cada segmento
    if x >= line_1.getLeftPoint().x and x >= line_2.getLeftPoint().x and \
        x <= line_1.getRightPoint().x and x <= line_1.getRightPoint().x and \
        y <= line_1.getTopPoint().y and y <= line_2.getTopPoint().y and \
        y >= line_1.getBottomPoint().y and y >= line_1.getBottomPoint().y:
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

    glutInitWindowPosition(0, 0)
    glutInitWindowSize(420, 420)
    window = glutCreateWindow("Intersec")
    
    glutDisplayFunc(displayCallback)
    glutMouseFunc(mouseHandler)

    glutMainLoop()

main()