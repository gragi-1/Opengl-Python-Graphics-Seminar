"""
07_textured_planes_matrices.py
==============================
Two textured planes in 3D perspective:
  - Plane A spins in place.
  - Plane B spins on its own axis AND orbits around Plane A.

Key concepts demonstrated:
  - gluPerspective for perspective projection.
  - glPushMatrix / glPopMatrix to isolate hierarchical transformations:
    the orbiting plane's transform is built on top of the scene's base
    transform without affecting Plane A.
  - glGetDoublev(GL_PROJECTION_MATRIX) to inspect the projection matrix
    and verify that it is NOT affine (last row != [0 0 0 1]).
  - Internal angles stored in radians; converted to degrees only for glRotatef.
  - Display list for efficient repeated drawing.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
from PIL import Image

# -- Configuration --------------------------------------------------------------
TEXTURE_PATH = "img/box.jpg"
FOV_Y = 25.0              # Vertical field-of-view (degrees, API requirement)
NEAR_PLANE = 100.0
FAR_PLANE = 1000.0
WINDOW_W = 550
WINDOW_H = 550

# Animation speeds in radians per second
SELF_SPIN_SPEED = 2.0 * math.pi / 9.0   # ~ 40deg/s  (self-rotation)
ORBIT_SPEED = 2.0 * math.pi / 18.0      # ~ 20deg/s  (orbit around plane A)
ORBIT_RADIUS = 20.0                      # Distance of orbiting plane from origin

# -- Geometry (square in the XY plane) -----------------------------------------
QUAD_TEXCOORDS = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
QUAD_VERTICES = [(-1.0, -1.0, 0.0), (1.0, -1.0, 0.0),
                 (1.0, 1.0, 0.0), (-1.0, 1.0, 0.0)]

# -- Global state ---------------------------------------------------------------
plane_list = None          # OpenGL display list id
tex_w = tex_h = None
tex_bytes = None
last_time = None
self_angle = 0.0           # Self-rotation angle (radians)
orbit_angle = 0.0          # Orbit angle (radians)
projection_logged = False  # Print the projection matrix only once


def load_texture():
    """Load the texture image and store raw RGBA bytes."""
    global tex_w, tex_h, tex_bytes
    image = Image.open(TEXTURE_PATH).convert("RGBA")
    tex_w, tex_h = image.size
    tex_bytes = image.tobytes("raw", "RGBA", 0, -1)


def build_plane_list():
    """
    Compile a display list that draws a textured quad.
    Using a display list avoids re-issuing all GL commands every frame.
    """
    global plane_list
    plane_list = glGenLists(1)
    glNewList(plane_list, GL_COMPILE)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tex_w, tex_h, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, tex_bytes)

    glEnable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    for (u, v), (x, y, z) in zip(QUAD_TEXCOORDS, QUAD_VERTICES):
        glTexCoord2f(u, v)
        glVertex3f(x, y, z)
    glEnd()
    glDisable(GL_TEXTURE_2D)

    glEndList()


def init():
    """Background colour, depth test, and perspective projection."""
    glClearColor(0.0, 0.0, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = WINDOW_W / float(WINDOW_H)
    gluPerspective(FOV_Y, aspect, NEAR_PLANE, FAR_PLANE)
    glMatrixMode(GL_MODELVIEW)


def reshape(w, h):
    """Recalculate projection on resize; also log the matrix once."""
    global projection_logged
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV_Y, w / float(h), NEAR_PLANE, FAR_PLANE)
    glMatrixMode(GL_MODELVIEW)

    # Print the projection matrix once to verify it is NOT affine.
    # An affine matrix has last row = [0, 0, 0, 1].
    # A perspective matrix has last row ~ [0, 0, -1, 0] -> not affine.
    if not projection_logged:
        proj = glGetDoublev(GL_PROJECTION_MATRIX)
        print("Projection matrix (perspective -- NOT affine):")
        for row in range(4):
            print("  ", [round(proj[row][col], 6) for col in range(4)])
        print("Last row != [0, 0, 0, 1] -> confirms non-affine projection.\n")
        projection_logged = True


def update_angles():
    """Advance both angles using real elapsed time (radians)."""
    global last_time, self_angle, orbit_angle
    current = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    if last_time is None:
        last_time = current
    dt = current - last_time
    last_time = current
    self_angle = (self_angle + SELF_SPIN_SPEED * dt) % (2.0 * math.pi)
    orbit_angle = (orbit_angle + ORBIT_SPEED * dt) % (2.0 * math.pi)


def draw_plane(position, spin_axis, spin_angle_rad, scale=5.0):
    """
    Helper: translate to *position*, scale, rotate by *spin_angle_rad*
    around *spin_axis*, then draw the compiled plane display list.
    """
    glTranslatef(*position)
    glScalef(scale, scale, 1.0)
    # Convert radians -> degrees for glRotatef
    glRotatef(math.degrees(spin_angle_rad), *spin_axis)
    glCallList(plane_list)


def display():
    """
    Display callback.
    - Plane A: translated to the left, spins in place.
    - Plane B: orbits around the Y axis, then spins on its own axis.
    glPushMatrix / glPopMatrix ensure each plane's transformations do not
    leak into the other.
    """
    update_angles()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Base camera transform: pull everything back along -Z
    glTranslatef(0.0, 0.0, -150.0)

    # -- Plane A: spins in place -------------------------------------------
    glPushMatrix()
    draw_plane(
        position=(-10.0, 0.0, 0.0),
        spin_axis=(1.0, 1.0, 1.0),
        spin_angle_rad=self_angle,
    )
    glPopMatrix()

    # -- Plane B: orbits around Plane A and also spins ---------------------
    glPushMatrix()
    # First, rotate the entire coordinate frame around Y -> creates the orbit
    glRotatef(math.degrees(orbit_angle), 0.0, 1.0, 0.0)
    # Then translate outward to the orbit radius
    glTranslatef(ORBIT_RADIUS, 0.0, 0.0)
    # Finally, draw the plane with its own spin
    draw_plane(
        position=(0.0, 0.0, 0.0),
        spin_axis=(1.0, -1.0, 1.0),
        spin_angle_rad=self_angle,
    )
    glPopMatrix()

    glutSwapBuffers()


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
    glutCreateWindow(b"Textured Planes - Matrices & Perspective")
    init()
    build_plane_list()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    glutMainLoop()
