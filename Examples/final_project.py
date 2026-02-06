"""
final_project.py -- Enhanced Solar System Simulation
=====================================================
A visually rich, physically-inspired simulation of the complete Solar System
rendered in real-time with OpenGL.

Features
--------
  * All 8 planets (Mercury through Neptune) with correct relative ordering.
  * Earth has three layers: day-side texture, night-side city-lights texture
    (via additive blending), and a semi-transparent cloud layer that
    rotates at a different speed to the surface.
  * Saturn has a textured ring (alpha-blended from saturn_ring.png).
  * Milky Way panorama mapped onto a large inverted skysphere as a
    photographic backdrop behind all scene geometry.
  * A dense starfield of ~2 500 stars that twinkle smoothly (random phase +
    sinusoidal brightness oscillation) layered on top of the backdrop.
  * Point-light source at the Sun position so day/night shading is physical.
  * The Moon orbits Earth with tidal locking.
  * Interactive camera: arrow keys orbit, +/- zoom, H resets.
  * Smooth time-based animation using high-resolution elapsed time.
  * Orbit lines drawn as faint coloured circles for each planet.
  * Orbital planes are tilted to their real astronomical inclinations and
    ascending nodes (J2000 epoch) so each orbit ring sits at its correct
    angle relative to the ecliptic.  Mercury's 7-degree tilt is clearly
    visible; the outer planets show subtler but physically accurate offsets.

Conventions
-----------
  * All internal angles are stored in **radians**.
  * Degrees appear ONLY at the OpenGL API boundary (glRotatef, gluPerspective).
  * All text in this file is 100% ASCII.

Controls
--------
  LEFT / RIGHT  -- orbit camera horizontally
  UP / DOWN     -- orbit camera vertically
  + / -         -- zoom in / out
  Space         -- pause / resume the simulation
  H             -- reset camera to default position
  Esc           -- quit
"""

# ---------------------------------------------------------------------------
#  Imports
# ---------------------------------------------------------------------------
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import ctypes
import math
import os
import random
import sys
from PIL import Image

# PyOpenGL exposes GLUT bitmap fonts via dynamic attribute lookup, which
# confuses static analysers (Pylance).  Resolve the pointer once here.
try:
    _FONT = GLUT_BITMAP_HELVETICA_18          # type: ignore[name-defined]
except NameError:
    # Fallback: build the ctypes pointer manually (FreeGLUT)
    _FONT = ctypes.c_void_p(+8)

# ---------------------------------------------------------------------------
#  Base directory for resource loading (PyInstaller compatibility)
# ---------------------------------------------------------------------------
# When frozen into a .exe, PyInstaller extracts data files into a temp
# folder referenced by sys._MEIPASS.  When running from source the base
# is one level up from the Examples/ directory (the repo root).
if getattr(sys, 'frozen', False):
    _BASE_DIR = sys._MEIPASS                       # type: ignore[attr-defined]
else:
    _BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
_BASE_DIR = os.path.abspath(_BASE_DIR)


def _res(relative_path):
    """Resolve a repo-relative path to an absolute path."""
    return os.path.join(_BASE_DIR, relative_path)


# ---------------------------------------------------------------------------
#  Window / projection constants
# ---------------------------------------------------------------------------
WINDOW_W, WINDOW_H = +1400, +850
NEAR_PLANE  = +1.0
FAR_PLANE   = +5000.0
FOV_Y       = +45.0  # degrees -- gluPerspective expects degrees

# ---------------------------------------------------------------------------
#  Texture paths (resolved via _res for source and frozen .exe)
# ---------------------------------------------------------------------------
TEX_SUN          = _res("img/sun.jpg")
TEX_MERCURY      = _res("img/mercury.jpg")
TEX_VENUS        = _res("img/venus.jpg")
TEX_VENUS_ATMO   = _res("img/venus_athmosfere.jpg")
TEX_EARTH_DAY    = _res("img/earth.jpg")
TEX_EARTH_NIGHT  = _res("img/earth_night.jpg")
TEX_EARTH_CLOUDS = _res("img/earth_clouds.jpg")
TEX_MOON         = _res("img/moon.jpg")
TEX_MARS         = _res("img/mars.jpg")
TEX_JUPITER      = _res("img/jupiter.jpg")
TEX_SATURN       = _res("img/saturn.jpg")
TEX_SATURN_RING  = _res("img/saturn_ring.png")
TEX_URANUS       = _res("img/uranus.jpg")
TEX_NEPTUNE      = _res("img/neptune.jpg")
TEX_MILKY_WAY    = _res("img/milky_way.jpg")

# ---------------------------------------------------------------------------
#  Sphere detail (slices / stacks)
# ---------------------------------------------------------------------------
SPHERE_SLICES = +80
SPHERE_STACKS = +80

# ---------------------------------------------------------------------------
#  Body radii (NOT to scale -- chosen for aesthetics)
# ---------------------------------------------------------------------------
R_SUN     = +14.0
R_MERCURY = +1.5
R_VENUS   = +3.0
R_EARTH   = +3.2
R_MOON    = +0.9
R_MARS    = +2.2
R_JUPITER = +7.0
R_SATURN  = +6.0
R_URANUS  = +4.0
R_NEPTUNE = +3.8

# Saturn ring dimensions (inner/outer radius relative to Saturn centre)
SATURN_RING_INNER = +7.5
SATURN_RING_OUTER = +12.0

# ---------------------------------------------------------------------------
#  Orbital distances from the Sun (NOT to scale)
# ---------------------------------------------------------------------------
D_MERCURY = +30.0
D_VENUS   = +50.0
D_EARTH   = +72.0
D_MOON    = +6.5    # from Earth centre
D_MARS    = +95.0
D_JUPITER = +135.0
D_SATURN  = +175.0
D_URANUS  = +215.0
D_NEPTUNE = +250.0

