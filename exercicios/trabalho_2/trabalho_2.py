#-*- coding: utf-8 -*-
from __future__ import division
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *
from Structures import Polygon, Point, Line, Joint
from Draw import *
import random

#este 'enum' armazena o estado atual da aplicação
class ApplicationState:
    NONE = 0
    DRAWING_POLYGON = 1
    MOVING_POLYGON = 2
    ROTATING_POLYGON = 3
currentState = ApplicationState.NONE

#armazenam os objetos da cena atual
previewLines = []
polygons = []
joints = []

#armazenam os IDs dos objetos selecionados (quando necessário)
selected_joint = -1
selected_polygon = -1

#armazenam informações sobre a posição do mouse
lastMousePoint = Point(0, 0)
currentMousePoint = Point(0, 0)

#desenha a cena como um todo
def displayCallback():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    #desenha os polígonos e as articulações que os conectam
    for polygon in polygons:
        drawPolygon(polygon)
        for joint in joints:
            if joint.connected(polygon):
                drawPoint(joint.global_pos)

    if currentState == ApplicationState.DRAWING_POLYGON:
        handleDrawPreview()
    elif currentState == ApplicationState.MOVING_POLYGON:
        handleTranslation()
    elif currentState == ApplicationState.ROTATING_POLYGON:
        handleRotation()

    glutSwapBuffers()

def handleDrawPreview():
    #desenha as linhas de pré-visualização do polígono que estivermos desenhando
    drawLine(Line(lastMousePoint, currentMousePoint))
    for line in previewLines:
        drawLine(line)

def handleTranslation():
    #atualiza a posição do polígono selecionado
    polygon = polygons[selected_polygon]
    polygon.translate(currentMousePoint)
    
    #atualiza a posição dos polígonos conectados a este polígono
    p, j = getConnectedPolygons(polygon)
    for polygon in p:
        polygon.translate(currentMousePoint)
    for joint in j:
        joint.translate(currentMousePoint)

def handleRotation():
    #rotaciona o polígono selecionado de acordo com a angulação
    #entre o cursor neste frame e o cursor no frame passado
    #em relação à articulação selecionada
    global lastMousePoint

    polygon = polygons[selected_polygon]
    p1 = lastMousePoint
    p2 = currentMousePoint
    p3 = joints[selected_joint].global_pos
    
    u = Point(p3.x - p1.x, p3.y - p1.y)
    v = Point(p3.x - p2.x, p3.y - p2.y)

    length_u = sqrt(u.x * u.x + u.y * u.y)
    length_v = sqrt(v.x * v.x + v.y * v.y)
    dot = u.x * v.x + u.y * v.y
    
    cos = dot / float(length_u * length_v)
    cos = min(cos, 1) #corrige erros de aproximação que tornam o cosseno > 1

    angle = acos(cos)
    
    sign = (p2.x - p1.x) * (p3.y - p2.y) - (p2.y - p1.y) * (p3.x - p2.x) #detecta orientação da rotação
    sign = 1 if sign > 0 else -1
    angle = angle * sign
    
    p, j = getChildren(polygon)
    for poly in p:
        poly.rotate(p3, angle)
    for joint in j:
        joint.rotate(p3, angle)

    lastMousePoint = currentMousePoint

#armazena a posição atual do cursor
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

def keyHandler(key, x, y):
    if key == 'c':
        clearScreen();

#clique do botão esquerdo do mouse
def onMouse1Down(x, y):
    global currentState
    global lastMousePoint
    global selected_polygon
    global selected_joint

    if currentState == ApplicationState.NONE:
        #caso a aplicação não esteja fazendo nada, checamos se um polígono foi clicado
        polygonClicked = getFirstPolygonClicked()
        lastMousePoint = Point(x, y)
        if polygonClicked is not None:

            selected_joint = getPolygonParentJoint(polygonClicked)
            selected_polygon = polygonClicked.p_id

            #se polígono clicado não é dependente de nenhuma articulação,
            #inicia-se a translação dele e dos polígonos conectados a ele
            if selected_joint == -1:
                currentState = ApplicationState.MOVING_POLYGON
                polygonClicked.update_offset(currentMousePoint)
                p, j = getConnectedPolygons(polygonClicked)
                for poly in p:
                    poly.update_offset(currentMousePoint)
                for joint in j:
                    joint.update_offset(currentMousePoint)
            #se ele depende de alguma articulação, iniciamos a rotação
            else:
                currentState = ApplicationState.ROTATING_POLYGON
        else:
            #se nenhum polígono foi clicado, começamos a desenhar
            currentState = ApplicationState.DRAWING_POLYGON

