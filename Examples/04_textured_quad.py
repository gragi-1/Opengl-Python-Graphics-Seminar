"""
04_textured_quad.py
===================
Displays a textured quad (square) using an image loaded with PIL.

Key concepts demonstrated:
  - Loading an image with PIL and uploading it to OpenGL as a 2D texture.
  - Mapping texture coordinates (u, v) to quad vertices.
  - GL_QUADS primitive for drawing a textured rectangle.
  - 2D orthographic projection.

No animation -- this is a static textured scene.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
from PIL import Image

# -- Configuration --------------------------------------------------------------
TEXTURE_PATH = "img/box.jpg"

# -- Texture data (loaded at module level for simplicity) ----------------------
image = Image.open(TEXTURE_PATH)
tex_width = image.size[0]       # Texture width in pixels
tex_height = image.size[1]      # Texture height in pixels
tex_bytes = image.tobytes("raw", "RGBX", 0, -1)  # Raw pixel data


def init():
    """Set up background colour, 2D projection, and texture parameters."""
    glClearColor(1.0, 1.0, 1.0, 0.0)       # White background
    glMatrixMode(GL_PROJECTION)
    gluOrtho2D(-2.0, 2.0, -2.0, 2.0)       # Orthographic projection
    glMatrixMode(GL_MODELVIEW)


def draw_textured_quad():
    """
    Display callback.
    Uploads the texture each frame (simple approach) and draws a quad
    spanning [-1, 1] in both axes with full texture mapping [0, 1]^2.
    """
    glClear(GL_COLOR_BUFFER_BIT)

    # Set texture filtering: nearest-neighbour (sharp, pixel-art style)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    # Upload the texture image to the GPU
    glTexImage2D(
        GL_TEXTURE_2D, 0, 3,
        tex_width, tex_height, 0,
        GL_RGBA, GL_UNSIGNED_BYTE, tex_bytes,
    )

    # Enable texturing, draw the quad, then disable texturing
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    #        tex coord (u,v)        vertex (x, y)
    glTexCoord2f(0.0, 0.0);  glVertex2f(-1.0, -1.0)   # bottom-left
    glTexCoord2f(0.0, 1.0);  glVertex2f(-1.0, +1.0)   # top-left
    glTexCoord2f(1.0, 1.0);  glVertex2f(+1.0, +1.0)   # top-right
    glTexCoord2f(1.0, 0.0);  glVertex2f(+1.0, -1.0)   # bottom-right
    glEnd()
    glDisable(GL_TEXTURE_2D)

    glFlush()


# -- Main entry point ----------------------------------------------------------
if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
    glutInitWindowPosition(200, 500)
    glutInitWindowSize(500, 500)
    glutCreateWindow(b"Textured Quad")
    init()
    glutDisplayFunc(draw_textured_quad)
    glutMainLoop()
