from __future__ import annotations

import numpy as np

from typing import TYPE_CHECKING

from pyglm.glm import vec3, mat4, lookAt

from scipy.stats import vonmises_fisher

if TYPE_CHECKING:
    from collections.abc import Iterator


def RandomCameraTransform(
    camera_dist: float = 10,
    kappa: float = np.inf,
    seed: int | None = None,
) -> Iterator[mat4]:
    vmf = vonmises_fisher(mu=(-1,0,0), kappa=kappa)
    rng = np.random.default_rng(seed=seed)

    while True:
        eye = camera_dist * vmf.rvs(random_state=rng).flatten()

        yield lookAt(vec3(eye), (0, 0, 0), (0, 1, 0))


__all__ = ["RandomCameraTransform"]
