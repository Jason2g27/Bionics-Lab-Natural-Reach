# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Persistent context for Claude Code. See README.md for the public-facing overview; this file is the working context and decisions log.

## What this project is

Bionics research. Given one arm's reaching movement to a target point, predict the natural full joint-configuration trajectory that brings the *other* arm to the same world-space point. There is no impaired subject in this phase — all data comes from healthy subjects. One arm's trajectory is the **driving signal (input)**; the other arm's trajectory to the same target is the **natural-movement reference (validation target)**.

**Important:** this is not a mirror. Both arms reach the same physical point; the relationship between the two arms' trajectories is what the model captures.

The modeled arm is represented as a 7-DOF kinematic chain (shoulder 3-DOF, elbow, forearm, wrist 2-DOF).

## Method

A set of governing equations (prospectus eqs 4.1–4.7, 6-step pipeline) acts as a forward model: `path = f(start, end, θ)`. θ is global — one parameter set (e, ΔL_la, timing), fit once across the dataset, not recomputed per movement. Fitting θ is a system-identification problem: choose θ so model-generated paths match recorded natural reaches.

The generation pipeline stops at **velocity** (Step 6). The objective matches both **position and velocity profiles** against healthy-subject data (§4.4). Acceleration (θ̈r) appears only in the EXO-UL8 robot equation of motion (eq 2.10, Chapter 2) — that's the exoskeleton controller's plant dynamics in a later phase, not something estimated from motion-capture data and not part of fitting the deviation variables.

Consequence: **30 Hz Kinect is sufficient. No IMU needed.** Velocity is a single differentiation — the clean tier. We never double-differentiate measured data, so acceleration-noise concerns do not arise.

No classifier. The objective is continuous and differentiable. A binary natural/not classifier is intentionally avoided — bad gradients, gameable.

## Decisions and gotchas (don't re-litigate without reason)

- **Velocity from Δ(joint angle) / Δ(actual timestamps), never Δangle / (1/30).** The matching target is the velocity profile itself, so timestamp jitter directly corrupts the fit.
- **Data pipeline order is load-bearing:** real per-frame timestamps → resample onto a uniform time grid → zero-phase low-pass (Butterworth + `filtfilt`) → then differentiate for velocity.
- **No naive finite differences for velocity.** Prefer a smoothing spline or Savitzky–Golay filter on joint-angle traces and differentiate analytically.
- **Reference frame:** convert Kinect camera-space coords to a body-centered frame (shoulder/spine midline; x toward right shoulder, matching the prospectus convention) before fitting.
- **Kinect gives joint positions; the model needs joint angles.** Derive shoulder/elbow/wrist angles from the joint-position vectors (or orientation quaternions). Decide the angle convention early and keep it consistent with the prospectus's 7-DOF definition.
- **Sensor limits:** Kinect v2 is 30 Hz → ~20–35 samples per reach. Fine for velocity. Hand/wrist are the noisiest joints — keep the arm square to the camera and unoccluded.

## Data collection

**Hardware:** Xbox One Kinect v2 + Kinect Adapter for Windows, Kinect for Windows SDK 2.0, USB 3.0. Sensor verified working (skeleton visible in Kinect Studio). Lab also has a dedicated mocap system + EXO-UL8 for later phases; Kinect is the first/cheap pass.

**Recorder:** DumpKinectSkeleton (sebtoun) → CSV. Needs .NET Framework 4.5+ (4.8 present on modern Windows).

**Raw CSV format** (long, one row per joint per frame):
```
Timestamp, JointID, Position.X/Y/Z, Orientation.X/Y/Z/W, State
```
- `State`: 2=Tracked, 1=Inferred, 0=NotTracked. Pivot in pandas to per-frame joint arrays.
- Record **both arms simultaneously**. Each bilateral trial yields two dataset samples: once with right arm as input / left as reference, once with left as input / right as reference. This doubles effective sample count without extra recording time. Note the designation in the filename or a sidecar; don't silently mix left-input and right-input samples.
- Pilot labeling: capture one file per trial via `--prefix=t1_rep1` etc. to skip segmentation; switch to one continuous file + speed-threshold segmentation later.
- Independently measure physical target locations — don't rely on the noisy Kinect hand for ground-truth endpoints.

**Processed dataset format** (what `src/optimize.py` expects), one dict per trial:
```
't'      : (T,)     time [s], uniform grid
'q_ref'  : (T, 7)   joint angles [rad]
'q_dot_ref' : (T, 7) joint velocities [rad/s]
'target' : (3,)     Cartesian target [m], body-centered frame
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
jupyter lab
```

Stack: Python, Jupyter notebooks. Libraries: numpy, scipy (`scipy.optimize` for the fit), pandas, matplotlib.

## Key commands

```bash
jupyter lab notebooks/01_data_collection.ipynb
python -m src.optimize
pytest                          # no tests yet; use when added
```

In notebooks, use `%autoreload 2` and keep logic thin — reusable code lives in `src/`.

## Architecture

### Data flow

```
Kinect CSV (long format)
    → pivot to per-frame arrays
    → body-centered reference frame (shoulder/spine midline, prospectus convention)
    → joint positions → joint angles (via position vectors or orientation quaternions)
    → resample to uniform time grid
    → zero-phase low-pass filter (Butterworth + filtfilt)
    → differentiate via spline / SG filter → joint velocities
    → dataset: list[dict]  (see format above)
         ↓
fit_parameters(dataset, theta_init)   ← src/optimize.py
         ↓
ArmModel(theta).forward(target, t)    ← src/model.py  [eqs 4.1–4.7]
         ↓
naturalness_cost(q_pred, q_dot_pred, q_ref, q_dot_ref, t)   ← src/naturalness.py
```

### Module responsibilities

- **`src/model.py`** — `ArmModel` class: holds θ = (e, ΔL_la, timing), exposes `forward(target, t) → (T, 7)` joint trajectory (and velocity). Implements the 6-step forward model (eqs 4.1–4.7). `JOINT_LIMITS` (radians) are placeholder values to be updated from measurements.
- **`src/naturalness.py`** — `naturalness_cost` (position + velocity profile error vs. recordings, optional smoothness), `smoothness_penalty`, `joint_limit_penalty` (soft constraint). `smoothness_weight=0` disables smoothness.
- **`src/optimize.py`** — `fit_parameters()` wraps `scipy.optimize.minimize` (default L-BFGS-B). `_objective` computes mean cost across the dataset and is the only place that instantiates `ArmModel` during optimization.
- **`notebooks/01_data_collection.ipynb`** — Load, validate, and plot trial CSVs; provides `load_trial()` converting CSV → dataset dict.

## Code conventions

Code should read like a well-informed student wrote it: functional and principled, not over-engineered. Prefer targeted patches over heavy rewrites.

## Current status / next steps

- [done] Sensor verified working.
- [done] Derivative order resolved: position + velocity objective, no acceleration from motion capture → 30 Hz Kinect sufficient, no IMU needed.
- [next] Run a 5-reach DumpKinectSkeleton pilot using per-trial `--prefix`.
- [next] Inspect the CSV: timestamps real, monotonic, units confirmed; frame count ≈ duration × 30; reaching-hand not mostly Inferred.
- Build CSV loader (pivot long → per-frame) + reference-frame transform + joint-angle extraction + resample-to-uniform-grid + zero-phase filter + velocity via spline.
- Implement the 6-step forward model (eqs 4.1–4.7) → position + velocity objective → global θ optimizer (e, ΔL_la, timing) → validate on held-out reaches.
