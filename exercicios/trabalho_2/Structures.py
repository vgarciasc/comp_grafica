#-*- coding: utf-8 -*-
from math import *
import random

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

    def rotate(self, origin, angle):
        #aplica a matriz de rotação de um ponto em relação a outro ponto
        #composição das matrizes de translação para a origem, rotação,
        #e translação para posição original
        output_x = self.x * cos(angle) - self.y * sin(angle) + (sin(angle) * origin.y - cos(angle) * origin.x + origin.x)
        output_y = self.x * sin(angle) + self.y * cos(angle) + (- sin(angle) * origin.x - cos(angle) * origin.y + origin.y)
        return Point(output_x, output_y)

    #classe utilizada para definir linhas (pares de pontos)
class Line:
    src = Point(0, 0)
    dst = Point(0, 0)

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def __str__(self):
        return "[" + str(self.src) + ", " + str(self.dst) + "]"

    def length(self):
        return sqrt(pow(self.dst.x - self.src.x, 2) + pow(self.dst.y - self.src.y, 2))

class Polygon:
    p_id = -1
    local_pts = []
    global_pts = []
    color = []

    def __init__(self, lines, p_id):
        self.local_pts = []
        self.global_pts = []
        self.p_id = p_id
        self.color = [random.randrange(0, 255) / float(255), random.randrange(0, 255) / float(255), random.randrange(0, 255) / float(255)]

        for i in range(0, len(lines)):
            if lines[i].length() > 1:
                self.global_pts.append(lines[i].src)

        self.update_offset(lines[0].src)

    def update_offset(self, point):
        self.local_pts = []
        for op in self.global_pts:
            self.local_pts.append(Point(op.x - point.x, op.y - point.y))

    def translate(self, point):
        self.global_pts = []
        for op in self.local_pts:
            self.global_pts.append(Point(op.x + point.x, op.y + point.y))

    def rotate(self, point, angle):
        new_points = []
        for lp in self.global_pts:
            new_points.append(lp.rotate(point, angle))
        self.global_pts = list(new_points)
        self.update_offset(self.get_first_point())
        self.translate(self.get_first_point())

    def get_first_point(self):
        return self.global_pts[0]

    def get_last_point(self):
        return self.global_pts[len(self.global_pts) - 1]

class Joint:
    parent = None
    child = None
    local_pos = Point(0, 0)
    global_pos = Point(0, 0)

    def __init__(self, point, curr, next):
        self.global_pos = point
        self.parent = curr
        self.child = next
        self.local_pos = Point(self.global_pos.x - self.parent.get_first_point().x, self.global_pos.y - self.parent.get_first_point().y)

    def translate(self, point):
        self.global_pos = Point(self.local_pos.x + point.x, self.local_pos.y + point.y)

    def update_offset(self, point):
        self.local_pos = Point(self.global_pos.x - point.x, self.global_pos.y - point.y)

    def rotate(self, point, angle):
        self.global_pos = self.global_pos.rotate(point, angle)

    def connected(self, polygon):
        return self.parent.p_id == polygon.p_id or self.child.p_id == polygon.p_id

    def swap(self):
        aux = self.parent
        self.parent = self.child
        self.child = aux
