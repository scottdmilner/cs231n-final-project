from __future__ import annotations

from pathlib import Path

import os
import torch

from torchvision.transforms import Compose, CenterCrop, Resize, ToTensor, functional
from PIL import Image

import AesPA_Net.baseline as aespa
from AesPA_Net.baseline import size_arrange, contextual_loss_v2, gram_matrix

from .base import DotDict, Stylizer, StylizerArgs

import matplotlib.pyplot as plt
import numpy as np


def highpass(img):
    f_transform = np.fft.fft2(img)
    f_shift = np.fft.fftshift(f_transform)

    # 3. Create the High-Pass Filter (HPF) Mask
    rows, cols = img.shape[-2:]
    crow, ccol = rows // 2, cols // 2  # Center point of the frequency image

    # Define cutoff radius
    cutoff_radius = 50

    # Block out the center low-frequencies by setting a circle of radius to 0
    y, x = np.ogrid[:rows, :cols]
    center_distance = (x - ccol)**2 + (y - crow)**2

    gaussian_lpf = np.exp(-center_distance / (2 * (cutoff_radius ** 2)))
    mask_gaussian = 1 - gaussian_lpf

    # 4. Apply the mask to the shifted FFT spectrum
    f_shift_filtered = f_shift * mask_gaussian

    # 5. Inverse FFT to return to spatial domain (the image pixels)
    f_ishift = np.fft.ifftshift(f_shift_filtered)
    img_back = np.fft.ifft2(f_ishift)
    # img_back = np.abs(img_back)  
    img_back = np.real(img_back)

    return img_back



class AespaStylizerSDS(Stylizer):
    def __init__(self, sargs: StylizerArgs, k: int = 1, crop: tuple[int, int]|None = None) -> None:
        super().__init__(sargs)
        self.k = k
        prepT = Compose(
            [
                ToTensor(),
                *([CenterCrop(crop)] if crop is not None else []),
                Resize(self._res),
            ]
        )

        self._style = size_arrange(prepT(Image.open(self._style_path))[:3,:,:].to(self._device).unsqueeze(0))

        args = DotDict(
            {
                "comment": "aespa",
                "type": "test",
                "batch_size": 1,
                "content_dir": "../../data/style/lame_ones",
                "style_dir": "../../data/style/good_ones",
                "train_result_dir": str(Path(aespa.__file__).parent / "train_results"),
                "test_result_dir": "../results",
                "num_workers": 4,
                "lr": 1e3,
                "device": "mps",
            }
        )
        self.model = aespa.Baseline(args)
        self.model.network.eval()
        for param in self.model.network.parameters():
            param.requires_grad = False

    def style(self, camera_view: torch.Tensor) -> torch.Tensor:
        pass

    def loss(self, render_stack: torch.Tensor, mask_stack: torch.Tensor | None = None) -> torch.Tensor:
        self.model.network.decoder.load_state_dict(
            torch.load(
                os.path.join(self.model.result_st_dir, "dec_model_.pth"), map_location=self._device
            )["state_dict"]
        )
        self.model.network.transformer.load_state_dict(
            torch.load(
                os.path.join(self.model.result_st_dir, "transformer_model_.pth"),
                map_location=self._device,
            )["state_dict"]
        )

        self.model.network.train(False)
        self.model.network.eval()

        # styles = []
        # for render in render_stack:
        render_stack_channels = render_stack.unsqueeze(1).repeat((1,3,1,1)).to(self._device)
        style = self._style.repeat((render_stack_channels.shape[0], 1, 1, 1))
        content = size_arrange(render_stack_channels)

        gray_content = functional.rgb_to_grayscale(content).repeat(1,3,1,1)

        style_adaptive_alpha = (
            (
                (
                    self.model.adaptive_gram_weight(style, 1, 8)
                    + self.model.adaptive_gram_weight(style, 2, 8)
                    + self.model.adaptive_gram_weight(style, 3, 8)
                )
                / 3
            )
            .unsqueeze(1)
            .to(self._device)
        )

        stylization, _, _, _, _ = self.model.network(content, style, style_adaptive_alpha, gray_content, style)

        # hp_style = highpass(stylization.clone().detach().mean(dim=1).cpu().numpy())
        # hp_render = highpass(render_stack.clone().detach().cpu().numpy())


        # return torch.Tensor(hp_style - hp_render)
            

            # plt.imshow(img_back[0])
            # plt.colorbar()
            # plt.show()
        # loss_fn = torch.nn.MSELoss()
        def exp_loss_fn(a: torch.Tensor, b: torch.Tensor, k: int) -> torch.Tensor:
            return (torch.abs(a - b) ** (1 / k + 1)).mean() / (1 / k + 1)
        # return loss_fn(stylization, render_stack.unsqueeze(1).to(self._device))
        return exp_loss_fn(stylization, render_stack.unsqueeze(1).to(self._device), self.k)
