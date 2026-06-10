from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import torch

import matplotlib.pyplot as plt


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


@dataclass
class StylizerArgs:
    resolution: tuple[int, int]
    style_path: str
    invert_style: bool = False
    invert_render: bool = False
    device: str | int | torch.device = "mps"


def exp_loss_fn(a: torch.Tensor, b: torch.Tensor, k: int) -> torch.Tensor:
    return (torch.abs(a - b) ** (1 / k + 1)).mean() / (1 / k + 1)


class Stylizer(ABC):
    _res: tuple[int, int]
    _device: torch.device
    _invert_render: bool
    _invert_style: bool
    _style_path: str

    def __init__(self, sargs: StylizerArgs, k: int = 1) -> None:
        self.k = k
        self._res = sargs.resolution
        self._device = (
            torch.device(sargs.device)
            if isinstance(sargs.device, int) or isinstance(sargs.device, str)
            else sargs.device
        )
        self._invert_render = sargs.invert_render
        self._invert_style = sargs.invert_style
        self._style_path = sargs.style_path
        super().__init__()

    @abstractmethod
    def style(self, camera_views: torch.Tensor) -> torch.Tensor:
        pass

    def loss(self, render_stack: torch.Tensor) -> torch.Tensor:
        loss_fn = torch.nn.MSELoss()
        render_stack_channels = render_stack.unsqueeze(1).repeat((1, 3, 1, 1)).detach()
        if self._invert_render:
            torch.sub(1, render_stack_channels, out=render_stack_channels)

        style = self.style(render_stack_channels.to(self._device)).mean(
            1, keepdim=True
        )  # mean over color

        # plt.imshow(style[0].permute((1,2,0)).to(torch.float32).cpu())
        # plt.show()

        # style_loss = loss_fn(render_stack, style)  # + tv_loss
        style_loss = exp_loss_fn(render_stack.unsqueeze(1).to(self._device), style, self.k)
        return style_loss
