"""
08_dual_orbit_cubes.py
======================
Two textured cubes that spin on their own axes while orbiting a common centre
in different planes:
  - Cube A orbits in the XY plane (rotation around the Z axis).
  - Cube B orbits in the XZ plane (rotation around the Y axis).

Key concepts demonstrated:
  - 3D textured cube built with vertex arrays and a display list.
  - Perspective projection with gluPerspective.
  - Hierarchical transforms with glPushMatrix / glPopMatrix.
  - Orbital positions computed with sin/cos in radians.
  - All internal angles in radians; converted to degrees only for glRotatef.
  - Depth testing for correct face ordering.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
from PIL import Image

# -- Window / projection -------------------------------------------------------
WINDOW_W = 800
WINDOW_H = 800
FOV_Y = 65.0          # gluPerspective FOV (degrees, API requirement)
NEAR_PLANE = 10.0
FAR_PLANE = 1000.0
CAMERA_Z = -120.0     # Camera pull-back along -Z

# -- Animation speeds (radians per second) -------------------------------------
SELF_SPIN_SPEED = 2.0 * math.pi / 9.0    # ~ 40deg/s  (self-rotation)
ORBIT_SPEED_XY = 2.0 * math.pi / 14.4    # ~ 25deg/s  (XY-plane orbit)
ORBIT_SPEED_XZ = 2.0 * math.pi / 24.0    # ~ 15deg/s  (XZ-plane orbit)
ORBIT_RADIUS = 45.0                       # Distance from the centre of the scene
CUBE_SCALE = 18.0                         # Uniform scale applied to each cube

# -- Texture --------------------------------------------------------------------
TEXTURE_PATH = "img/box.jpg"

# -- Cube geometry --------------------------------------------------------------
# 8 unique vertices of a unit cube [0, 1]^3
VERTEX_CUBE = [
    (0.0, 0.0, 0.0), (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0), (1.0, 1.0, 0.0),
    (0.0, 0.0, 1.0), (1.0, 0.0, 1.0),
    (0.0, 1.0, 1.0), (1.0, 1.0, 1.0),
]

# Face indices (6 faces x 4 vertices each, drawn as GL_QUADS)
INDEX_CUBE = [
    0, 1, 3, 2,  # face z = 0
    4, 5, 7, 6,  # face z = 1
    0, 1, 5, 4,  # face y = 0
    2, 3, 7, 6,  # face y = 1
    1, 3, 7, 5,  # face x = 1
    0, 2, 6, 4,  # face x = 0
]

# Texture coordinates: the same [0,1]^2 quad is tiled on every face
SQUARE_TEX = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)] * 6

# -- Global state ---------------------------------------------------------------
cube_list = None                # Display list id
tex_w = tex_h = None
tex_bytes = None
last_time = None
self_angle = 0.0                # Self-rotation (radians)
orbit_angle_xy = 0.0            # Orbit in XY plane (radians)
orbit_angle_xz = 0.0            # Orbit in XZ plane (radians)


# -- Texture loading -----------------------------------------------------------
def load_texture():
    """Read the image file and store raw RGBA pixel data."""
    global tex_w, tex_h, tex_bytes
    image = Image.open(TEXTURE_PATH).convert("RGBA")
    tex_w, tex_h = image.size
    tex_bytes = image.tobytes("raw", "RGBA", 0, -1)


# -- Display list ---------------------------------------------------------------
def build_cube_list():
    """
    Compile a display list for the unit cube.
    The cube is centred at the origin via a translate(-0.5) inside the list,
    so callers only need to scale and position it.
    """
    global cube_list
    # Expand indexed vertices into a flat list for glVertexPointer
    verts = [VERTEX_CUBE[i] for i in INDEX_CUBE]

    cube_list = glGenLists(1)
    glNewList(cube_list, GL_COMPILE)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Centre the cube at the origin (vertices go from 0->1, shift by -0.5)
    glPushMatrix()
    glTranslatef(-0.5, -0.5, -0.5)

    # Use vertex arrays for efficient rendering
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, verts)
    glTexCoordPointer(2, GL_FLOAT, 0, SQUARE_TEX)
    glDrawArrays(GL_QUADS, 0, len(verts))
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)

    glPopMatrix()
    glEndList()


# -- Init -----------------------------------------------------------------------
def init():
    """Background, depth test, texture upload, and projection setup."""
    glClearColor(0.0, 0.0, 0.0, 0.0)         # Black background
    glEnable(GL_DEPTH_TEST)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glDisable(GL_CULL_FACE)                    # Show both faces of each quad
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    # Texture setup
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, tex_w, tex_h, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, tex_bytes)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glEnable(GL_TEXTURE_2D)

    # Perspective projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = WINDOW_W / float(WINDOW_H)
    gluPerspective(FOV_Y, aspect, NEAR_PLANE, FAR_PLANE)
    glMatrixMode(GL_MODELVIEW)


def reshape(w, h):
    """Recalculate projection when the window is resized."""
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV_Y, w / float(h), NEAR_PLANE, FAR_PLANE)
    glMatrixMode(GL_MODELVIEW)


# -- Animation ------------------------------------------------------------------
def update_angles():
    """Advance all angles using real elapsed time (radians)."""
    global last_time, self_angle, orbit_angle_xy, orbit_angle_xz
    current = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    if last_time is None:
        last_time = current
    dt = current - last_time
    last_time = current
    self_angle = (self_angle + SELF_SPIN_SPEED * dt) % (2.0 * math.pi)
    orbit_angle_xy = (orbit_angle_xy + ORBIT_SPEED_XY * dt) % (2.0 * math.pi)
    orbit_angle_xz = (orbit_angle_xz + ORBIT_SPEED_XZ * dt) % (2.0 * math.pi)


def draw_cube(position, spin_axis=(1.0, 2.0, 0.0), spin_angle_rad=0.0):
    """
    Draw a scaled, rotated cube at *position*.
    The spin angle is in radians and converted to degrees for glRotatef.
    """
    glPushMatrix()
    glTranslatef(*position)
    glScalef(CUBE_SCALE, CUBE_SCALE, CUBE_SCALE)
    glRotatef(math.degrees(spin_angle_rad), *spin_axis)
    glCallList(cube_list)
    glPopMatrix()


# -- Display --------------------------------------------------------------------
def display():
    """
    Display callback.
    - Cube A: orbits in the XY plane.  Its position is computed with
      cos/sin of orbit_angle_xy (radians) -> (x, y) on a circle.
    - Cube B: orbits in the XZ plane.  Same idea with orbit_angle_xz -> (x, z).
    Both cubes also spin on their own axes.
    """
    update_angles()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Pull the camera back so both orbits are visible
    glTranslatef(0.0, 0.0, CAMERA_Z)

    # -- Cube A: orbits in the XY plane (circle around Z) -----------------
    x_a = ORBIT_RADIUS * math.cos(orbit_angle_xy)  # radians -> cos/sin
    y_a = ORBIT_RADIUS * math.sin(orbit_angle_xy)
    draw_cube((x_a, y_a, 0.0), spin_angle_rad=self_angle)

    # -- Cube B: orbits in the XZ plane (circle around Y) -----------------
    x_b = ORBIT_RADIUS * math.cos(orbit_angle_xz)
    z_b = ORBIT_RADIUS * math.sin(orbit_angle_xz)
    draw_cube((x_b, 0.0, z_b), spin_axis=(1.0, -1.0, 1.0),
              spin_angle_rad=self_angle)

    glutSwapBuffers()


def idle():
    """Request continuous redisplay for animation."""
    glutPostRedisplay()


# -- Main entry point ----------------------------------------------------------
if __name__ == "__main__":
    load_texture()
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowPosition(0, 0)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"Dual Orbiting Textured Cubes")
    init()
    build_cube_list()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutReshapeFunc(reshape)
    glutMainLoop()
