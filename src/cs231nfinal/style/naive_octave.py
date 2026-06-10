from __future__ import annotations

import torch

from torchvision.io import read_image
from torchvision.transforms import Compose, Grayscale, Resize

from .base import Stylizer, StylizerArgs


class NaiveStylizerOctave(Stylizer):
    _style_image: torch.Tensor
    _style_image2: torch.Tensor
    _style_image4: torch.Tensor

    def __init__(self, sargs: StylizerArgs, k: int = 1) -> None:
        super().__init__(sargs, k=k)
        preT = Compose(
            [
                Resize(self._res),
                Grayscale(),
            ]
        )
        style_image1 = preT(read_image(self._style_path) / 255).squeeze().to(self._device)
        style_image2 = preT(style_image1.tile((1, 2, 2)))
        style_image4 = preT(style_image2.tile((1, 2, 2)))

        self._style_image = (style_image1 + style_image2 + style_image4) / 3

        if self._invert_style:
            torch.sub(1, self._style_image, out=self._style_image)

    def style(self, camera_views: torch.Tensor) -> torch.Tensor:
        style_mask = camera_views < (1.0 - 1e-6)
        return self._style_image.detach().clone() * style_mask + (1 - style_mask.to(torch.float32))
