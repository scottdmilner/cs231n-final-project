from abc import ABC, abstractmethod

import torch
from torchvision.io import read_image
from torchvision.transforms import Resize, Grayscale


class Stylizer(ABC):
    _res: tuple[int, int]

    def __init__(self, resolution: tuple[int, int]) -> None:
        self._res = resolution
        super().__init__()

    @abstractmethod
    def style(self, views: torch.Tensor) -> torch.Tensor:
        pass


class NaiveStylizer(Stylizer):
    _style_image: torch.Tensor

    def __init__(
        self, resolution: tuple[int, int], image_path: str, invert: bool = False
    ) -> None:
        resize_T = Resize(resolution)
        grayscale_T = Grayscale()
        self._style_image = grayscale_T(
            resize_T(read_image(image_path) / 255)
        ).squeeze()

        if invert:
            self._style_image = 1 - self._style_image

        super().__init__(resolution)

    def style(self, views: torch.Tensor) -> torch.Tensor:
        style_mask = views < (1.0 - 1e-6)
        return self._style_image.detach().clone() * style_mask + (
            1 - style_mask.to(torch.float32)
        )