# ---------------------------------------------------------------------------
#  Angular speeds -- orbital (radians / second)
#  Faster for inner planets, slower for outer (inspired by Kepler).
# ---------------------------------------------------------------------------
W_MERCURY_ORBIT = +2.0 * math.pi / +12.0
W_VENUS_ORBIT   = +2.0 * math.pi / +20.0
W_EARTH_ORBIT   = +2.0 * math.pi / +30.0
W_MOON_ORBIT    = +2.0 * math.pi / +5.0
W_MARS_ORBIT    = +2.0 * math.pi / +45.0
W_JUPITER_ORBIT = +2.0 * math.pi / +80.0
W_SATURN_ORBIT  = +2.0 * math.pi / +120.0
W_URANUS_ORBIT  = +2.0 * math.pi / +170.0
W_NEPTUNE_ORBIT = +2.0 * math.pi / +220.0

# ---------------------------------------------------------------------------
#  Angular speeds -- self-rotation (radians / second)
# ---------------------------------------------------------------------------
W_SUN_SPIN     = +2.0 * math.pi / +25.0
W_MERCURY_SPIN = +2.0 * math.pi / +20.0
W_VENUS_SPIN   = -2.0 * math.pi / +35.0   # Venus rotates retrograde!
W_EARTH_SPIN   = +2.0 * math.pi / +3.0
W_CLOUD_SPIN   = +2.0 * math.pi / +4.5    # clouds drift faster than surface
W_MARS_SPIN    = +2.0 * math.pi / +3.1
W_JUPITER_SPIN = +2.0 * math.pi / +1.5    # Jupiter spins fast
W_SATURN_SPIN  = +2.0 * math.pi / +1.7
W_URANUS_SPIN  = -2.0 * math.pi / +2.8    # Uranus also retrograde
W_NEPTUNE_SPIN = +2.0 * math.pi / +2.5

# ---------------------------------------------------------------------------
#  Axial tilts (radians)
# ---------------------------------------------------------------------------
TILT_EARTH   = +23.44 * math.pi / +180.0
TILT_MARS    = +25.19 * math.pi / +180.0
TILT_SATURN  = +26.73 * math.pi / +180.0
TILT_URANUS  = +97.77 * math.pi / +180.0  # Uranus is sideways!
TILT_NEPTUNE = +28.32 * math.pi / +180.0

# ---------------------------------------------------------------------------
#  Orbital inclinations to the ecliptic (radians)
#  Real astronomical values -- Earth is the reference plane at 0 deg.
# ---------------------------------------------------------------------------
INCL_MERCURY = +7.005 * math.pi / +180.0
INCL_VENUS   = +3.395 * math.pi / +180.0
INCL_EARTH   = +0.0
INCL_MARS    = +1.848 * math.pi / +180.0
INCL_JUPITER = +1.303 * math.pi / +180.0
INCL_SATURN  = +2.489 * math.pi / +180.0
INCL_URANUS  = +0.773 * math.pi / +180.0
INCL_NEPTUNE = +1.770 * math.pi / +180.0
INCL_MOON    = +5.145 * math.pi / +180.0   # to the ecliptic

# ---------------------------------------------------------------------------
#  Longitude of ascending node (radians, J2000 epoch)
#  Determines the direction in which each orbital plane is tilted.
# ---------------------------------------------------------------------------
NODE_MERCURY = +48.331  * math.pi / +180.0
NODE_VENUS   = +76.680  * math.pi / +180.0
NODE_EARTH   = +0.0
NODE_MARS    = +49.558  * math.pi / +180.0
NODE_JUPITER = +100.464 * math.pi / +180.0
NODE_SATURN  = +113.665 * math.pi / +180.0
NODE_URANUS  = +74.006  * math.pi / +180.0
NODE_NEPTUNE = +131.784 * math.pi / +180.0
NODE_MOON    = +125.08  * math.pi / +180.0  # mean value (precesses)

# ---------------------------------------------------------------------------
#  Starfield parameters
# ---------------------------------------------------------------------------
NUM_STARS              = +2500
STAR_SPHERE_RADIUS     = +2000.0
SKY_SPHERE_RADIUS      = +2500.0   # Milky Way backdrop (behind stars)
STAR_TWINKLE_SPEED_MIN = +0.5   # radians / second
STAR_TWINKLE_SPEED_MAX = +3.0
STAR_MIN_BRIGHTNESS    = +0.25
STAR_MAX_BRIGHTNESS    = +1.0

# ---------------------------------------------------------------------------
#  Camera defaults
# ---------------------------------------------------------------------------
CAM_DEFAULT_DIST  = -280.0
CAM_DEFAULT_YAW   = +0.0       # radians
CAM_DEFAULT_PITCH = +0.35      # radians (~20 deg down)
CAM_YAW_SPEED     = +2.0       # radians / second while key held
CAM_PITCH_SPEED   = +1.5
CAM_ZOOM_SPEED    = +80.0      # units / second
CAM_MIN_DIST      = -50.0
CAM_MAX_DIST      = -800.0

# ---------------------------------------------------------------------------
#  Orbit trail settings
# ---------------------------------------------------------------------------
ORBIT_SEGMENTS = +180
ORBIT_ALPHA    = +0.15

# ---------------------------------------------------------------------------
#  Runtime state -- angles (radians)
# ---------------------------------------------------------------------------
angle_sun_spin     = +0.0
angle_mercury_orb  = +0.0;  angle_mercury_spin = +0.0
angle_venus_orb    = +0.0;  angle_venus_spin   = +0.0
angle_earth_orb    = +0.0;  angle_earth_spin   = +0.0
angle_cloud_spin   = +0.0
angle_moon_orb     = +0.0
angle_mars_orb     = +0.0;  angle_mars_spin    = +0.0
angle_jupiter_orb  = +0.0;  angle_jupiter_spin = +0.0
angle_saturn_orb   = +0.0;  angle_saturn_spin  = +0.0
angle_uranus_orb   = +0.0;  angle_uranus_spin  = +0.0
angle_neptune_orb  = +0.0;  angle_neptune_spin = +0.0

