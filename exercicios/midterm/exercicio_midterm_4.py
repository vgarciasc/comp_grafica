from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def changeSize(w, h):
    if h == 0:
        h = 1
    
    ratio = 1.0 * w / h

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    glViewport(0, 0, w, h)

    gluPerspective(45, ratio, 1, 1000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(10, -10, 10, 0,
        0, 0, 0, 0,
        1)

def drawWing(side):
    if side == "left":
        glColor3f(1.0, 0, 0)
    else:
        glColor3f(0, 0.5, 0.5)

    glBegin(GL_TRIANGLES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 2.0, 0.0)
    glVertex3f(3.0, 0.0, 0.0)
    glEnd()

def drawBird(side, angle):
    glPushMatrix()

    glTranslatef(2.0, 3.0, 0.0)
    scaleX = 0
    if side == "left":
        scaleX = -1.5
    elif side == "right":
        scaleX = 1.5

    glScalef(scaleX, 1.5, 1.5)
    glRotatef(-90.0, 0.0, 0.0, 1.0)
    glRotatef(angle, 1.0, 0.0, 0.0)

    drawWing(side)
    glPopMatrix()    

renderScene_angle = 0
renderScene_down = False

def renderScene():
    global renderScene_angle
    global renderScene_down

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    drawBird("left", renderScene_angle)
    drawBird("right", renderScene_angle)

    if renderScene_angle >= 60:
        renderScene_down = True
    elif renderScene_angle <= 0:
        renderScene_down = False
    
    if renderScene_down:
        renderScene_angle -= 1
    else:
        renderScene_angle += 1

    glutSwapBuffers()

#main
glutInit()
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA)

glutInitWindowPosition(100, 100)
glutInitWindowSize(420, 420)
window = glutCreateWindow("Bird")

glutDisplayFunc(renderScene)
glutIdleFunc(renderScene)
glutReshapeFunc(changeSize)

glutMainLoop()