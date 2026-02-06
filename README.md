# OpenGL & Python -- Graphics Seminar

Eight progressive OpenGL exercises and a capstone **Solar System simulation**, all written from scratch in Python with PyOpenGL and FreeGLUT.  
The exercises start from a flat rotating polygon and end with textured cubes orbiting in 3D. The final project ties everything together into a real-time, interactive Solar System with per-pixel lighting, a photographic Milky Way backdrop, twinkling stars, multi-layer Earth rendering and **physically accurate orbital inclinations**.

> Every angle is stored internally in **radians**. Degrees only appear at the `glRotatef` / `gluPerspective` boundary.

---

## Quick start

```bash
# clone and enter the repo
git clone https://github.com/<your-user>/Opengl-Python-Graphics-Seminar.git
cd Opengl-Python-Graphics-Seminar

# install dependencies
pip install pyopengl pillow

# run any exercise
python Examples/01_rotating_polygon.py

# run the final project
python Examples/final_project.py
```

> **Windows note** -- If GLUT is missing, install the pre-built FreeGLUT wheel:
> ```bash
> pip install pyopengl pyopengl-accelerate
> ```

All scripts must be launched **from the repository root** so the `img/` texture paths resolve correctly.

---

## Building a standalone `.exe` (Windows)

You can package the final project into a self-contained executable that runs on machines without Python installed.

### Prerequisites

```bash
pip install pyinstaller
```

### Build command

```bash
pyinstaller --noconfirm --onedir --windowed ^
    --name "SolarSystem" ^
    --add-data "img;img" ^
    --collect-all OpenGL ^
    Examples/final_project.py
```

| Flag | Why |
|------|-----|
| `--onedir` | Keeps all runtime files in a single folder (faster startup than `--onefile`). |
| `--windowed` | Suppresses the console window on launch. |
| `--add-data "img;img"` | Bundles the texture folder inside the distribution. |
| `--collect-all OpenGL` | Ensures every dynamically-loaded OpenGL sub-module is included. |

After the build finishes the executable and its support files live in:

```
dist/
  SolarSystem/
    SolarSystem.exe      <-- double-click to run
    _internal/
      img/               <-- bundled textures
      ...                <-- Python runtime, DLLs, etc.
```

Copy the entire `SolarSystem/` folder to any Windows machine and run `SolarSystem.exe`. No Python installation required.

> `build/`, `dist/` and `*.spec` are already in `.gitignore` and will not be committed.

---

## Repository layout

```
.
+-- Examples/
|   +-- 01_rotating_polygon.py
|   +-- 02_square.py
|   +-- 03_rotate.py
|   +-- 04_textured_quad.py
|   +-- 05_textured_polygon.py
|   +-- 06_textured_perspective.py
|   +-- 07_textured_planes_matrices.py
|   +-- 08_dual_orbit_cubes.py
|   +-- final_project.py
+-- img/
|   +-- box.jpg                  # shared texture (exercises 04-08)
|   +-- milky_way.jpg            # Milky Way panorama (skysphere backdrop)
|   +-- sun.jpg
|   +-- mercury.jpg
|   +-- venus.jpg
|   +-- venus_athmosfere.jpg
|   +-- earth.jpg
|   +-- earth_night.jpg          # city lights (night hemisphere)
|   +-- earth_clouds.jpg         # cloud layer (alpha from luminance)
|   +-- moon.jpg
|   +-- mars.jpg
|   +-- jupiter.jpg
|   +-- saturn.jpg
|   +-- saturn_ring.png          # ring texture with alpha channel
|   +-- uranus.jpg
|   +-- neptune.jpg
+-- LICENSE
+-- README.md
```

---

## Exercise breakdown

| # | Script | Topics |
|---|--------|--------|
| 01 | `01_rotating_polygon.py` | GLUT window, `gluOrtho2D`, polar vertex generation, `time.perf_counter()` loop |
| 02 | `02_square.py` | NumPy vertex arrays, per-vertex colour, `GL_TRIANGLE_STRIP` |
| 03 | `03_rotate.py` | `glRotatef` (radians to degrees), `glTranslatef`, seamless horizontal wrapping |
| 04 | `04_textured_quad.py` | PIL image loading, `glTexImage2D`, UV coordinates |
| 05 | `05_textured_polygon.py` | Polar UV mapping, `GL_REPEAT` vs `GL_CLAMP_TO_EDGE` |
| 06 | `06_textured_perspective.py` | `gluPerspective`, reshape callback, depth testing, double buffering |
| 07 | `07_textured_planes_matrices.py` | `glPushMatrix` / `glPopMatrix`, display lists, matrix hierarchy |
| 08 | `08_dual_orbit_cubes.py` | 3D vertex arrays, orbital motion (sin/cos), hierarchical transforms |