last_time = None

# Camera state
cam_dist  = CAM_DEFAULT_DIST
cam_yaw   = CAM_DEFAULT_YAW
cam_pitch = CAM_DEFAULT_PITCH

# Key tracking for smooth camera (set of currently pressed special keys)
keys_held = set()

# Pause state
paused = False

# ---------------------------------------------------------------------------
#  Starfield data (filled in create_starfield)
# ---------------------------------------------------------------------------
star_positions  = []   # list of (x, y, z)
star_phases     = []   # random phase offset per star (radians)
star_speeds     = []   # twinkle frequency per star (radians/s)
star_base_sizes = []   # base GL point size per star

# ---------------------------------------------------------------------------
#  GL resource handles (populated after context creation)
# ---------------------------------------------------------------------------
dl_sun         = None
dl_mercury     = None
dl_venus       = None
dl_earth_day   = None
dl_earth_night = None
dl_earth_cloud = None
dl_moon        = None
dl_mars        = None
dl_jupiter     = None
dl_saturn      = None
dl_saturn_ring = None
dl_uranus      = None
dl_neptune     = None
dl_glow        = None   # plain sphere used for Sun corona glow
dl_milky_way   = None   # inverted skysphere for Milky Way backdrop


# ===================================================================
#  Texture loading
# ===================================================================

def load_texture(filepath, has_alpha=False, alpha_from_luminance=False):
    """Load an image from *filepath* and upload it as a GL_TEXTURE_2D.

    Parameters
    ----------
    filepath : str
        Path to the image file (JPEG, PNG, etc.).
    has_alpha : bool
        If True the image is loaded with an alpha channel (RGBA).
    alpha_from_luminance : bool
        If True the alpha channel is derived from the pixel brightness.
        White pixels become opaque, black pixels become transparent.
        Ideal for cloud maps stored as RGB JPEGs.

    Returns
    -------
    int
        The OpenGL texture name (id).
    """
    img = Image.open(filepath)

    if alpha_from_luminance:
        # Build RGBA where A = luminance of the pixel
        img_rgb = img.convert("RGB")
        lum = img.convert("L")           # grayscale = perceived brightness
        img = Image.merge("RGBA", (*img_rgb.split(), lum))
        raw = img.tobytes("raw", "RGBA", +0, -1)
        gl_fmt = GL_RGBA
    elif has_alpha:
        img = img.convert("RGBA")
        raw = img.tobytes("raw", "RGBA", +0, -1)
        gl_fmt = GL_RGBA
    else:
        # Pad to RGBX (4 bytes per pixel) for alignment
        img = img.convert("RGBX")
        raw = img.tobytes("raw", "RGBX", +0, -1)
        gl_fmt = GL_RGBA

    w, h = img.size
    tex_id = glGenTextures(+1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, +1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexImage2D(GL_TEXTURE_2D, +0, GL_RGBA, w, h, +0,
                 gl_fmt, GL_UNSIGNED_BYTE, raw)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    return tex_id


# ===================================================================
#  Sphere display-list builder
# ===================================================================

def build_sphere_list(filepath, radius, has_alpha=False,
                      alpha_from_luminance=False):
    """Create a display list that draws a textured sphere.

    The texture is loaded and bound inside the list so calling
    glCallList is sufficient to render the sphere.
    """
    dl = glGenLists(+1)
    q = gluNewQuadric()
    gluQuadricDrawStyle(q, GLU_FILL)
    gluQuadricNormals(q, GLU_SMOOTH)
    gluQuadricTexture(q, GL_TRUE)

    tex_id = load_texture(filepath, has_alpha=has_alpha,
                          alpha_from_luminance=alpha_from_luminance)

    glNewList(dl, GL_COMPILE)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    # gluSphere places its poles on the Z-axis.  Rotate -90 deg around X
    # so the poles align with Y (the "up" direction in our world) and
    # textures wrap horizontally around the equator as expected.
    glPushMatrix()
    glRotatef(-90.0, +1.0, +0.0, +0.0)
    gluSphere(q, radius, SPHERE_SLICES, SPHERE_STACKS)
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)
    glEndList()

    gluDeleteQuadric(q)
    return dl


# ===================================================================
#  Saturn ring display-list builder
# ===================================================================

def build_ring_list(filepath, inner, outer, segments=+120):
    """Create a display list for a flat textured ring (annulus) in the XZ plane.

    The ring is built as a GL_TRIANGLE_STRIP between *inner* and *outer*
    radii, with the texture mapped radially.
    """
    dl = glGenLists(+1)
    tex_id = load_texture(filepath, has_alpha=True)

    glNewList(dl, GL_COMPILE)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glBegin(GL_TRIANGLE_STRIP)
    for i in range(segments + +1):
        theta = +2.0 * math.pi * i / segments
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        # Texture: u maps around the ring, v maps inner->outer
        u = float(i) / float(segments)

        # Inner vertex
        glTexCoord2f(u, +0.0)
        glVertex3f(inner * cos_t, +0.0, inner * sin_t)

        # Outer vertex
        glTexCoord2f(u, +1.0)
        glVertex3f(outer * cos_t, +0.0, outer * sin_t)
    glEnd()

    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    glEndList()

    return dl


# ===================================================================
#  Sun corona glow sphere
# ===================================================================

