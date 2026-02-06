from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from numpy import *
import time
import sys


# Simple OpenGL demo: rotating colored square that scrolls horizontally and wraps seamlessly.

# Vertices of the shape (square drawn as triangle strip with repeated points at ends)
vertices  = array([
    [-1.0, -1.0], [-0.5, -0.5],
    [-1.0, +1.0], [-0.5, +0.5],
    [+1.0, +1.0], [+0.5, +0.5],
    [+1.0, -1.0], [+0.5, -0.5],
    [-1.0, -1.0], [-0.5, -0.5]
], dtype=float)

# Per-vertex RGB colors (strip shares colors at repeated vertices)
color = array([
    [+1.0, +0.0, +0.0], [+1.0, +0.0, +0.0],
    [+0.0, +0.0, +1.0], [+0.0, +0.0, +1.0],
    [+1.0, +0.0, +1.0], [+1.0, +0.0, +1.0],
    [+0.0, +1.0, +0.0], [+0.0, +1.0, +0.0],
    [+1.0, +0.0, +0.0], [+1.0, +0.0, +0.0]
], dtype=float)

# Start time for animation
start_time = None

def init():
    global start_time
    glClearColor(+0.6, +0.7, +0.82, +1.0)  # Set background color
    gluOrtho2D(-2.0, +2.0, -2.0, +2.0)   # Set orthographic projection
    start_time = time.perf_counter()   # Record start time

def display():
    global start_time
    glClear(GL_COLOR_BUFFER_BIT)
    glPushMatrix()
    # Calculate smooth angle based on elapsed time
    elapsed = time.perf_counter() - start_time
    angle = (elapsed * +60.0) % +360.0  # 60 degrees per second
    # Horizontal translation from left to right; viewport is [-2, 2], so travel span is 4
    speed = +0.7  # units per second
    width = +4.0
    x = (elapsed * speed) % width - 2.0

    # Draw three copies (left, center, right) so when one exits, the next is already entering
    for offset in [-width, +0, width]:
        glPushMatrix()
        glTranslatef(x + offset, +0.0, +0.0)
        glRotatef(angle, +0.0, +0.0, +1.0)
        square()
        glPopMatrix()

    # Pop the initial matrix push to keep the stack balanced
    glPopMatrix()

    glFlush()

def idle():
    # Continuously request redisplay so animation keeps updating
    glutPostRedisplay()

def square():
    # Draw the colored square using a triangle strip (10 vertices)
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(+0, +10):
        glColor3fv(color[i])
        glVertex2fv(vertices[i])
    glEnd()

if __name__ == "__main__":
    # Initialize GLUT and create window
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowPosition(+300, +300)
    glutInitWindowSize(+500, +500)
    glutCreateWindow(b'Window')
    init()
    # Register display and idle callbacks
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    # Start the main loop (blocks here)
    glutMainLoop()