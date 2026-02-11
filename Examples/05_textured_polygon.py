"""
05_textured_polygon.py
======================
Textures a regular polygon of N sides using a polar texture-coordinate mapping.

Key concepts demonstrated:
  - Regular polygon vertices computed with trigonometry (radians).
  - Polar texture mapping: each vertex gets (u, v) based on its angle from
    the polygon centre, centred at (0.5, 0.5) in texture space.
  - GL_REPEAT vs GL_CLAMP_TO_EDGE wrap modes -- see what happens when texture
    coordinates fall outside [0, 1]^2 by increasing COORD_SCALE.
  - Loading and uploading a texture with PIL.

Change COORD_SCALE to a value > 1.0 to push texture coordinates outside [0, 1]
and observe how the wrap mode affects the result.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
from PIL import Image

# -- Configuration --------------------------------------------------------------
N_SIDES = 13          # Number of sides of the regular polygon
RADIUS = 1.2          # Radius of the polygon in world units
TEXTURE_PATH = "img/box.jpg"
USE_REPEAT = True     # True -> GL_REPEAT (tile); False -> GL_CLAMP_TO_EDGE
COORD_SCALE = 0.5     # Multiplier for texture coords; > 1.0 goes outside [0, 1]

# -- Texture data (populated by load_texture) -----------------------------------
tex_width = None
tex_height = None
tex_bytes = None


def load_texture():
    """Load the texture image from disk and convert to raw RGBA bytes."""
    global tex_width, tex_height, tex_bytes
    image = Image.open(TEXTURE_PATH).convert("RGBA")
    tex_width, tex_height = image.size
    tex_bytes = image.tobytes("raw", "RGBA", 0, -1)


def init():
    """Set up background colour, 2D projection, and texture parameters."""
    glClearColor(0.9, 0.9, 0.95, 1.0)      # Near-white background
    glMatrixMode(GL_PROJECTION)
    gluOrtho2D(-2.0, 2.0, -2.0, 2.0)       # Orthographic projection
    glMatrixMode(GL_MODELVIEW)

    # Choose wrap mode based on configuration flag
    wrap_mode = GL_REPEAT if USE_REPEAT else GL_CLAMP_TO_EDGE
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap_mode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap_mode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    # Upload texture to the GPU once
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA,
        tex_width, tex_height, 0,
        GL_RGBA, GL_UNSIGNED_BYTE, tex_bytes,
    )


def draw_textured_polygon():
    """
    Display callback.
    Draws a regular N-sided polygon with texture coordinates derived from
    polar mapping around the polygon centre.
    """
    glClear(GL_COLOR_BUFFER_BIT)
    glEnable(GL_TEXTURE_2D)

    glBegin(GL_POLYGON)
    for i in range(N_SIDES):
        # Vertex angle in radians: evenly spaced around the circle
        theta = 2.0 * math.pi * i / N_SIDES

        # World-space vertex position (polar -> cartesian)
        x = RADIUS * math.cos(theta)
        y = RADIUS * math.sin(theta)

        # Texture coordinates centred at (0.5, 0.5).
        # COORD_SCALE > 1.0 pushes coords outside [0, 1] to demonstrate
        # the effect of GL_REPEAT vs GL_CLAMP_TO_EDGE.
        u = 0.5 + 0.5 * math.cos(theta) * COORD_SCALE
        v = 0.5 + 0.5 * math.sin(theta) * COORD_SCALE

        glTexCoord2f(u, v)
        glVertex2f(x, y)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glFlush()


# -- Main entry point ----------------------------------------------------------
if __name__ == "__main__":
    load_texture()
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
    glutInitWindowPosition(200, 300)
    glutInitWindowSize(600, 600)
    glutCreateWindow(b"Textured Regular Polygon")
    init()
    glutDisplayFunc(draw_textured_polygon)
    glutMainLoop()
