from __future__ import annotations

from pathlib import Path

import torch

from torchvision.transforms import Compose, Resize, ToTensor, functional
from PIL import Image

import AesPA_Net.baseline as aespa
from AesPA_Net.baseline import size_arrange, contextual_loss_v2, gram_matrix

from .base import DotDict, Stylizer, StylizerArgs


class AespaStylizer(Stylizer):
    def __init__(self, image_path: str, sargs: StylizerArgs) -> None:
        super().__init__(sargs)
        prepT = Compose([
            ToTensor(),
            Resize(self._res),
        ])

        self._style = size_arrange(prepT(Image.open(image_path)).to(self._device).unsqueeze(0))

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
    
    def style(self, camera_views: torch.Tensor) -> torch.Tensor:
        pass

    def loss(self, render_stack: torch.Tensor, mask_stack: torch.Tensor|None=None) -> torch.Tensor:
        render_stack_channels = render_stack.unsqueeze(1).repeat((1, 3, 1, 1)).to(self._device)
        style = self._style.repeat((render_stack_channels.shape[0], 1, 1, 1))

        content = size_arrange(render_stack_channels)

        gray_content = functional.rgb_to_grayscale(content).repeat(1, 3, 1, 1)
        # gray_style = transforms.functional.rgb_to_grayscale(style).repeat(1, 3, 1, 1)

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
            # + (
            #     (
            #         self.model.adaptive_gram_weight(gray_style, 1, 8)
            #         + self.model.adaptive_gram_weight(gray_style, 2, 8)
            #         + self.model.adaptive_gram_weight(gray_style, 3, 8)
            #     )
            #     / 3
            # )
            # .unsqueeze(1)
            # .to(self._device)
        ) # / 2

        # content_recon, _, _, _, _ = self.model.network(
        #     gray_content, content, torch.ones_like(style_adaptive_alpha), gray_content, content
        # )
        # style_recon, _, _, _, _ = self.model.network(
        #     gray_style, style, style_adaptive_alpha, gray_style, style
        # )

        stylization, attn_style_4_1, attn_style_5_1, attn_map_4_1, attn_map_5_1 = (
            self.model.network(content, style, style_adaptive_alpha, gray_content, style)
        )

        global_style_loss = 0
        local_style_loss = 0

        local_style_loss = self.model.proposed_local_gram_loss_v2(
            stylization, style, style_adaptive_alpha
        )

        for level in [2, 3, 4, 5]:
            stylized_feat = self.model.network.encoder.get_features(stylization, level)
            style_feat = self.model.network.encoder.get_features(style, level)
            content_feat = self.model.network.encoder.get_features(content, level)
            # recon_style_feat = self.model.network.encoder.get_features(style_recon, level)
            # recon_content_feat = self.model.network.encoder.get_features(content_recon, level)

            # identity_loss2 += self.model.calc_content_loss(
            #     recon_content_feat, content_feat
            # ) + self.model.calc_content_loss(recon_style_feat, style_feat)

            if level in [4, 5]:
                # global_style_loss += self.calc_style_loss(stylized_feat, style_feat, dim=True)
                global_style_loss += self.model.calc_style_loss_centered_gram(
                    stylized_feat, style_feat, dim=True
                )
                # content_loss += self.model.calc_content_loss(
                #     stylized_feat, content_feat, norm=True
                # )
                # if level == 4:
                #     cx_loss += (
                #         contextual_loss_v2(content_feat, recon_content_feat)
                #     ) + (contextual_loss_v2(style_feat, recon_style_feat))
            del (
                style_feat,
                content_feat,
                stylized_feat,
                # recon_content_feat,
                # recon_style_feat,
            )
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            elif torch.mps.is_available():
                torch.mps.empty_cache()

        attnded_style_loss = torch.mean(
            (
                self.model.MSE_instance_loss(
                    gram_matrix(attn_style_4_1),
                    gram_matrix(self.model.network.encoder.get_features(stylization, 4)),
                )
                + self.model.MSE_instance_loss(
                    gram_matrix(attn_style_5_1),
                    gram_matrix(self.model.network.encoder.get_features(stylization, 5)),
                )
            ),
            dim=(1, 2),
        )
        total_loss = (
            # 1.0*content_loss
            # + 1.0*identity_loss2
            # + 0.2 * local_style_loss
            # + 100.0 * torch.mean(attnded_style_loss * style_adaptive_alpha)
            + 10.0 * torch.mean(global_style_loss * (1 - style_adaptive_alpha))
            # + 1.5*color_loss
            # + tv_loss
            # + 0.1*G_loss #Final_v9_adv_t2_no_adv
        )
        return total_loss