#levantar do clique do botão esquerdo do mouse
def onMouse1Up(x, y):
    global drawingPolygon
    global lastMousePoint
    global previewLines
    global currentState
    global selected_joint
    global selected_polygon

    if currentState == ApplicationState.DRAWING_POLYGON:
        #se um polígono foi fechado, checamos se ele é válido e o criamos.
        if len(previewLines) > 0 and currentMousePoint.distance(previewLines[0].src) < 10:
            currentState = ApplicationState.NONE

            aux = list(previewLines)
            aux.append(Line(lastMousePoint, previewLines[0].src))
            if hasIntersection(aux):
                previewLines = []
                return
            
            polygons.append(Polygon(aux, len(polygons)))
            previewLines = []
            return

        #caso contrário, checamos se esta linha é válida
        #e se for, começamos a pré-visualizá-la
        lines = list(previewLines)
        lines.append(Line(lastMousePoint, currentMousePoint))

        if not hasIntersection(lines):
            previewLines.append(Line(lastMousePoint, currentMousePoint))
            lastMousePoint = Point(currentMousePoint.x, currentMousePoint.y)
        
    #se estávamos movendo ou rotacionando um polígono, agora não estamos mais
    elif currentState == ApplicationState.MOVING_POLYGON:
        currentState = ApplicationState.NONE
        selected_polygon = -1

    elif currentState == ApplicationState.ROTATING_POLYGON:
        currentState = ApplicationState.NONE
        selected_polygon = -1
        selected_joint = -1

#clique do botão direito do mouse
def onMouse2Down(x, y):
    global currentState
    global previewLines

    #se estiver desenhando um poligono, cancele
    if currentState == ApplicationState.DRAWING_POLYGON:
        currentState = ApplicationState.NONE
        previewLines = []
    #adiciona uma articulação, se possível
    elif currentState == ApplicationState.NONE:
        poly = hasClickedOnPolygonPair()
        if poly is not None:
            p1, l1 = getConnectedPolygons(poly[0])
            p2, l2 = getConnectedPolygons(poly[1])
            if len(p2) > len(p1): #o polígono de grupo maior vira 'pai'
                poly.reverse()
            elif len(p1) == 1 and len(p2) == 1: #no caso 'base', o polígono mais antigo vira 'pai'
                poly.sort(key=lambda x: x.p_id)
            handleJointClick(poly[0], poly[1])

#controla o clique em articulações
def handleJointClick(parent, child):
    global selected_joint
    #remove articulação caso ela já exista
    for joint in joints:
        if joint.connected(parent) and joint.connected(child):
            joints.remove(joint)
            return
    #impede que articulação gere um ciclo
    p1, j1 = getConnectedPolygons(parent)
    p2, j2 = getConnectedPolygons(child)
    for polygon in p1:
        if polygon.p_id == child.p_id:
            return
    #adiciona articulação à lista de articulações
    joints.append(Joint(currentMousePoint, parent, child))
    #atualiza as articulações para corrigir as relações pai-filho
    k = 0
    pool = [child]
    changed_joints = []
    while k < len(pool):
        polygon = pool[k]
        for j in joints:
            if j.child.p_id == polygon.p_id \
                and j.parent.p_id != parent.p_id \
                and j not in changed_joints:
                pool.append(j.parent)
                changed_joints.append(j)
                j.swap()
        k = k + 1

#checa se clicamos em um par de polígonos
def hasClickedOnPolygonPair():
    output = []
    for i in range(len(polygons)-1, -1, -1):
        polygon = polygons[i]
        if pointInsidePolygon(currentMousePoint, polygon):
            output.append(polygon)
    if len(output) == 2:
        return output
    return None

#retorna o polígono mais recente que foi clicado
#(mais recentes são desenhados na frente)
def getFirstPolygonClicked():
    for i in range(len(polygons)-1, -1, -1):
        polygon = polygons[i]
        if pointInsidePolygon(currentMousePoint, polygon):
            return polygon
    return None

#retorna a articulação em que o polígono é 'pai'
def getPolygonParentJoint(polygon):
    for joint in joints:
        if joint.child.p_id == polygon.p_id:
            return joints.index(joint)
    return -1

#retorna articulações e polígonos filhos de 'polygon'
def getChildren(polygon):
    output_p = [polygon]
    output_j = []
    k = 0
    while k < len(output_p):
        pl = output_p[k]
        for joint in joints:
            if joint.parent.p_id == pl.p_id:
                if joint.child not in output_p:
                    output_p.append(joint.child)
                if joint not in output_j:
                    output_j.append(joint)
        k += 1
    return output_p, output_j

