"""Naturalness objective and feasibility constraints."""

import numpy as np


def naturalness_cost(q_pred: np.ndarray, q_ref: np.ndarray, t: np.ndarray,
                     smoothness_weight: float = 0.0) -> float:
    """
    Compute the naturalness cost for a predicted trajectory.

    Parameters
    ----------
    q_pred           : (T, N_JOINTS) — synthesized trajectory [rad]
    q_ref            : (T, N_JOINTS) — reference (recorded) natural trajectory [rad]
    t                : (T,)          — time samples [s]
    smoothness_weight: weight on the minimum-jerk smoothness penalty (0 = disabled)

    Returns
    -------
    cost : scalar float
    """
    raise NotImplementedError("Naturalness objective not yet implemented.")


def smoothness_penalty(q: np.ndarray, t: np.ndarray) -> float:
    """Integrated squared jerk across all joints."""
    raise NotImplementedError


def joint_limit_penalty(q: np.ndarray, limits: np.ndarray) -> float:
    """Soft penalty for exceeding joint limits."""
    raise NotImplementedError