def build_glow_list():
    """Create a display list for a plain (untextured) unit sphere.

    Used to render the Sun's corona glow by drawing this sphere at
    various scales with semi-transparent additive colour.
    """
    dl = glGenLists(+1)
    q = gluNewQuadric()
    gluQuadricDrawStyle(q, GLU_FILL)
    gluQuadricNormals(q, GLU_SMOOTH)
    gluQuadricTexture(q, GL_FALSE)

    glNewList(dl, GL_COMPILE)
    gluSphere(q, +1.0, +40, +40)
    glEndList()

    gluDeleteQuadric(q)
    return dl


# ===================================================================
#  Milky Way skysphere
# ===================================================================

def build_sky_sphere_list(filepath, radius):
    """Create a display list for a large inverted sphere textured with the
    Milky Way panorama.

    The sphere faces *inward* (normals reversed via gluQuadricOrientation)
    so the texture is visible from inside.  It is drawn without lighting
    to act as a static photographic backdrop behind everything else.
    """
    dl = glGenLists(+1)
    q = gluNewQuadric()
    gluQuadricDrawStyle(q, GLU_FILL)
    gluQuadricNormals(q, GLU_SMOOTH)
    gluQuadricTexture(q, GL_TRUE)
    gluQuadricOrientation(q, GLU_INSIDE)   # normals point inward

    tex_id = load_texture(filepath)

    glNewList(dl, GL_COMPILE)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glPushMatrix()
    glRotatef(-90.0, +1.0, +0.0, +0.0)    # poles on Y
    gluSphere(q, radius, +64, +64)
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)
    glEndList()

    gluDeleteQuadric(q)
    return dl


# ===================================================================
#  Starfield
# ===================================================================

def create_starfield():
    """Populate the starfield arrays with random positions on a large sphere
    and random twinkle parameters."""
    global star_positions, star_phases, star_speeds, star_base_sizes

    star_positions  = []
    star_phases     = []
    star_speeds     = []
    star_base_sizes = []

    for _ in range(NUM_STARS):
        # Uniform distribution on a sphere (Marsaglia method)
        while True:
            u = random.uniform(-1.0, +1.0)
            v = random.uniform(-1.0, +1.0)
            s = u * u + v * v
            if s < +1.0:
                break
        sq = +2.0 * math.sqrt(+1.0 - s)
        x = STAR_SPHERE_RADIUS * u * sq
        y = STAR_SPHERE_RADIUS * v * sq
        z = STAR_SPHERE_RADIUS * (+1.0 - +2.0 * s)
        star_positions.append((x, y, z))

        star_phases.append(random.uniform(+0.0, +2.0 * math.pi))
        star_speeds.append(random.uniform(STAR_TWINKLE_SPEED_MIN,
                                          STAR_TWINKLE_SPEED_MAX))
        star_base_sizes.append(random.uniform(+1.0, +2.5))


def draw_starfield(t):
    """Draw every star as a GL point with brightness oscillating over time.

    Stars are rendered in three size passes (small, medium, large) to
    create visual depth.  Each star has a subtle warm/cool colour tint.

    Parameters
    ----------
    t : float
        Current time in seconds (used for twinkle phase).
    """
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glEnable(GL_POINT_SMOOTH)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Three size buckets for visual depth: (min_base, max_base, point_size)
    buckets = [
        (+0.0, +1.5, +1.2),   # small dim stars
        (+1.5, +2.0, +2.2),   # medium stars
        (+2.0, +3.0, +3.5),   # large bright stars
    ]

    for lo, hi, pt_size in buckets:
        glPointSize(pt_size)
        glBegin(GL_POINTS)
        for i in range(NUM_STARS):
            bs = star_base_sizes[i]
            if bs < lo or bs >= hi:
                continue

            phase = star_speeds[i] * t + star_phases[i]
            brightness = STAR_MIN_BRIGHTNESS + (
                STAR_MAX_BRIGHTNESS - STAR_MIN_BRIGHTNESS
            ) * (+0.5 + +0.5 * math.sin(phase))

            warmth = bs / +2.5
            r = brightness * (+0.9 + +0.1 * warmth)
            g = brightness
            b = brightness * (+1.0 - +0.1 * warmth + +0.1)
            glColor3f(min(r, +1.0), min(g, +1.0), min(b, +1.0))

            x, y, z = star_positions[i]
            glVertex3f(x, y, z)
        glEnd()

    glDisable(GL_BLEND)
    glDisable(GL_POINT_SMOOTH)


# ===================================================================
#  Orbit trails
# ===================================================================

def draw_orbit_ring(radius, r, g, b, incl_rad=+0.0, node_rad=+0.0):
    """Draw a faint, anti-aliased orbit circle tilted to the correct plane.

    The ring is drawn in the XZ plane and then rotated by *node_rad*
    (ascending node) around Y followed by *incl_rad* (inclination)
    around X so it sits at the real orbital tilt.
    """
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glLineWidth(+1.2)

    glPushMatrix()
    # Tilt the drawing plane to match the real orbital inclination
    glRotatef(math.degrees(node_rad), +0.0, +1.0, +0.0)
    glRotatef(math.degrees(incl_rad), +1.0, +0.0, +0.0)

    glBegin(GL_LINE_LOOP)
    glColor4f(r, g, b, ORBIT_ALPHA)
    for i in range(ORBIT_SEGMENTS):
        theta = +2.0 * math.pi * i / ORBIT_SEGMENTS
        glVertex3f(radius * math.cos(theta), +0.0, radius * math.sin(theta))
    glEnd()

    glPopMatrix()

    glLineWidth(+1.0)
    glDisable(GL_LINE_SMOOTH)
    glDisable(GL_BLEND)


