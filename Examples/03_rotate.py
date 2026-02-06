"""
03_rotate.py
============
A coloured square that rotates and scrolls horizontally, wrapping seamlessly
from right to left so it never disappears.

Key concepts demonstrated:
  - Time-based animation with radians (converted to degrees only for glRotatef).
  - glPushMatrix / glPopMatrix to isolate transformations.
  - Seamless horizontal wrapping by drawing three offset copies of the shape.
  - GL_TRIANGLE_STRIP with per-vertex colour.

All internal angles are stored and computed in **radians**.
The only conversion to degrees happens at the glRotatef call, which requires it.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from numpy import array
import math
import time
import sys

# -- Configuration --------------------------------------------------------------
ROTATION_SPEED = math.pi / 3.0  # Rotation speed: pi/3 rad/s  (~ 60deg/s)
SCROLL_SPEED = 0.7              # Horizontal translation speed (units/s)
VIEWPORT_HALF = 2.0             # Orthographic range: [-2, +2]
VIEWPORT_WIDTH = 2.0 * VIEWPORT_HALF  # Total visible width = 4.0 units

# -- Geometry -------------------------------------------------------------------
# 10 vertices: pairs of (outer, inner) forming a frame via GL_TRIANGLE_STRIP.
# The last pair repeats the first to close the shape.
vertices = array([
    [-1.0, -1.0], [-0.5, -0.5],
    [-1.0, +1.0], [-0.5, +0.5],
    [+1.0, +1.0], [+0.5, +0.5],
    [+1.0, -1.0], [+0.5, -0.5],
    [-1.0, -1.0], [-0.5, -0.5],
], dtype=float)

# -- Per-vertex RGB colours ----------------------------------------------------
color = array([
    [+1.0, +0.0, +0.0], [+1.0, +0.0, +0.0],   # red
    [+0.0, +0.0, +1.0], [+0.0, +0.0, +1.0],   # blue
    [+1.0, +0.0, +1.0], [+1.0, +0.0, +1.0],   # magenta
    [+0.0, +1.0, +0.0], [+0.0, +1.0, +0.0],   # green
    [+1.0, +0.0, +0.0], [+1.0, +0.0, +0.0],   # red (closing pair)
], dtype=float)

NUM_VERTICES = len(vertices)

# -- Global state ---------------------------------------------------------------
start_time = None  # Set once in init(); reference for elapsed time


def init():
    """Set up background colour, orthographic projection, and start timer."""
    global start_time
    glClearColor(+0.6, +0.7, +0.82, +1.0)                # Light blue-grey
    gluOrtho2D(-VIEWPORT_HALF, +VIEWPORT_HALF,
               -VIEWPORT_HALF, +VIEWPORT_HALF)             # 2D projection
    start_time = time.perf_counter()


def display():
    """
    Display callback.
    1. Computes elapsed time.
    2. Derives rotation angle (radians) and horizontal offset.
    3. Draws three copies of the shape (left, centre, right) so wrapping
       is perfectly seamless -- as one copy exits the viewport on the right,
       the next is already entering from the left.
    """
    glClear(GL_COLOR_BUFFER_BIT)

    elapsed = time.perf_counter() - start_time

    # Rotation angle in radians; increases at ROTATION_SPEED rad/s
    angle_rad = (elapsed * ROTATION_SPEED) % (2.0 * math.pi)

    # Horizontal position: wraps within [-VIEWPORT_HALF, +VIEWPORT_HALF]
    x = (elapsed * SCROLL_SPEED) % VIEWPORT_WIDTH - VIEWPORT_HALF

    # Draw three offset copies for seamless wrap-around
    for offset in [-VIEWPORT_WIDTH, 0.0, +VIEWPORT_WIDTH]:
        glPushMatrix()
        glTranslatef(x + offset, +0.0, +0.0)
        # glRotatef requires degrees -> convert only here
        glRotatef(math.degrees(angle_rad), +0.0, +0.0, +1.0)
        draw_square()
        glPopMatrix()

    glFlush()


def idle():
    """Request continuous redisplay to keep the animation running."""
    glutPostRedisplay()


def draw_square():
    """Draw the coloured frame shape using a triangle strip."""
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(NUM_VERTICES):
        glColor3fv(color[i])
        glVertex2fv(vertices[i])
    glEnd()


# -- Main entry point ----------------------------------------------------------
if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowPosition(+300, +300)
    glutInitWindowSize(+500, +500)
    glutCreateWindow(b"Rotating & Scrolling Square")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutMainLoop()
