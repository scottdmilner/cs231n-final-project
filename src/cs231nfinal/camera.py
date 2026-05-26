from __future__ import annotations

import numpy as np

from typing import TYPE_CHECKING

from cs248a_renderer.model.transforms import Transform3D
from pyglm.glm import vec3, quat, mat4, normalize, cross, dot, lookAt

if TYPE_CHECKING:
    from collections.abc import Iterator


def RandomCameraTransform(
    camera_pos: vec3 = vec3(0, 0, 10),
    sigma: float = 0,
    seed: int | None = None,
) -> Iterator[mat4]:
    forward = vec3(0, 0, 1)
    rng = np.random.default_rng(seed=seed)

    while True:
        v = vec3(*rng.normal((*forward,), sigma))
        v = normalize(v)

        random_transform = Transform3D(
            rotation=normalize(quat(dot(forward, v) + 1, *cross(forward, v)))
        )

        yield lookAt(random_transform.get_matrix() @ -camera_pos, (0, 0, 0), (0, 1, 0))


__all__ = ["RandomCameraTransform"]