def draw_all_orbits():
    """Draw orbit paths for every planet around the Sun."""
    # (radius, r, g, b, inclination, ascending_node)
    orbits = [
        (D_MERCURY, +0.7, +0.7, +0.7, INCL_MERCURY, NODE_MERCURY),
        (D_VENUS,   +0.9, +0.7, +0.4, INCL_VENUS,   NODE_VENUS),
        (D_EARTH,   +0.3, +0.5, +0.9, INCL_EARTH,   NODE_EARTH),
        (D_MARS,    +0.9, +0.4, +0.3, INCL_MARS,     NODE_MARS),
        (D_JUPITER, +0.8, +0.7, +0.5, INCL_JUPITER,  NODE_JUPITER),
        (D_SATURN,  +0.8, +0.8, +0.5, INCL_SATURN,   NODE_SATURN),
        (D_URANUS,  +0.5, +0.8, +0.9, INCL_URANUS,   NODE_URANUS),
        (D_NEPTUNE, +0.3, +0.4, +0.9, INCL_NEPTUNE,  NODE_NEPTUNE),
    ]
    for dist, r, g, b, incl, node in orbits:
        draw_orbit_ring(dist, r, g, b, incl, node)


# ===================================================================
#  Lighting setup (Sun as point light)
# ===================================================================

