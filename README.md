# OpenGL Python Graphics Seminar

A hands-on collection of progressive OpenGL examples written in Python with **PyOpenGL** and **GLUT**. Each exercise builds on the previous one, introducing new graphics-programming concepts -- from drawing a simple polygon to texturing 3D cubes with perspective projection.

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
|   \\-- 08_dual_orbit_cubes.py         # Two textured cubes orbiting in XY and XZ planes
|-- img/
|   \\-- box.jpg                        # Sample texture used by examples 04-08
|-- LICENSE                             # MIT License
\\-- README.md
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

# Run any example
python Examples/01_rotating_polygon.py
python Examples/08_dual_orbit_cubes.py
```

Examples 04-08 load a texture from `img/box.jpg`. Make sure you run them from the repository root so the relative path resolves correctly.

---

## License

This project is released under the [MIT License](LICENSE).