#checa se um ponto está dentro de um polígono (odd-even)
def pointInsidePolygon(point, polygon):
    line = Line(point, Point(0, 0))
    intersections = 0

    polygon_lines = []
    for i in range(0, len(polygon.global_pts) - 1):
        aux = Line(polygon.global_pts[i], polygon.global_pts[i+1])
        polygon_lines.append(aux)
    aux = Line(polygon.get_last_point(), polygon.get_first_point())
    polygon_lines.append(aux)

    for l in polygon_lines:
        if getIntersection(line, l):
            intersections += 1

    return intersections % 2 == 1

#retorna todos os polígonos conectados por articulações a 'polygon'
def getConnectedPolygons(polygon):
    k = 0
    output_pl = [polygon]
    output_j = []
    while k < len(output_pl):
        for j in joints:
            if j.parent == output_pl[k]:
                if j.child not in output_pl:
                    output_pl.append(j.child)
                if j not in output_j:
                    output_j.append(j)
            elif j.child == output_pl[k]:
                if j.parent not in output_pl:
                    output_pl.append(j.parent)
                if j not in output_j:
                    output_j.append(j)
        k += 1
    return output_pl, output_j

#checa se há uma interseção em um array de segmentos
def hasIntersection(lines):
    for i in range(0, len(lines)):
        for j in range(i + 1, len(lines)):
            line_1 = lines[i]
            line_2 = lines[j]

            intersec = getIntersection(line_1, line_2)
            if intersec is not None:
                return True

    return False

#checa se há uma interseção entre dois segmentos
def getIntersection(line_1, line_2):
    p = line_1.src
    r = Point(line_1.dst.x - line_1.src.x, line_1.dst.y - line_1.src.y)
    q = line_2.src
    s = Point(line_2.dst.x - line_2.src.x, line_2.dst.y - line_2.src.y)
    
    if (r.x == 0 and r.y == 0) or (s.x == 0 and s.y == 0):
        return None #ponto

    qp = Point(q.x - p.x, q.y - p.y)
    pq = Point(p.x - q.x, p.y - q.y)
    r_x_s = crossProduct(r, s)
    qp_x_r = crossProduct(qp, r)

    if r_x_s == 0 and qp_x_r == 0:
        return None #colinear
    
    qp_x_s = crossProduct(qp, s)
    pq_x_r = crossProduct(pq, r)
    s_x_r = crossProduct(s, r)
    
    if r_x_s == 0 and qp_x_r != 0:
        return None #paralelo

    t = float(qp_x_s) / float(r_x_s)
    u = float(pq_x_r) / float(s_x_r)

    if r_x_s != 0 and (t > 0 and t < 1) and (u > 0 and u < 1):
        return Point(p.x + t*r.x, p.y + t*r.y) #interseção!
    else:
        return None #sem interseção

#produto vetorial
def crossProduct(point_1, point_2):
    return point_1.x * point_2.y - point_1.y * point_2.x

#deleta todos os polígonos e articulações
def clearScreen():
    global polygons
    global previewLines
    global joints
    global selected_joint
    global selected_polygon
    polygons = []
    previewLines = []
    joints = []
    selected_joint = -1
    selected_polygon = -1

#imprime informações de help
def printHelp():
    print "Estudante: Vinícius Garcia / DRE: 115.039.031"
    print "==============================================="
    print "Trabalho 2 de CG 2017.2 - Desenhando Polígonos"
    print "==============================================="
    print "Desenhar: botão esquerdo do mouse em área vazia, iniciando polígono."
    print "Cancelar desenho de polígono: botão direito do mouse enquanto estiver desenhando."
    print "Adicionar/remover articulação: botão direito do mouse em cima da interseção entre dois polígonos."
    print "Mover: botão esquerdo do mouse em um polígono 'raiz' e arrastar."
    print "Rotacionar: botão esquerdo do mouse em um polígono 'não-raiz' e arrastar."
    print "Limpar a tela: pressionar tecla 'C'."

#utiliza métodos do PyOpenGL para realizar as ações básicas
#(abrir tela, chamar callbacks de display, etc)
def main():
    printHelp();
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE)

    glutInitWindowPosition(150, 150)
    glutInitWindowSize(420, 420)
    window = glutCreateWindow("Trabalho 2 - CG")
    
    glutDisplayFunc(displayCallback)
    glutMouseFunc(mouseHandler)
    glutKeyboardFunc(keyHandler)
    glutPassiveMotionFunc(mousePosUpdater)
    glutMotionFunc(mousePosUpdater)
    glutIdleFunc(displayCallback)

    glutMainLoop()

main()