def setup_lighting():
    """Configure a single point light at the origin (the Sun).

    GL_LIGHT0 emits white diffuse/specular light; a dim ambient term
    ensures the dark sides of planets are not completely black.
    """
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Light at the origin (Sun position in world space)
    glLightfv(GL_LIGHT0, GL_POSITION, [+0.0, +0.0, +0.0, +1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [+0.08, +0.08, +0.10, +1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [+1.0,  +0.98, +0.92, +1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [+1.0,  +1.0,  +1.0,  +1.0])

    # Attenuation so distant planets receive less light (subtle effect)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION,  +1.0)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION,    +0.0005)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, +0.000002)

    # Default material -- planets override as needed
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [+0.3, +0.3, +0.3, +1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, +25.0)


# ===================================================================
#  Helper: draw a generic planet
# ===================================================================

def draw_planet(orbit_angle, orbit_radius, spin_angle, tilt_rad,
                display_list, axial_tilt_axis=(+0.0, +0.0, +1.0),
                incl_rad=+0.0, node_rad=+0.0):
    """Draw a planet at its orbital position with axial tilt and spin.

    Parameters
    ----------
    orbit_angle : float   Orbital angle in radians.
    orbit_radius : float  Distance from the Sun.
    spin_angle : float    Self-rotation angle in radians.
    tilt_rad : float      Axial tilt in radians.
    display_list : int    GL display list for the textured sphere.
    axial_tilt_axis : tuple  Axis around which to apply axial tilt.
    incl_rad : float      Orbital inclination to the ecliptic (radians).
    node_rad : float      Longitude of ascending node (radians).
    """
    glPushMatrix()

    # 0) Tilt the orbital plane to its real inclination
    glRotatef(math.degrees(node_rad), +0.0, +1.0, +0.0)
    glRotatef(math.degrees(incl_rad), +1.0, +0.0, +0.0)

    # 1) Orbit: rotate frame around Y then translate outward
    glRotatef(math.degrees(orbit_angle), +0.0, +1.0, +0.0)
    glTranslatef(orbit_radius, +0.0, +0.0)

    # 2) Axial tilt
    if abs(tilt_rad) > +0.001:
        glRotatef(math.degrees(tilt_rad),
                  axial_tilt_axis[0], axial_tilt_axis[1], axial_tilt_axis[2])

    # 3) Self-rotation around the (now tilted) local Y axis
    glRotatef(math.degrees(spin_angle), +0.0, +1.0, +0.0)

    glColor3f(+1.0, +1.0, +1.0)  # neutral colour so texture is not tinted
    glCallList(display_list)

    glPopMatrix()


# ===================================================================
#  Earth special rendering (day + night + clouds)
# ===================================================================

def draw_earth():
    """Draw Earth with three layers:

    1. **Day texture** -- lit normally by GL_LIGHT0.
    2. **Night texture** -- blended on top with additive blending so city
       lights glow on the dark hemisphere (the lighting naturally dims the
       day texture on the dark side, letting the night layer show through).
    3. **Cloud layer** -- a slightly larger, semi-transparent sphere that
       rotates at a different speed, giving the illusion of weather.
    """
    glPushMatrix()

    # -- Tilt orbital plane to true inclination --------------------------
    glRotatef(math.degrees(NODE_EARTH), +0.0, +1.0, +0.0)
    glRotatef(math.degrees(INCL_EARTH), +1.0, +0.0, +0.0)

    # -- Move to Earth's orbital position --------------------------------
    glRotatef(math.degrees(angle_earth_orb), +0.0, +1.0, +0.0)
    glTranslatef(D_EARTH, +0.0, +0.0)

    # -- Save orbital position for the Moon later ------------------------
    glPushMatrix()

    # -- Axial tilt + spin -----------------------------------------------
    glRotatef(math.degrees(TILT_EARTH), +0.0, +0.0, +1.0)
    glRotatef(math.degrees(angle_earth_spin), +0.0, +1.0, +0.0)

    glColor3f(+1.0, +1.0, +1.0)

    # Layer 1: Day-side texture (standard lit rendering)
    glEnable(GL_LIGHTING)
    glCallList(dl_earth_day)

    # Layer 2: Night-side city lights (additive blend)
    # Where diffuse lighting is low (dark side), the additive
    # night texture "shows through"; where it is bright (day side)
    # the additive contribution is visually negligible.
    glEnable(GL_BLEND)
    glBlendFunc(GL_ONE, GL_ONE)  # additive
    glDisable(GL_LIGHTING)       # night lights are emissive
    glDepthFunc(GL_LEQUAL)       # draw on same depth as day sphere
    glCallList(dl_earth_night)
    glDepthFunc(GL_LESS)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

    glPopMatrix()  # back to orbital position (no tilt/spin)

    # Layer 3: Clouds -- slightly larger sphere, semi-transparent,
    # own rotation speed
    glPushMatrix()
    glRotatef(math.degrees(TILT_EARTH), +0.0, +0.0, +1.0)
    glRotatef(math.degrees(angle_cloud_spin), +0.0, +1.0, +0.0)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # Per-pixel alpha (from luminance) makes clouds opaque and clear sky
    # transparent.  Vertex alpha provides an overall softness multiplier.
    glColor4f(+1.0, +1.0, +1.0, +0.75)
    glDepthMask(GL_FALSE)                # don't write to depth buffer
    glCallList(dl_earth_cloud)
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)

    glPopMatrix()  # back to orbital position

    # -- Moon ------------------------------------------------------------
    draw_moon()

    glPopMatrix()  # back to world origin


def draw_moon():
    """Draw the Moon orbiting Earth with tidal locking.

    Called while the matrix is at Earth's orbital position (no tilt/spin).
    """
    glPushMatrix()

    # Tilt the Moon's orbital plane (inclined ~5.1 deg to the ecliptic)
    glRotatef(math.degrees(NODE_MOON), +0.0, +1.0, +0.0)
    glRotatef(math.degrees(INCL_MOON), +1.0, +0.0, +0.0)

    # Orbit around Earth (local Y)
    glRotatef(math.degrees(angle_moon_orb), +0.0, +1.0, +0.0)
    glTranslatef(D_MOON, +0.0, +0.0)

    # Tidal lock: cancel the orbital rotation on the body itself
    glRotatef(-math.degrees(angle_moon_orb), +0.0, +1.0, +0.0)

    glColor3f(+1.0, +1.0, +1.0)
    glCallList(dl_moon)

    glPopMatrix()


# ===================================================================
#  Saturn special rendering (planet + ring)
# ===================================================================

def draw_saturn():
    """Draw Saturn with its tilted ring system."""
    glPushMatrix()

    # Tilt the orbital plane to true inclination
    glRotatef(math.degrees(NODE_SATURN), +0.0, +1.0, +0.0)
    glRotatef(math.degrees(INCL_SATURN), +1.0, +0.0, +0.0)

    # Orbit
    glRotatef(math.degrees(angle_saturn_orb), +0.0, +1.0, +0.0)
    glTranslatef(D_SATURN, +0.0, +0.0)

    # Axial tilt
    glRotatef(math.degrees(TILT_SATURN), +0.0, +0.0, +1.0)

    # Self-spin
    glPushMatrix()
    glRotatef(math.degrees(angle_saturn_spin), +0.0, +1.0, +0.0)
    glColor3f(+1.0, +1.0, +1.0)
    glCallList(dl_saturn)
    glPopMatrix()

    # Ring (stays in the equatorial plane -- does not spin with the planet)
    glColor4f(+1.0, +1.0, +1.0, +0.85)
    glCallList(dl_saturn_ring)

    glPopMatrix()


# ===================================================================
#  OpenGL initialisation
# ===================================================================

def init_gl():
    """One-time GL state: background colour, depth test, projection."""
    glClearColor(+0.0, +0.0, +0.0, +0.0)  # black -- the void of space
    glClearDepth(+1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)

    glShadeModel(GL_SMOOTH)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    # Point size for starfield
    glPointSize(+1.8)
    glEnable(GL_POINT_SMOOTH)

    # Initial projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV_Y, WINDOW_W / float(WINDOW_H), NEAR_PLANE, FAR_PLANE)
    glMatrixMode(GL_MODELVIEW)


def reshape(w, h):
    """Adjust the viewport and projection when the window is resized."""
    if h == +0:
        h = +1
    glViewport(+0, +0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV_Y, w / float(h), NEAR_PLANE, FAR_PLANE)
    glMatrixMode(GL_MODELVIEW)


# ===================================================================
#  Animation update
# ===================================================================

def update_angles():
    """Advance every angle based on real elapsed time."""
    global last_time
    global angle_sun_spin
    global angle_mercury_orb, angle_mercury_spin
    global angle_venus_orb, angle_venus_spin
    global angle_earth_orb, angle_earth_spin, angle_cloud_spin
    global angle_moon_orb
    global angle_mars_orb, angle_mars_spin
    global angle_jupiter_orb, angle_jupiter_spin
    global angle_saturn_orb, angle_saturn_spin
    global angle_uranus_orb, angle_uranus_spin
    global angle_neptune_orb, angle_neptune_spin
    global cam_yaw, cam_pitch, cam_dist

    now = glutGet(GLUT_ELAPSED_TIME) / +1000.0  # seconds
    if last_time is None:
        last_time = now
    dt = now - last_time
    last_time = now

    # Camera always responds; planetary motion freezes when paused
    cam_dt = dt
    if paused:
        dt = +0.0

    TWO_PI = +2.0 * math.pi

    # Sun
    angle_sun_spin = (angle_sun_spin + W_SUN_SPIN * dt) % TWO_PI

    # Mercury
    angle_mercury_orb  = (angle_mercury_orb  + W_MERCURY_ORBIT * dt) % TWO_PI
    angle_mercury_spin = (angle_mercury_spin  + W_MERCURY_SPIN  * dt) % TWO_PI

    # Venus
    angle_venus_orb  = (angle_venus_orb  + W_VENUS_ORBIT * dt) % TWO_PI
    angle_venus_spin = (angle_venus_spin  + W_VENUS_SPIN  * dt) % TWO_PI

    # Earth + clouds
    angle_earth_orb  = (angle_earth_orb  + W_EARTH_ORBIT * dt) % TWO_PI
    angle_earth_spin = (angle_earth_spin  + W_EARTH_SPIN  * dt) % TWO_PI
    angle_cloud_spin = (angle_cloud_spin  + W_CLOUD_SPIN  * dt) % TWO_PI

    # Moon
    angle_moon_orb = (angle_moon_orb + W_MOON_ORBIT * dt) % TWO_PI

    # Mars
    angle_mars_orb  = (angle_mars_orb  + W_MARS_ORBIT * dt) % TWO_PI
    angle_mars_spin = (angle_mars_spin  + W_MARS_SPIN  * dt) % TWO_PI

    # Jupiter
    angle_jupiter_orb  = (angle_jupiter_orb  + W_JUPITER_ORBIT * dt) % TWO_PI
    angle_jupiter_spin = (angle_jupiter_spin  + W_JUPITER_SPIN  * dt) % TWO_PI

    # Saturn
    angle_saturn_orb  = (angle_saturn_orb  + W_SATURN_ORBIT * dt) % TWO_PI
    angle_saturn_spin = (angle_saturn_spin  + W_SATURN_SPIN  * dt) % TWO_PI

    # Uranus
    angle_uranus_orb  = (angle_uranus_orb  + W_URANUS_ORBIT * dt) % TWO_PI
    angle_uranus_spin = (angle_uranus_spin  + W_URANUS_SPIN  * dt) % TWO_PI

    # Neptune
    angle_neptune_orb  = (angle_neptune_orb  + W_NEPTUNE_ORBIT * dt) % TWO_PI
    angle_neptune_spin = (angle_neptune_spin  + W_NEPTUNE_SPIN  * dt) % TWO_PI

    # -- Smooth camera controls (always active, even when paused) --------
    if GLUT_KEY_LEFT in keys_held:
        cam_yaw -= CAM_YAW_SPEED * cam_dt
    if GLUT_KEY_RIGHT in keys_held:
        cam_yaw += CAM_YAW_SPEED * cam_dt
    if GLUT_KEY_UP in keys_held:
        cam_pitch = min(cam_pitch + CAM_PITCH_SPEED * cam_dt, math.pi / +2.0 - +0.05)
    if GLUT_KEY_DOWN in keys_held:
        cam_pitch = max(cam_pitch - CAM_PITCH_SPEED * cam_dt, -math.pi / +2.0 + +0.05)
    if ord('+') in keys_held or ord('=') in keys_held:
        cam_dist = min(cam_dist + CAM_ZOOM_SPEED * cam_dt, CAM_MIN_DIST)
    if ord('-') in keys_held:
        cam_dist = max(cam_dist - CAM_ZOOM_SPEED * cam_dt, CAM_MAX_DIST)


# ===================================================================
#  HUD text overlay
# ===================================================================

def draw_hud_text(text, x, y):
    """Draw *text* as a bitmap string at screen position (*x*, *y*) pixels.

    Uses an orthographic overlay so coordinates are in window pixels.
    (0, 0) is the bottom-left corner.
    """
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    vp = glGetIntegerv(GL_VIEWPORT)
    gluOrtho2D(+0, vp[2], +0, vp[3])
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)
    glColor3f(+1.0, +1.0, +1.0)

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(_FONT, ord(ch))

    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


# ===================================================================
#  Display callback
# ===================================================================

def display():
    """Main render loop: clear, set camera, draw everything, swap."""
    update_angles()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # -- Camera transform ------------------------------------------------
    glTranslatef(+0.0, +0.0, cam_dist)
    glRotatef(math.degrees(cam_pitch), +1.0, +0.0, +0.0)
    glRotatef(math.degrees(cam_yaw),   +0.0, +1.0, +0.0)

    # -- Milky Way backdrop (furthest layer, no lighting) ----------------
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)             # always behind everything
    glColor3f(+1.0, +1.0, +1.0)
    glCallList(dl_milky_way)
    glEnable(GL_DEPTH_TEST)

    # -- Starfield (twinkling points on top of the backdrop) --------------
    t = glutGet(GLUT_ELAPSED_TIME) / +1000.0
    draw_starfield(t)

    # -- Orbit trails (no lighting) --------------------------------------
    draw_all_orbits()

    # -- Lighting (Sun is at origin) -------------------------------------
    glEnable(GL_LIGHTING)
    setup_lighting()

    # -- Sun (emissive -- not affected by its own light) -----------------
    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_EMISSION, [+1.0, +0.95, +0.8, +1.0])
    glRotatef(math.degrees(angle_sun_spin), +0.0, +1.0, +0.0)
    glColor3f(+1.0, +1.0, +1.0)
    glCallList(dl_sun)
    glMaterialfv(GL_FRONT, GL_EMISSION, [+0.0, +0.0, +0.0, +1.0])  # reset
    glPopMatrix()

    # -- Sun glow / corona (additive semi-transparent layers) -----------
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # additive blending for glow
    glDepthMask(GL_FALSE)

    glow_layers = [
        (R_SUN * +1.12, +1.0,  +0.85, +0.4,  +0.12),
        (R_SUN * +1.28, +1.0,  +0.7,  +0.2,  +0.06),
        (R_SUN * +1.50, +0.9,  +0.5,  +0.15, +0.03),
    ]
    for scale, gr, gg, gb, ga in glow_layers:
        glPushMatrix()
        glScalef(scale, scale, scale)
        glColor4f(gr, gg, gb, ga)
        glCallList(dl_glow)
        glPopMatrix()

    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

    # -- Mercury ---------------------------------------------------------
    draw_planet(angle_mercury_orb, D_MERCURY, angle_mercury_spin,
                +0.0, dl_mercury,
                incl_rad=INCL_MERCURY, node_rad=NODE_MERCURY)

    # -- Venus -----------------------------------------------------------
    draw_planet(angle_venus_orb, D_VENUS, angle_venus_spin,
                +0.0, dl_venus,
                incl_rad=INCL_VENUS, node_rad=NODE_VENUS)

    # -- Earth (custom renderer for day/night/clouds/moon) ---------------
    draw_earth()

    # -- Mars ------------------------------------------------------------
    draw_planet(angle_mars_orb, D_MARS, angle_mars_spin,
                TILT_MARS, dl_mars,
                incl_rad=INCL_MARS, node_rad=NODE_MARS)

    # -- Jupiter ---------------------------------------------------------
    draw_planet(angle_jupiter_orb, D_JUPITER, angle_jupiter_spin,
                +0.0, dl_jupiter,
                incl_rad=INCL_JUPITER, node_rad=NODE_JUPITER)

    # -- Saturn (custom renderer for ring) -------------------------------
    draw_saturn()

    # -- Uranus (extreme axial tilt ~98 deg) ----------------------------
    draw_planet(angle_uranus_orb, D_URANUS, angle_uranus_spin,
                TILT_URANUS, dl_uranus,
                incl_rad=INCL_URANUS, node_rad=NODE_URANUS)

    # -- Neptune ---------------------------------------------------------
    draw_planet(angle_neptune_orb, D_NEPTUNE, angle_neptune_spin,
                TILT_NEPTUNE, dl_neptune,
                incl_rad=INCL_NEPTUNE, node_rad=NODE_NEPTUNE)

    glDisable(GL_LIGHTING)

    # -- HUD overlay (pause indicator) ----------------------------------
    if paused:
        draw_hud_text("|| PAUSED -- Press SPACE to resume", +10.0, +20.0)

    glutSwapBuffers()


