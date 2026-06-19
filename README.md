# Bionics-Lab-Natural-Reach

Optimizing global biomechanical parameters to synthesize natural full-arm reaching trajectories for an impaired arm from the healthy arm's movement.

## Overview

In bilateral assistive and bionic systems, a common goal is to help an impaired arm produce purposeful, natural-looking movement. This project predicts the natural trajectory of an impaired (assisted) arm toward a target, using the movement of the healthy arm as the driving signal.

When the healthy arm reaches a point in space, the system computes a full joint-configuration trajectory that brings the impaired arm to the same point — not by mirroring the healthy arm's pose, but by synthesizing a movement that is natural for the impaired side.

The underlying biomechanics are described by a set of governing equations with a number of free parameters (θ). This repo focuses on finding the global parameter values that make the resulting motion as natural as possible.

## Problem Statement

- **Input:** the healthy arm's reaching movement and the target point it reaches.
- **Output:** a natural, full joint-configuration trajectory that brings the impaired arm to the same target point.
- **What we optimize:** a single, global set of parameters θ for the governing equations — tuned once, not recomputed per movement.
- **What "natural" means:** closeness of the synthesized trajectory to self-recorded natural reaching movements — measured as joint-trajectory error against the recordings, optionally combined with a smoothness term (e.g. minimum-jerk).

## Approach

The core is a global parameter-optimization loop:

1. Sense the healthy arm's trajectory and the target point it reaches.
2. Generate a candidate impaired-arm trajectory from the governing equations, parameterized by θ.
3. Score how natural the candidate is (cost term plus feasibility and joint-limit constraints).
4. Optimize θ to minimize the cost across the dataset.
5. Actuate the resulting trajectory on the impaired arm or model.

Because θ is global and fixed across movements, fitting it is effectively a system-identification problem: choose the parameters so the forward model reproduces natural movement across many recorded reaches, subject to physical constraints. A binary "natural / not natural" classifier is intentionally avoided in favor of a continuous, differentiable objective.

## Arm Model

The impaired arm is modeled as a 7-DOF kinematic chain:

| Index | Joint | DOF |
|-------|-------|-----|
| q0 | Shoulder flexion / extension | 1 |
| q1 | Shoulder abduction / adduction | 1 |
| q2 | Shoulder internal / external rotation | 1 |
| q3 | Elbow flexion / extension | 1 |
| q4 | Forearm pronation / supination | 1 |
| q5 | Wrist flexion / extension | 1 |
| q6 | Wrist radial / ulnar deviation | 1 |

## Data Format

Recorded trials are stored as CSV files under `data/`. Each file represents one reaching movement with one row per timestep:

```
time, q0, q1, q2, q3, q4, q5, q6, target_x, target_y, target_z
```

- Angles (`q0`–`q6`) in radians.
- Target (`target_x/y/z`) in metres — Cartesian position of the reached point.

## Project Structure

```
Bionics-Lab-Natural-Reach/
├── notebooks/
│   └── 01_data_collection.ipynb   # load, validate, and plot trial CSVs
├── data/                           # recorded reaching trials (CSV)
├── src/
│   ├── __init__.py
│   ├── model.py                    # ArmModel — parameterized forward model (7-DOF)
│   ├── optimize.py                 # fit_parameters() — global θ optimization
│   └── naturalness.py             # naturalness cost, smoothness penalty, joint-limit constraints
├── requirements.txt
└── README.md
```

## Getting Started

```bash
git clone https://github.com/<you>/Bionics-Lab-Natural-Reach.git
cd Bionics-Lab-Natural-Reach
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
jupyter lab
```

Open `notebooks/01_data_collection.ipynb` to load and inspect recorded movement data.

## Project Status

Early-stage research. The project scaffold is in place — directory structure, module interfaces, and data-loading utilities are ready. Current work is recording the movement dataset. The governing equations and forward model (`src/model.py`) will be implemented once data collection begins.

## Roadmap

- [ ] Record a dataset of natural reaching movements (healthy arm trajectories + target points)
- [ ] Implement the governing equations as a parameterized forward model (`src/model.py`)
- [ ] Define the naturalness objective and feasibility / joint-limit constraints (`src/naturalness.py`)
- [ ] Build the optimization loop for global θ (`src/optimize.py`)
- [ ] Validate against held-out natural movements
- [ ] (Optional) add a learned naturalness scorer if the analytical objective proves insufficient
