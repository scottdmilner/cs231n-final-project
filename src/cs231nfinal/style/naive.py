from __future__ import annotations

import torch

from torchvision.io import read_image
from torchvision.transforms import Compose, Grayscale, Resize

from .base import Stylizer, StylizerArgs


class NaiveStylizer(Stylizer):
    _style_image: torch.Tensor

    def __init__(self, sargs: StylizerArgs, k: int = 1) -> None:
        super().__init__(sargs, k=k)
        preT = Compose(
            [
                Resize(self._res),
                Grayscale(),
            ]
        )
        self._style_image = preT(read_image(self._style_path) / 255).squeeze().to(self._device)

        if self._invert_style:
            torch.sub(1, self._style_image, out=self._style_image)

    def style(self, camera_views: torch.Tensor) -> torch.Tensor:
        style_mask = camera_views < (1.0 - 1e-6)
        return self._style_image.detach().clone() * style_mask + (1 - style_mask.to(torch.float32))