# ===================================================================
#  Callbacks: keyboard + idle
# ===================================================================

def idle():
    """Request continuous redisplay for smooth animation."""
    glutPostRedisplay()


def special_key_down(key, _x, _y):
    """Track special key presses (arrow keys)."""
    keys_held.add(key)


def special_key_up(key, _x, _y):
    """Track special key releases."""
    keys_held.discard(key)


def normal_key_down(key, _x, _y):
    """Handle normal key presses: Space (pause), +, -, Esc."""
    global paused

    if key == b'\x1b':  # Escape
        try:
            glutLeaveMainLoop()
        except Exception:
            os._exit(+0)
        return
    elif key == b' ':
        paused = not paused
    elif key == b'+' or key == b'=':
        keys_held.add(ord('+'))
    elif key == b'-':
        keys_held.add(ord('-'))


def normal_key_up(key, _x, _y):
    """Track normal key releases."""
    global cam_dist, cam_yaw, cam_pitch

    if key == b'+' or key == b'=':
        keys_held.discard(ord('+'))
        keys_held.discard(ord('='))
    elif key == b'-':
        keys_held.discard(ord('-'))
    elif key == b'h' or key == b'H':
        # Home -- reset camera
        cam_dist  = CAM_DEFAULT_DIST
        cam_yaw   = CAM_DEFAULT_YAW
        cam_pitch = CAM_DEFAULT_PITCH


