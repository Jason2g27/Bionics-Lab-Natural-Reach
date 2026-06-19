"""Global parameter optimization for theta."""

import numpy as np
from scipy.optimize import OptimizeResult

from .model import ArmModel
from .naturalness import naturalness_cost


def fit_parameters(
    dataset: list[dict],
    theta_init: np.ndarray,
    smoothness_weight: float = 0.0,
    method: str = "L-BFGS-B",
    **scipy_kwargs,
) -> OptimizeResult:
    """
    Find the global theta that minimizes naturalness cost across the dataset.

    Parameters
    ----------
    dataset         : list of dicts, each with keys:
                        'target'  : (3,) Cartesian target [m]
                        't'       : (T,) time samples [s]
                        'q_ref'   : (T, N_JOINTS) reference trajectory [rad]
    theta_init      : initial parameter vector
    smoothness_weight: passed through to naturalness_cost
    method          : scipy.optimize.minimize method
    **scipy_kwargs  : forwarded to scipy.optimize.minimize

    Returns
    -------
    result : scipy OptimizeResult (.x holds the fitted theta)
    """
    raise NotImplementedError("Optimization loop not yet implemented.")


def _objective(theta: np.ndarray, dataset: list[dict],
               smoothness_weight: float) -> float:
    model = ArmModel(theta)
    total = 0.0
    for sample in dataset:
        q_pred = model.forward(sample["target"], sample["t"])
        total += naturalness_cost(q_pred, sample["q_ref"], sample["t"],
                                  smoothness_weight)
    return total / len(dataset)
