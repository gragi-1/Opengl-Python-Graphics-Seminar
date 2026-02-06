from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from numpy import *
import time
import sys

def init():
    glClearColor(0.6, 0.7, 0.82, 1.0)
    gluOrtho2D(-2.0, 2.0, -2.0, 2.0)

def display():
    current_time = time.perf_counter()
    triangle(6, 1.7, current_time)

def idle():
    glutPostRedisplay()

def triangle(num_sides, radius, t):
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(0.9, 0.2, 0.15)
    glBegin(GL_POLYGON)
    for i in range(0, num_sides):
        glVertex2f(radius * sin(t + (i * 2*pi / num_sides)), radius * cos(t + (i * 2*pi / num_sides)))
    glEnd()
    glFlush()

if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowPosition(300, 300)
    glutInitWindowSize(500, 500)
    glutCreateWindow(b'Mi primera ventana')
    init()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutMainLoop()