"""
02_square.py
============
Draws a static coloured square (actually a frame shape) using GL_TRIANGLE_STRIP.

Key concepts demonstrated:
  - Defining geometry with NumPy arrays of 2D vertices.
  - Per-vertex colouring with glColor3fv / glVertex2fv.
  - GL_TRIANGLE_STRIP primitive: pairs of outer and inner vertices form
    a continuous strip of triangles that together produce a coloured frame.
  - 2D orthographic projection with gluOrtho2D.

No animation or rotation is used here -- this is a purely static scene.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from numpy import array
import sys

# -- Geometry -------------------------------------------------------------------
# 10 vertices alternate between outer and inner edges of the frame.
# The strip closes by repeating the first pair at the end.
vertices = array([
    [-1.0, -0.5], [-0.5, -0.25],   # bottom edge (outer, inner)
    [-1.0, +0.5], [-0.5, +0.25],   # left edge
    [+1.0, +0.5], [+0.5, +0.25],   # top edge
    [+1.0, -0.5], [+0.5, -0.25],   # right edge
    [-1.0, -0.5], [-0.5, -0.25],   # close the strip
], dtype=float)

# -- Per-vertex colours (RGB) --------------------------------------------------
# Each vertex gets its own colour; OpenGL interpolates across each triangle.
color = array([
    [1.0, 0.0, 0.0], [0.0, 1.0, 0.0],   # red / green
    [0.0, 0.0, 1.0], [1.0, 1.0, 0.0],   # blue / yellow
    [1.0, 0.0, 1.0], [0.0, 1.0, 1.0],   # magenta / cyan
    [0.5, 0.5, 0.5], [0.2, 0.2, 0.2],   # grey / dark grey
    [1.0, 0.0, 0.0], [0.0, 1.0, 0.0],   # red / green (closing pair)
], dtype=float)

NUM_VERTICES = len(vertices)  # Total vertices in the strip


def init():
    """One-time OpenGL setup: background colour and 2D projection."""
    glClearColor(0.6, 0.7, 0.82, 1.0)       # Light blue-grey background
    gluOrtho2D(-2.0, 2.0, -2.0, 2.0)        # Orthographic projection


def square():
    """
    Display callback.
    Clears the screen and draws the coloured frame using a triangle strip.
    """
    glClear(GL_COLOR_BUFFER_BIT)

    # Draw the frame as a continuous triangle strip
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(NUM_VERTICES):
        glColor3fv(color[i])       # Set colour for this vertex
        glVertex2fv(vertices[i])   # Emit the vertex
    glEnd()

    glFlush()  # Force execution of all GL commands


# -- Main entry point ----------------------------------------------------------
if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowPosition(300, 300)
    glutInitWindowSize(500, 500)
    glutCreateWindow(b"Coloured Square")
    init()
    glutDisplayFunc(square)
    glutMainLoop()
