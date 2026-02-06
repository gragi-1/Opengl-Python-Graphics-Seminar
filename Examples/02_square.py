from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from numpy import *
import time
import sys

vertices  = array([[-1.0, -0.5], [-0.5, -0.25], [-1.0, 0.5], [-0.5, 0.25], [1.0, 0.5], [0.5, 0.25], [1.0, -0.5], [0.5, -0.25], [-1.0, -0.5], [-0.5, -0.25]], dtype=float)

color = array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 1.0], [0.5, 0.5, 0.5], [0.2, 0.2, 0.2], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=float)

def init():
    glClearColor(0.6, 0.7, 0.82, 1.0)
    gluOrtho2D(-2.0, 2.0, -2.0, 2.0)

def square():
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(0.9, 0.2, 0.15)
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(0, 10):
        glColor3fv(color[i])
        glVertex2fv(vertices[i])
    glEnd()
    glFlush()

if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowPosition(300, 300)
    glutInitWindowSize(500, 500)
    glutCreateWindow(b'Mi primera ventana')
    init()
    glutDisplayFunc(square)
    glutMainLoop()