"""
06_textured_perspective.py
==========================
Displays a textured square in 3D perspective that rotates around the Y axis.

Key concepts demonstrated:
  - gluPerspective for perspective projection (replaces glFrustum).
  - Reshape callback to keep the aspect ratio correct when the window is resized.
  - Time-based rotation stored internally in radians; converted to degrees only
    for glRotatef.
  - Double buffering (GLUT_DOUBLE) for smooth animation.
  - Depth testing (GL_DEPTH_TEST) to handle correct face ordering.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
from PIL import Image

# -- Configuration --------------------------------------------------------------
TEXTURE_PATH = "img/box.jpg"
FOV_Y = 60.0             # Vertical field-of-view for gluPerspective (degrees, API requirement)
NEAR_PLANE = 0.1          # Distance to the near clipping plane
FAR_PLANE = 100.0         # Distance to the far clipping plane
WINDOW_W = 750
WINDOW_H = 750
ROTATION_SPEED = math.pi / 6.0  # Rotation speed: pi/6 rad/s (~ 30deg/s)

# -- Geometry (square lying in the XY plane, z = 0) ----------------------------
quad_texcoords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
quad_vertices = [(-1.0, -1.0, 0.0), (1.0, -1.0, 0.0),
                 (1.0, 1.0, 0.0), (-1.0, 1.0, 0.0)]

# -- Global state ---------------------------------------------------------------
angle_rad = 0.0           # Current rotation angle in radians
last_time = None           # Previous frame timestamp (seconds)
tex_w = tex_h = None
tex_bytes = None


def load_texture():
    """Load an image from disk and store its raw RGBA pixel data."""
    global tex_w, tex_h, tex_bytes
    image = Image.open(TEXTURE_PATH).convert("RGBA")
    tex_w, tex_h = image.size
    tex_bytes = image.tobytes("raw", "RGBA", 0, -1)


def init():
    """One-time OpenGL setup: background, depth test, and texture upload."""
    glClearColor(0.0, 0.0, 0.2, 1.0)       # Dark blue background
    glEnable(GL_DEPTH_TEST)                  # Enable depth testing

    # Texture filtering and wrap mode
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    # Upload texture to the GPU
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA,
        tex_w, tex_h, 0,
        GL_RGBA, GL_UNSIGNED_BYTE, tex_bytes,
    )


def reshape(w, h):
    """
    Reshape callback: recalculates the projection matrix whenever the
    window is resized, keeping the aspect ratio correct.
    """
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = w / float(h)
    # gluPerspective expects the FOV in degrees (OpenGL convention)
    gluPerspective(FOV_Y, aspect, NEAR_PLANE, FAR_PLANE)
    glMatrixMode(GL_MODELVIEW)


def update_angle():
    """Advance the rotation angle based on real elapsed time (radians)."""
    global angle_rad, last_time
    current = glutGet(GLUT_ELAPSED_TIME) / 1000.0  # milliseconds -> seconds
    if last_time is None:
        last_time = current
    dt = current - last_time
    last_time = current
    # Accumulate angle in radians; wrap at 2pi to avoid overflow
    angle_rad = (angle_rad + ROTATION_SPEED * dt) % (2.0 * math.pi)


def display():
    """
    Display callback.
    1. Updates the angle.
    2. Positions the camera (translate along -Z).
    3. Rotates the quad around the Y axis.
    4. Draws the textured quad.
    """
    update_angle()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Move the scene away from the camera so it is visible
    glTranslatef(0.0, 0.0, -6.0)

    # Rotate around Y axis -- convert radians -> degrees for glRotatef
    glRotatef(math.degrees(angle_rad), 0.0, 1.0, 0.0)

    # Draw the textured quad
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    for (u, v), (x, y, z) in zip(quad_texcoords, quad_vertices):
        glTexCoord2f(u, v)
        glVertex3f(x, y, z)
    glEnd()
    glDisable(GL_TEXTURE_2D)

    glutSwapBuffers()  # Swap front and back buffers (double buffering)


def idle():
    """Request continuous redisplay for animation."""
    glutPostRedisplay()


# -- Main entry point ----------------------------------------------------------
if __name__ == "__main__":
    load_texture()
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowPosition(0, 0)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"Textured Square in Perspective")
    init()
    reshape(WINDOW_W, WINDOW_H)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    glutMainLoop()
