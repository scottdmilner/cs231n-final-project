from __future__ import annotations

import torch

from PIL import Image
from torchvision.transforms import Compose, Lambda, Normalize, Resize, ToTensor

from gatys import VGG, GramMatrix, GramMSELoss, GATYS_VGG_WEIGHTS

from .base import Stylizer, StylizerArgs


class GatysStylizer(Stylizer):
    def _prep(self, img: torch.Tensor):
        t = Compose(
            [
                Resize(self._res),
                Lambda(lambda x: x[torch.LongTensor([2, 1, 0])]),  # turn to BGR
                Normalize(
                    mean=[0.40760392, 0.45795686, 0.48501961],  # subtract imagenet mean
                    std=[1, 1, 1],
                ),
                Lambda(lambda x: x.mul_(255)),
            ]
        )
        return t(img).unsqueeze(0)

    def __init__(
        self,
        sargs: StylizerArgs,
        style_weights: list[float] | None = None,
    ) -> None:
        super().__init__(sargs)

        if style_weights is None:
            # these are good weights settings:
            style_weights = [1e3 / n**2 for n in [64, 128, 256, 512, 512]]

        self.vgg = VGG()
        self.vgg.load_state_dict(torch.load(GATYS_VGG_WEIGHTS))

        for param in self.vgg.parameters():
            param.requires_grad = False

        self.vgg.to(self._device)

        self.style_image = self._prep(ToTensor()(Image.open(self._style_path))).to(self._device)
        if self._invert_style:
            torch.sub(1, self.style_image, out=self.style_image)

        # define layers, loss functions, weights and compute optimization targets
        self.style_layers = ["r11", "r21", "r31", "r41", "r51"]
        self.loss_layers = self.style_layers
        loss_fns = [GramMSELoss()] * len(self.style_layers)
        self.loss_fns = [loss_fn.to(self._device) for loss_fn in loss_fns]

        self.weights = style_weights

        # compute optimization targets
        style_targets = [
            GramMatrix()(A).detach() for A in self.vgg(self.style_image, self.style_layers)
        ]
        self.targets = style_targets

    def style(self, camera_views: torch.Tensor) -> torch.Tensor:
        pass

    def loss(
        self, render_stack: torch.Tensor, mask_stack: torch.Tensor | None = None
    ) -> torch.Tensor:
        render_stack_channels = render_stack.unsqueeze(1).repeat((1, 3, 1, 1)).to(self._device)
        if self._invert_render:
            torch.sub(1, render_stack_channels, out=render_stack_channels)
        out = self.vgg(render_stack_channels, self.loss_layers)
        layer_losses = torch.stack(
            [self.weights[a] * self.loss_fns[a](A, self.targets[a]) for a, A in enumerate(out)]
        )

        return layer_losses.sum()
