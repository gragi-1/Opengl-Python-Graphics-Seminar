# OpenGL Python Graphics Seminar

A hands-on collection of progressive OpenGL examples written in Python with **PyOpenGL** and **GLUT**. Each exercise builds on the previous one, introducing new graphics-programming concepts -- from drawing a simple polygon to a full Sun-Earth-Moon simulation.

> **Convention** -- All internal angle calculations use **radians**. Degrees appear only where the OpenGL API requires them (`glRotatef`, `gluPerspective`).

---

## Repository structure

```
.
|-- Examples/
|   |-- 01_rotating_polygon.py          # Animated regular polygon (2D, radians)
|   |-- 02_square.py                    # Static coloured frame (GL_TRIANGLE_STRIP)
|   |-- 03_rotate.py                    # Rotating + scrolling square with seamless wrap
|   |-- 04_textured_quad.py             # Image texture on a 2D quad
|   |-- 05_textured_polygon.py          # Texture on an N-sided polygon + wrap modes
|   |-- 06_textured_perspective.py      # Textured square in 3D perspective (gluPerspective)
|   |-- 07_textured_planes_matrices.py  # Two planes: self-spin + orbit (push/pop matrix)
|   |-- 08_dual_orbit_cubes.py          # Two textured cubes orbiting in XY and XZ planes
|   \-- final_project.py               # Sun-Earth-Moon system simulation
|-- img/
|   |-- box.jpg                         # Sample texture (examples 04-08)
|   |-- sun.jpg                         # Sun texture (final project)
|   |-- mercury.jpg                     # Mercury texture
|   |-- venus.jpg                       # Venus texture
|   |-- venus_athmosfere.jpg            # Venus atmosphere texture
|   |-- earth.jpg                       # Earth day-side texture
|   |-- earth_night.jpg                 # Earth night-side city lights
|   |-- earth_clouds.jpg                # Earth cloud layer
|   |-- moon.jpg                        # Moon texture
|   |-- mars.jpg                        # Mars texture
|   |-- jupiter.jpg                     # Jupiter texture
|   |-- saturn.jpg                      # Saturn texture
|   |-- saturn_ring.png                 # Saturn ring (RGBA with alpha)
|   |-- uranus.jpg                      # Uranus texture
|   \-- neptune.jpg                     # Neptune texture
|-- LICENSE                             # MIT License
\-- README.md
```

---

## Topics covered

| # | File | Concepts |
|---|------|----------|
| 01 | `01_rotating_polygon.py` | GLUT basics, `gluOrtho2D`, polar coordinates, `time.perf_counter()` animation |
| 02 | `02_square.py` | NumPy vertex arrays, per-vertex colour, `GL_TRIANGLE_STRIP` |
| 03 | `03_rotate.py` | `glRotatef` (radians -> degrees), `glTranslatef`, seamless horizontal wrapping |
| 04 | `04_textured_quad.py` | PIL image loading, `glTexImage2D`, texture coordinates |
| 05 | `05_textured_polygon.py` | Polar texture mapping, `GL_REPEAT` vs `GL_CLAMP_TO_EDGE` |
| 06 | `06_textured_perspective.py` | `gluPerspective`, reshape callback, depth testing, double buffering |
| 07 | `07_textured_planes_matrices.py` | `glPushMatrix`/`glPopMatrix`, display lists, `glGetDoublev` (non-affine proof) |
| 08 | `08_dual_orbit_cubes.py` | 3D vertex arrays, orbital motion (sin/cos in radians), hierarchical transforms |

### Final project

| File | Concepts |
|------|----------|
| `final_project.py` | Complete Solar System (all 8 planets), twinkling starfield (2 500 stars), OpenGL lighting (point light at the Sun), Earth day/night cycle (additive city-lights blending) + cloud layer, Saturn textured ring, Venus/Uranus retrograde spin, axial tilts, tidal locking, interactive camera (arrow keys + zoom), display lists, alpha blending |

---

## Final project -- Enhanced Solar System

The final project brings together all concepts from the exercises into a rich, interactive 3D scene:

### Bodies

- **Sun** -- emissive textured sphere at the origin, acting as a GL point light.
- **Mercury, Venus, Mars, Jupiter, Uranus, Neptune** -- textured spheres with correct orbital ordering and Kepler-inspired speeds (inner planets orbit faster).
- **Earth** -- three-layer rendering:
  1. Day-side texture lit by the Sun (GL_LIGHT0).
  2. Night-side city-lights texture using **additive blending** so lights glow only on the dark hemisphere.
  3. Semi-transparent **cloud layer** rotating at a different speed than the surface.
- **Moon** -- orbits Earth with **tidal locking** (always shows the same face).
- **Saturn** -- textured sphere plus an alpha-blended **ring** built as a `GL_TRIANGLE_STRIP` annulus.
- **Venus** and **Uranus** spin **retrograde** (negative angular velocity).
- **Uranus** is tilted ~98 deg (nearly sideways), matching reality.

### Visual effects

- **2 500 twinkling stars** -- uniformly distributed on a large sphere with sinusoidal brightness oscillation and subtle warm/cool colour temperature variation.
- **Orbit trails** -- faint colour-coded circles in the XZ plane for every planet.
- **OpenGL lighting** -- point light at the Sun with attenuation; emissive material on the Sun itself; smooth-shaded diffuse/specular on all planets.

### Camera controls

| Key | Action |
|-----|--------|
| Left / Right arrows | Orbit horizontally |
| Up / Down arrows | Orbit vertically |
| + / - | Zoom in / out |
| H | Reset camera to default |
| Esc | Quit |

Sizes and distances are NOT to scale -- they are chosen for aesthetics. All angular velocities, radii, and orbital distances are configurable constants at the top of the file.

---

## Prerequisites

- **Python 3.8+**
- **PyOpenGL** -- Python bindings for OpenGL
- **Pillow (PIL)** -- image loading (used from example 04 onward)
- A system with OpenGL and GLUT support (FreeGLUT is recommended on Windows/Linux)

### Install dependencies

```bash
pip install pyopengl pillow
```

> On Windows you may also need the pre-built FreeGLUT DLLs. The easiest way is:
> ```bash
> pip install pyopengl pyopengl-accelerate
> ```

---

## Running the examples

```bash
# From the repository root
cd Opengl-Python-Graphics-Seminar

# Run any exercise
python Examples/01_rotating_polygon.py
python Examples/08_dual_orbit_cubes.py

# Run the final project
python Examples/final_project.py
```

Examples 04-08 load a texture from `img/box.jpg`. The final project loads 13 textures from `img/` (all planets, Earth night/clouds, Saturn ring, etc.). Make sure you run all scripts from the repository root so relative paths resolve correctly.

Once the final project window opens, use the **arrow keys** to orbit the camera, **+/-** to zoom, and **H** to reset the view.

---

## License

This project is released under the [MIT License](LICENSE).
