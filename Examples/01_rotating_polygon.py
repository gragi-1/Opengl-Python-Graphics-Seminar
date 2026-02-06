"""
01_rotating_polygon.py
======================
Draws a regular polygon (default: hexagon) that rotates smoothly over time.

Key concepts demonstrated:
  - GLUT window creation and event loop.
  - 2D orthographic projection with gluOrtho2D.
  - Drawing a GL_POLYGON with vertices placed using polar coordinates (radians).
  - Time-based animation via idle callback and time.perf_counter().

The rotation angle is computed directly from wall-clock time in radians,
so the polygon spins at a constant angular velocity regardless of frame rate.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
import math
import time
import sys

# -- Configuration --------------------------------------------------------------
NUM_SIDES = 6        # Number of sides of the regular polygon
RADIUS = 1.7         # Distance from center to each vertex
ANGULAR_SPEED = 1.0  # Rotation speed in radians per second
BG_COLOR = (0.6, 0.7, 0.82, 1.0)  # Light blue-grey background (RGBA)
POLY_COLOR = (0.9, 0.2, 0.15)     # Red-orange polygon fill (RGB)

# -- Global state ---------------------------------------------------------------
start_time = None  # Recorded once at startup; used as animation reference


def init():
    """One-time OpenGL setup: background colour and 2D projection."""
    global start_time
    glClearColor(*BG_COLOR)
    # Orthographic projection mapping world coords [-2, 2] to the viewport
    gluOrtho2D(-2.0, 2.0, -2.0, 2.0)
    start_time = time.perf_counter()


def display():
    """
    Called every frame.  Computes the current rotation angle in radians
    from elapsed time and draws the polygon.
    """
    elapsed = time.perf_counter() - start_time
    # Current rotation angle (radians); increases linearly with time
    angle_rad = elapsed * ANGULAR_SPEED

    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(*POLY_COLOR)

    # Draw a regular polygon centered at the origin
    glBegin(GL_POLYGON)
    for i in range(NUM_SIDES):
        # Evenly-spaced vertex angle in radians: i * (2pi / n)
        vertex_angle = angle_rad + i * 2.0 * math.pi / NUM_SIDES
        x = RADIUS * math.sin(vertex_angle)
        y = RADIUS * math.cos(vertex_angle)
        glVertex2f(x, y)
    glEnd()

    glFlush()


def idle():
    """Idle callback: continuously requests a redisplay so the animation runs."""
    glutPostRedisplay()


# -- Main entry point ----------------------------------------------------------
if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowPosition(300, 300)
    glutInitWindowSize(500, 500)
    glutCreateWindow(b"Rotating Polygon")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutMainLoop()