# ===================================================================
#  Main
# ===================================================================

def main():
    global dl_sun, dl_mercury, dl_venus
    global dl_earth_day, dl_earth_night, dl_earth_cloud, dl_moon
    global dl_mars, dl_jupiter, dl_saturn, dl_saturn_ring
    global dl_uranus, dl_neptune, dl_glow, dl_milky_way

    # -- GLUT setup ------------------------------------------------------
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowPosition(+50, +50)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"Solar System | Arrows=orbit  +/-=zoom  Space=pause  H=reset  Esc=quit")

    # Let glutLeaveMainLoop() return to caller instead of calling exit()
    try:
        glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE,
                      GLUT_ACTION_GLUTMAINLOOP_RETURNS)
    except Exception:
        pass  # not all GLUT builds support this option

    # -- GL state --------------------------------------------------------
    init_gl()

    # -- Build display lists for each body -------------------------------
    print("Loading textures...")
    dl_sun     = build_sphere_list(TEX_SUN,     R_SUN)
    dl_mercury = build_sphere_list(TEX_MERCURY, R_MERCURY)
    dl_venus   = build_sphere_list(TEX_VENUS,   R_VENUS)
    dl_earth_day   = build_sphere_list(TEX_EARTH_DAY,    R_EARTH)
    dl_earth_night = build_sphere_list(TEX_EARTH_NIGHT,  R_EARTH)
    dl_earth_cloud = build_sphere_list(TEX_EARTH_CLOUDS, R_EARTH * +1.015,
                                        alpha_from_luminance=True)
    dl_moon    = build_sphere_list(TEX_MOON,    R_MOON)
    dl_mars    = build_sphere_list(TEX_MARS,    R_MARS)
    dl_jupiter = build_sphere_list(TEX_JUPITER, R_JUPITER)
    dl_saturn  = build_sphere_list(TEX_SATURN,  R_SATURN)
    dl_saturn_ring = build_ring_list(TEX_SATURN_RING,
                                     SATURN_RING_INNER, SATURN_RING_OUTER)
    dl_glow      = build_glow_list()
    dl_milky_way = build_sky_sphere_list(TEX_MILKY_WAY, SKY_SPHERE_RADIUS)
    dl_uranus  = build_sphere_list(TEX_URANUS,  R_URANUS)
    dl_neptune = build_sphere_list(TEX_NEPTUNE, R_NEPTUNE)
    print("All textures loaded.")

    # -- Starfield -------------------------------------------------------
    create_starfield()

    # -- Register callbacks ----------------------------------------------
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutReshapeFunc(reshape)
    glutSpecialFunc(special_key_down)
    glutSpecialUpFunc(special_key_up)
    glutKeyboardFunc(normal_key_down)
    glutKeyboardUpFunc(normal_key_up)

    # -- Enter main loop -------------------------------------------------
    print("Controls: Arrows=orbit | +/-=zoom | Space=pause | H=reset | Esc=quit")
    glutMainLoop()


if __name__ == "__main__":
    main()
