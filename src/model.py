"""Parameterized forward model for the impaired arm (7-DOF, 3-D)."""

import numpy as np

# Joint indices for the 7-DOF arm
# q[0]  shoulder flexion/extension
# q[1]  shoulder abduction/adduction
# q[2]  shoulder internal/external rotation
# q[3]  elbow flexion/extension
# q[4]  forearm pronation/supination
# q[5]  wrist flexion/extension
# q[6]  wrist radial/ulnar deviation
N_JOINTS = 7

# Placeholder joint limits [min, max] in radians — update with measured values
JOINT_LIMITS = np.array([
    [-1.57,  3.14],   # shoulder flex/ext
    [-0.52,  1.57],   # shoulder abd/add
    [-1.57,  0.52],   # shoulder int/ext rotation
    [ 0.00,  2.53],   # elbow flex/ext
    [-1.57,  1.57],   # forearm pronation/supination
    [-1.22,  1.22],   # wrist flex/ext
    [-0.52,  0.35],   # wrist radial/ulnar deviation
])


class ArmModel:
    """
    Forward model: given global parameters theta and a target point,
    produce a joint-angle trajectory q(t) of shape (T, N_JOINTS).
    """

    def __init__(self, theta: np.ndarray):
        self.theta = np.asarray(theta, dtype=float)

    def forward(self, target: np.ndarray, t: np.ndarray) -> np.ndarray:
        """
        Generate an impaired-arm trajectory toward `target`.

        Parameters
        ----------
        target : (3,) array — Cartesian target position [m]
        t      : (T,) array — time samples [s]

        Returns
        -------
        q : (T, N_JOINTS) array — joint angles [rad]
        """
        raise NotImplementedError("Governing equations not yet implemented.")

    def within_joint_limits(self, q: np.ndarray) -> bool:
        """Return True if every joint angle in q is within JOINT_LIMITS."""
        return bool(
            np.all(q >= JOINT_LIMITS[:, 0]) and np.all(q <= JOINT_LIMITS[:, 1])
        )
