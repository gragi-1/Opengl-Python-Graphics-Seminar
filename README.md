<p align="center">
  <strong>OpenGL &amp; Python — Graphics Seminar</strong><br>
  <em>Eight progressive OpenGL exercises and a capstone Solar System simulation</em>
</p>

<p align="center">
  <img alt="Python 3.8+" src="https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white">
  <img alt="OpenGL" src="https://img.shields.io/badge/OpenGL-Fixed%20Pipeline-5586A4?logo=opengl&logoColor=white">
  <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-green.svg">
  <img alt="Platform" src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey">
</p>

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Exercise Catalogue](#exercise-catalogue)
7. [Final Project — Solar System Simulation](#final-project--solar-system-simulation)
   - [Rendered Bodies & Effects](#rendered-bodies--effects)
   - [Physically Accurate Orbital Mechanics](#physically-accurate-orbital-mechanics)
   - [Multi-layer Earth Rendering](#multi-layer-earth-rendering)
   - [Saturn Ring System](#saturn-ring-system)
   - [Starfield & Milky Way Backdrop](#starfield--milky-way-backdrop)
   - [Controls](#controls)
   - [Implementation Highlights](#implementation-highlights)
   - [Configuration Reference](#configuration-reference)
8. [Building a Standalone Executable](#building-a-standalone-executable)
9. [Repository Layout](#repository-layout)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)
12. [License](#license)

---

## Overview

This repository contains a complete, from-scratch graphics programming curriculum built with **Python**, **PyOpenGL**, and **FreeGLUT**. It is structured as eight incremental exercises that progressively introduce core OpenGL concepts — from flat 2-D polygon rendering to textured 3-D transforms — culminating in a real-time, interactive **Solar System simulation** that ties every technique together.

All internal angles are stored in **radians**. Degrees appear exclusively at the OpenGL API boundary (`glRotatef`, `gluPerspective`).

---

## Features

- **Progressive learning path** — 8 exercises building from 2-D primitives to full 3-D textured scenes.
- **Complete Solar System** — All 8 planets (Mercury–Neptune), the Moon, the Sun, Saturn's ring, and a starfield.
- **Physically accurate orbital planes** — Inclinations and ascending nodes sourced from J2000 epoch data.
- **Multi-layer Earth** — Day texture, additive night city-lights, and an independent cloud layer with luminance-derived alpha.
- **Saturn ring with Keplerian rotation** — The ring rotates at its own mean Keplerian angular velocity, independent of the planet's surface spin.
- **Milky Way panoramic backdrop** — A photographic equirectangular panorama mapped onto an inverted skysphere.
- **Twinkling starfield** — 2 500 procedural stars with sinusoidal brightness oscillation and warm/cool colour tints.
- **Point-light shading** — `GL_LIGHT0` at the Sun with attenuation for physical day/night illumination.
- **Sun corona glow** — Three-layer additive semi-transparent shells.
- **Time-based animation** — `glutGet(GLUT_ELAPSED_TIME)` drives all motion; frame-rate drops do not affect simulation speed.
- **Interactive camera** — Smooth orbital camera with arrow-key control, zoom, pause, and home reset.
- **PyInstaller-ready** — Resource paths resolve via `sys._MEIPASS` when frozen into a standalone `.exe`.

---

## Requirements

| Dependency      | Version   | Purpose                                   |
|-----------------|-----------|-------------------------------------------|
| **Python**      | ≥ 3.8     | Runtime interpreter                       |
| **PyOpenGL**    | any       | OpenGL / GLU / GLUT bindings              |
| **Pillow**      | any       | Image loading (JPEG, PNG)                 |
| **FreeGLUT**    | any       | Windowing & input (ships with PyOpenGL on Windows) |
| **PyInstaller** | any       | *(optional)* Building the standalone `.exe` |

> **Note:** On Linux, FreeGLUT is typically available as a system package (`freeglut3-dev` on Debian/Ubuntu, `freeglut-devel` on Fedora). On macOS, GLUT is provided by the system frameworks.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/gragi-1/Opengl-Python-Graphics-Seminar.git
cd Opengl-Python-Graphics-Seminar
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (CMD)
.\.venv\Scripts\activate.bat

# Linux / macOS
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install pyopengl pillow
```

<details>
<summary><strong>Windows — If GLUT is not found at runtime</strong></summary>

Install the pre-built FreeGLUT wheel:

```bash
pip install pyopengl pyopengl-accelerate
```

If that does not resolve the issue, download `freeglut.dll` from [the FreeGLUT project](https://freeglut.sourceforge.net/) and place it in the same directory as your Python executable or on your `PATH`.

</details>

<details>
<summary><strong>Linux — Install FreeGLUT system package</strong></summary>

```bash
# Debian / Ubuntu
sudo apt-get install freeglut3-dev

# Fedora
sudo dnf install freeglut-devel

# Arch
sudo pacman -S freeglut
```

</details>

---

## Usage

> **Important:** All scripts must be launched **from the repository root** so the `img/` texture paths resolve correctly.

### Run any exercise

```bash
python Examples/01_rotating_polygon.py
python Examples/02_square.py
# ... etc.
```

### Run the final Solar System simulation

```bash
python Examples/final_project.py
```

The window opens at **1 400 × 850 px** by default. Resize freely — the projection adapts automatically.

---

## Exercise Catalogue

Each exercise introduces one or two new OpenGL concepts while reinforcing prior ones.

| #  | Script                             | Key Concepts                                                                        |
|----|------------------------------------|-------------------------------------------------------------------------------------|
| 01 | `01_rotating_polygon.py`           | GLUT window lifecycle, `gluOrtho2D`, polar vertex generation, time-based idle loop  |
| 02 | `02_square.py`                     | NumPy vertex arrays, per-vertex colour, `GL_TRIANGLE_STRIP`                         |
| 03 | `03_rotate.py`                     | `glRotatef` (radians → degrees), `glTranslatef`, seamless horizontal wrapping       |
| 04 | `04_textured_quad.py`              | PIL image loading, `glTexImage2D`, UV coordinates, `GL_QUADS`                       |
| 05 | `05_textured_polygon.py`           | Polar UV mapping, `GL_REPEAT` vs `GL_CLAMP_TO_EDGE`, texture coordinate scaling     |
| 06 | `06_textured_perspective.py`       | `gluPerspective`, reshape callback, depth testing, double buffering                 |
| 07 | `07_textured_planes_matrices.py`   | `glPushMatrix` / `glPopMatrix`, display lists, matrix hierarchy                     |
| 08 | `08_dual_orbit_cubes.py`           | 3-D vertex arrays, orbital motion (sin / cos), hierarchical transforms              |

---

## Final Project — Solar System Simulation

The capstone integrates transforms, texturing, lighting, blending, and display lists into a single interactive scene rendered at 60 + FPS.

### Rendered Bodies & Effects

| Body / Element   | Details                                                                                                      |
|------------------|--------------------------------------------------------------------------------------------------------------|
| **Milky Way**    | Equirectangular panorama (`milky_way.jpg`) mapped onto a large inverted `gluSphere`. Drawn with depth testing disabled so it always sits behind all scene geometry. |
| **Starfield**    | 2 500 procedural stars generated with the Marsaglia uniform-sphere method. Three point-size buckets, sinusoidal brightness oscillation, and warm/cool colour tints create a layered twinkling effect. |
| **Sun**          | Emissive textured sphere at the origin plus a three-layer additive corona glow. Serves as the scene's `GL_LIGHT0` point light with constant + linear + quadratic attenuation. |
| **Mercury–Mars** | Textured spheres with Kepler-inspired orbital speeds (inner planets faster). Venus spins retrograde.          |
| **Earth**        | Three-pass rendering: (1) day texture lit by the Sun, (2) additive night city-lights, (3) independent cloud sphere with luminance-derived alpha. See [Multi-layer Earth Rendering](#multi-layer-earth-rendering). |
| **Moon**         | Orbits Earth with tidal locking. Inclination of 5.145° to the ecliptic with ascending node at 125.08°.       |
| **Jupiter**      | Largest sphere; fast self-rotation.                                                                           |
| **Saturn**       | Planet body + alpha-blended ring annulus rotating at a mean Keplerian rate. See [Saturn Ring System](#saturn-ring-system). |
| **Uranus**       | Extreme axial tilt (~97.8°); retrograde spin.                                                                 |
| **Neptune**      | Axial tilt of ~28.3°; outermost orbit.                                                                        |
| **Orbit trails** | Anti-aliased, colour-coded `GL_LINE_LOOP` circles tilted to each planet's real inclination and ascending node. |

### Physically Accurate Orbital Mechanics

Every planet's orbital plane is tilted to its **real astronomical inclination** relative to the ecliptic (Earth's orbital plane = 0°). The **longitude of ascending node** (J2000 epoch) determines the direction of each tilt.

| Body    | Inclination (°) | Ascending Node (°) | Visible Effect                                     |
|---------|-----------------|---------------------|----------------------------------------------------|
| Mercury | 7.005           | 48.331              | Clearly visible tilt — the most inclined inner planet |
| Venus   | 3.395           | 76.680              | Moderate tilt                                       |
| Earth   | 0.000           | —                   | Reference plane (ecliptic)                          |
| Mars    | 1.848           | 49.558              | Subtle tilt                                         |
| Jupiter | 1.303           | 100.464             | Slight offset                                       |
| Saturn  | 2.489           | 113.665             | Moderate tilt                                       |
| Uranus  | 0.773           | 74.006              | Nearly ecliptic                                     |
| Neptune | 1.770           | 131.784             | Subtle tilt                                         |
| Moon    | 5.145           | 125.080             | Inclined relative to Earth's orbit                  |

### Multi-layer Earth Rendering

Earth is rendered in three separate passes within a single frame:

1. **Day texture** — Standard lit rendering with `GL_LIGHT0`. The Sun illuminates the day hemisphere; the far side goes dark naturally.
2. **Night city-lights** — Rendered with **additive blending** (`GL_ONE, GL_ONE`). On the dark hemisphere the day texture contribution is near zero, so the additive city-lights layer glows through. On the lit side the additive contribution is negligible against the bright day texture.
3. **Cloud layer** — A slightly larger sphere (1.015× Earth radius) textured with `earth_clouds.jpg`. At load time each pixel's brightness is used as its alpha channel (white → opaque cloud, black → transparent sky). The cloud sphere rotates at a different angular velocity than the surface, creating the illusion of moving weather systems.

### Saturn Ring System

Saturn's ring is modelled as a flat `GL_TRIANGLE_STRIP` annulus in the XZ plane, textured with `saturn_ring.png` (RGBA with alpha for transparency). The ring sits in Saturn's equatorial plane (tilted 26.73° from the orbital plane) and **rotates at its own mean Keplerian angular velocity**, independent of the planet's surface spin. This reflects the physical reality that ring particles orbit Saturn at different speeds (inner particles faster, outer particles slower); the simulation uses a single intermediate rate as a visual approximation.

### Starfield & Milky Way Backdrop

The background is composed of two layers:

1. **Milky Way skysphere** — A large inverted `gluSphere` with normals facing inward (`gluQuadricOrientation(GLU_INSIDE)`) textured with a photographic panorama. Drawn first with depth testing disabled.
2. **Starfield** — 2 500 points distributed uniformly on a sphere using the Marsaglia method. Each star has a random phase, twinkle frequency, and base size. Stars are drawn in three size buckets with `GL_POINT_SMOOTH` for anti-aliasing. Brightness oscillates sinusoidally over time.

### Controls

| Key             | Action                          |
|-----------------|---------------------------------|
| `←` / `→`      | Orbit camera horizontally       |
| `↑` / `↓`      | Orbit camera vertically         |
| `+` / `-`      | Zoom in / out                   |
| `Space`         | Pause / resume simulation       |
| `H`             | Reset camera to default view    |
| `Esc`           | Quit                            |

Camera movement is always responsive, even while the simulation is paused.

### Implementation Highlights

| Technique                      | Description                                                                                              |
|--------------------------------|----------------------------------------------------------------------------------------------------------|
| **Display lists**              | Each textured body is pre-compiled into a `glGenLists` / `glNewList` / `glEndList` block for fast per-frame rendering. |
| **Time-based animation**       | `glutGet(GLUT_ELAPSED_TIME)` provides a high-resolution clock. All angular velocities are in rad/s and multiplied by `dt`. |
| **gluSphere pole alignment**   | `gluSphere` places its poles on Z. Each sphere display list includes a −90° rotation around X so poles align with the Y axis and equatorial texture bands wrap correctly. |
| **Cloud alpha from luminance** | `earth_clouds.jpg` is a standard RGB JPEG. At load time the L (luminance) channel is extracted and merged as the alpha channel, avoiding the need for a pre-authored RGBA file. |
| **Orbit plane tilting**        | Two sequential rotations — ascending node around Y, then inclination around X — correctly orient each orbital plane in 3-D space. |
| **Smooth camera**              | Key-down / key-up callbacks populate a `keys_held` set. Each frame, held keys apply their angular or zoom velocity multiplied by the frame delta. |
| **Pause mechanism**            | Planetary `dt` is zeroed; the camera continues to use its own `cam_dt`, keeping the view interactive while the Solar System is frozen. |
| **PyInstaller compatibility**  | All resource paths go through `_res()`, which resolves from `sys._MEIPASS` when frozen or from the repo root when running from source. |

### Configuration Reference

All simulation constants are defined at the top of [Examples/final_project.py](Examples/final_project.py) and are easy to adjust.

<details>
<summary><strong>Body radii</strong></summary>

| Constant    | Value | Unit   |
|-------------|-------|--------|
| `R_SUN`     | 14.0  | GL units |
| `R_MERCURY` | 1.5   | GL units |
| `R_VENUS`   | 3.0   | GL units |
| `R_EARTH`   | 3.2   | GL units |
| `R_MOON`    | 0.9   | GL units |
| `R_MARS`    | 2.2   | GL units |
| `R_JUPITER` | 7.0   | GL units |
| `R_SATURN`  | 6.0   | GL units |
| `R_URANUS`  | 4.0   | GL units |
| `R_NEPTUNE` | 3.8   | GL units |

</details>

<details>
<summary><strong>Orbital distances</strong></summary>

| Constant    | Value | Unit   |
|-------------|-------|--------|
| `D_MERCURY` | 30.0  | GL units |
| `D_VENUS`   | 50.0  | GL units |
| `D_EARTH`   | 72.0  | GL units |
| `D_MOON`    | 6.5   | GL units (from Earth) |
| `D_MARS`    | 95.0  | GL units |
| `D_JUPITER` | 135.0 | GL units |
| `D_SATURN`  | 175.0 | GL units |
| `D_URANUS`  | 215.0 | GL units |
| `D_NEPTUNE` | 250.0 | GL units |

</details>

<details>
<summary><strong>Angular velocities (orbital & spin)</strong></summary>

All values in rad/s. Defined as `2π / period` where *period* is in seconds.

| Body    | Orbital period (s) | Spin period (s) | Notes                            |
|---------|---------------------|-----------------|----------------------------------|
| Sun     | —                   | 25.0            |                                  |
| Mercury | 12.0                | 20.0            |                                  |
| Venus   | 20.0                | −35.0           | Negative = retrograde            |
| Earth   | 30.0                | 3.0             | Clouds: 4.5 s                    |
| Moon    | 5.0                 | tidally locked  |                                  |
| Mars    | 45.0                | 3.1             |                                  |
| Jupiter | 80.0                | 1.5             |                                  |
| Saturn  | 120.0               | 1.7             | Ring: 2.2 s (mean Keplerian)     |
| Uranus  | 170.0               | −2.8            | Negative = retrograde            |
| Neptune | 220.0               | 2.5             |                                  |

</details>

> Sizes, distances, and speeds are **not to scale** — they are tuned for readability and visual appeal. Every constant can be modified in one place at the top of the source file.

---

## Building a Standalone Executable

The final project can be packaged into a self-contained Windows `.exe` with **PyInstaller**. No Python installation is required on the target machine.

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

| Flag                    | Purpose                                                             |
|-------------------------|---------------------------------------------------------------------|
| `--onedir`              | Single folder distribution (faster startup than `--onefile`)        |
| `--windowed`            | Suppresses the console window on launch                             |
| `--add-data "img;img"`  | Bundles the `img/` texture folder inside the distribution           |
| `--collect-all OpenGL`  | Ensures every dynamically-loaded OpenGL sub-module is included      |

### Output structure

```
dist/
  SolarSystem/
    SolarSystem.exe          ← double-click to run
    _internal/
      img/                   ← bundled textures
      ...                    ← Python runtime, DLLs, etc.
```

Copy the entire `SolarSystem/` folder to any Windows machine and run `SolarSystem.exe`.

> **Note:** `build/`, `dist/`, and `*.spec` are listed in `.gitignore` and will not be committed.

---

## Repository Layout

```
Opengl-Python-Graphics-Seminar/
├── Examples/
│   ├── 01_rotating_polygon.py          # 2-D polygon, polar vertices, idle animation
│   ├── 02_square.py                    # NumPy arrays, per-vertex colour, triangle strip
│   ├── 03_rotate.py                    # Rotation, translation, seamless wrapping
│   ├── 04_textured_quad.py             # Texture loading, UV mapping, GL_QUADS
│   ├── 05_textured_polygon.py          # Polar UV mapping, wrap modes
│   ├── 06_textured_perspective.py      # gluPerspective, depth test, double buffer
│   ├── 07_textured_planes_matrices.py  # Matrix hierarchy, display lists
│   ├── 08_dual_orbit_cubes.py          # 3-D cubes, dual orbits, hierarchical transforms
│   └── final_project.py                # ★ Solar System simulation (capstone)
├── img/
│   ├── box.jpg                         # Shared texture (exercises 04–08)
│   ├── milky_way.jpg                   # Milky Way panorama (skysphere backdrop)
│   ├── sun.jpg
│   ├── mercury.jpg
│   ├── venus.jpg
│   ├── venus_athmosfere.jpg            # Venus atmosphere overlay
│   ├── earth.jpg                       # Day-side texture
│   ├── earth_night.jpg                 # City lights (night hemisphere)
│   ├── earth_clouds.jpg                # Cloud layer (alpha from luminance)
│   ├── moon.jpg
│   ├── mars.jpg
│   ├── jupiter.jpg
│   ├── saturn.jpg
│   ├── saturn_ring.png                 # Ring texture (RGBA with alpha)
│   ├── uranus.jpg
│   └── neptune.jpg
├── build/                              # PyInstaller build artefacts (git-ignored)
├── SolarSystem.spec                    # PyInstaller spec file
├── LICENSE                             # MIT License
└── README.md                           # This file
```

---

## Troubleshooting

| Problem                                                   | Solution                                                                                                            |
|-----------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| **`ImportError: No module named OpenGL`**                 | Run `pip install pyopengl pillow`.                                                                                  |
| **`OpenGL.error.NullFunctionError` / GLUT not found**    | Install FreeGLUT. On Windows: `pip install pyopengl-accelerate` or place `freeglut.dll` on your `PATH`.             |
| **Textures not loading / blank spheres**                  | Make sure you launch from the **repository root** (`cd Opengl-Python-Graphics-Seminar`) so `img/` is found.         |
| **Black window with no rendering**                        | Your GPU may not support the fixed-function pipeline. Try updating your graphics drivers.                           |
| **Very low FPS**                                          | Reduce `SPHERE_SLICES` / `SPHERE_STACKS` or `NUM_STARS` at the top of `final_project.py`.                          |
| **PyInstaller `.exe` crashes on launch**                  | Ensure `--collect-all OpenGL` and `--add-data "img;img"` were passed. Check `build/SolarSystem/warn-SolarSystem.txt` for missing modules. |
| **Fonts render as empty on Linux**                        | Some GLUT builds lack bitmap fonts. Install `freeglut3-dev` and rebuild/reinstall PyOpenGL.                         |

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. **Fork** the repository and create a feature branch from `main`.
2. Keep commits atomic and write clear commit messages.
3. Ensure all scripts still run from the repository root without errors.
4. New exercises should follow the existing naming convention (`NN_description.py`).
5. Open a **pull request** with a description of what you changed and why.

---

## License

This project is released under the [MIT License](LICENSE).

```
MIT License — Copyright (c) 2026 gragi-1
```