---

## Final project -- Solar System simulation

The capstone pulls together transforms, texturing, lighting and blending into a single interactive scene.

### What is rendered

| Body / Element | Details |
|----------------|---------|
| **Milky Way** | A photographic panorama (`milky_way.jpg`) mapped onto a large inverted skysphere. Drawn without lighting and behind all geometry to serve as a realistic galactic backdrop. |
| **Starfield** | 2 500 procedural stars layered on top of the Milky Way. Placed with the Marsaglia uniform-sphere method, three point-size buckets and sinusoidal brightness give a twinkling, layered depth effect. |
| **Sun** | Emissive textured sphere at the origin + three-layer additive corona glow. Acts as the scene's point light (`GL_LIGHT0` with attenuation). |
| **Mercury -- Neptune** | Textured spheres with Kepler-inspired orbital speeds (inner planets faster). Venus and Uranus spin retrograde. Uranus is tilted ~98 degrees. |
| **Earth** | Three-pass rendering: (1) day texture lit by the Sun, (2) night city-lights via **additive blending** so they only glow on the dark hemisphere, (3) cloud layer with **alpha derived from luminance** rotating independently of the surface. |
| **Moon** | Orbits Earth with tidal locking (same face always visible). Orbit inclined ~5.1 degrees to the ecliptic. |
| **Saturn** | Planet body + alpha-blended ring built as a `GL_TRIANGLE_STRIP` annulus, tilted 26.7 degrees. |
| **Orbits** | Anti-aliased, colour-coded rings tilted to each planet's **real orbital inclination** and ascending node (J2000 epoch). |

### Orbital inclinations

Each planet's orbit is tilted to its real astronomical inclination relative to the ecliptic plane (Earth's orbital plane, used as the 0-degree reference). The longitude of ascending node sets the *direction* of the tilt.

| Body | Inclination | Ascending node |
|------|-------------|----------------|
| Mercury | 7.005 deg | 48.3 deg |
| Venus | 3.395 deg | 76.7 deg |
| Earth | 0.000 deg | -- |
| Mars | 1.848 deg | 49.6 deg |
| Jupiter | 1.303 deg | 100.5 deg |
| Saturn | 2.489 deg | 113.7 deg |
| Uranus | 0.773 deg | 74.0 deg |
| Neptune | 1.770 deg | 131.8 deg |
| Moon | 5.145 deg | 125.1 deg |

Mercury's 7-degree tilt is clearly visible; outer planets show subtler but physically accurate offsets.

### Controls

| Key | Action |
|-----|--------|
| Left / Right | Orbit the camera horizontally |
| Up / Down | Orbit the camera vertically |
| `+` / `-` | Zoom in / out |
| Space | Pause / resume the simulation |
| H | Reset camera to default position |
| Esc | Quit |

All sizes, distances and speeds are **not to scale** -- they are tuned for readability. Every constant is defined at the top of `final_project.py` and is easy to tweak.

### Implementation highlights

- **Milky Way skysphere** -- `milky_way.jpg` is mapped onto a large inverted `gluSphere` (normals facing inward via `gluQuadricOrientation(GLU_INSIDE)`). Drawn with depth testing disabled so it always sits behind every other object.
- **Realistic orbital planes** -- Each planet's orbit ring and motion path are tilted by its real inclination to the ecliptic with the correct ascending-node direction (J2000 data). The Moon's orbit is also inclined ~5.1 degrees.
- **Time-based animation** -- `glutGet(GLUT_ELAPSED_TIME)` drives all motion so frame-rate drops do not affect speed.
- **Display lists** -- Each textured body is pre-compiled into a GL display list for fast rendering.
- **gluSphere pole fix** -- `gluSphere` puts poles on Z; every sphere is rotated -90 degrees around X inside its display list so poles align with Y and equatorial bands wrap correctly.
- **Cloud alpha from luminance** -- `earth_clouds.jpg` is a standard RGB JPEG. At load time the brightness of each pixel is used as its alpha channel, making white clouds opaque and black sky transparent, without needing a pre-authored RGBA file.
- **Pause / resume** -- Planetary `dt` is set to zero while paused; the camera keeps responding with its own `cam_dt`.
- **PyInstaller-ready** -- Resource paths go through `_res()`, which resolves from `sys._MEIPASS` when frozen or from the repo root when running from source.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Python | >= 3.8 | Runtime |
| PyOpenGL | any | OpenGL / GLU / GLUT bindings |
| Pillow | any | Image loading (JPEG, PNG) |
| PyInstaller | any | *(optional)* Building the standalone `.exe` |

FreeGLUT must be available on the system. On Windows it ships with `pyopengl` or can be installed via `pyopengl-accelerate`.

---

## License

Released under the [MIT License](LICENSE).
