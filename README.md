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

## Recording Data

**Hardware required:** Xbox One Kinect v2, Kinect Adapter for Windows, Kinect for Windows SDK 2.0, USB 3.0 port.

**Recorder:** [DumpKinectSkeleton](https://github.com/sebtoun/DumpKinectSkeleton) — download the latest release, extract anywhere.

### Physical setup

1. Position the Kinect on a stable surface ~1.5–2 m in front of the subject, at roughly chest height.
2. Place a physical target (tape mark, small object) at a reachable point — ~50 cm in front at shoulder height is a good start.
3. **Measure the target's position** from the subject's shoulder with a tape measure and record it. Do not rely on the Kinect hand joint for ground-truth target coordinates.
4. Keep both arms unoccluded and square to the sensor throughout the reach.

### Recording a trial

Each trial captures one bilateral reach. The subject reaches with **both arms simultaneously** to the target, holds 1–2 seconds, then returns to neutral.

```
DumpKinectSkeleton.exe --prefix="C:\Bionics Lab\Bionics-Lab-Natural-Reach\data\t1_rep1"
```

Stop recording with **Ctrl+C** after the subject returns to neutral. Run a separate command per trial:

```
DumpKinectSkeleton.exe --prefix="...\data\t1_rep2"
DumpKinectSkeleton.exe --prefix="...\data\t1_rep3"
```

Aim for **5 trials per target location, 3–5 target locations** for a usable pilot dataset.

### Naming convention

```
t{target}_{side}_rep{n}.csv
```

Example: `t1_right_rep1.csv` = target 1, right arm as driving input, rep 1. Each bilateral recording produces two dataset entries (right-as-input and left-as-input), so note the designation explicitly — don't silently mix them.

### What the raw CSV looks like

Long format, one row per joint per frame (25 joints × ~30 fps):

```
Timestamp, JointID, Position.X/Y/Z, Orientation.X/Y/Z/W, State
```

`State`: 2 = Tracked, 1 = Inferred, 0 = NotTracked. The loader in `notebooks/01_data_collection.ipynb` pivots this to a per-frame array and flags frames where the reaching hand is not fully tracked.

### Notes

- Raw CSVs are gitignored — back them up to a shared drive separately.
- Verify the first CSV before recording more: timestamps should be monotonic, frame count ≈ duration × 30, reaching hand mostly `State=2`.

## Project Status

Early-stage research. The project scaffold is in place — directory structure, module interfaces, and data-loading utilities are ready. Current work is recording the movement dataset. The governing equations and forward model (`src/model.py`) will be implemented once data collection begins.

## Roadmap

- [ ] Record a dataset of natural reaching movements (healthy arm trajectories + target points)
- [ ] Implement the governing equations as a parameterized forward model (`src/model.py`)
- [ ] Define the naturalness objective and feasibility / joint-limit constraints (`src/naturalness.py`)
- [ ] Build the optimization loop for global θ (`src/optimize.py`)
- [ ] Validate against held-out natural movements
- [ ] (Optional) add a learned naturalness scorer if the analytical objective proves insufficient
