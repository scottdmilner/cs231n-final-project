from __future__ import annotations

import torch

import StyleID
# from omegaconf import OmegaConf
# from StyleID.ldm.models.diffusion.ddim import DDIMSampler
import copy
from einops import rearrange


from .base import DotDict, Stylizer, StylizerArgs


import cv2

from StyleID.diffusers_implementation.stable_diffusion import (
    load_stable_diffusion,
    encode_latent,
    decode_latent,
    get_text_embedding,
    get_unet_layers,
    attention_op,
)
from StyleID.diffusers_implementation.run_styleid_diffusers import style_transfer_module
from StyleID.diffusers_implementation.utils import normalize


class InjectionStylizer2(Stylizer):
    def __init__(self, sargs, invert: bool = False) -> None:
        super().__init__(sargs)

        self.ddim_steps = 8
        self.device = "mps"
        self.dtype = torch.float16
        self.in_c = 4
        self.guidance_scale = 0  # no text

        self.style_text = None
        self.content_text = None

        self.style_transfer_params = {
            "gamma": 0.75,
            "tau": 1.5,
            "injection_layers": [7, 8, 9, 10, 11],
        }

        # Get SD modules
        sd_version = "1.5"  # can be better, need to register
        self.vae, self.tokenizer, self.text_encoder, self.unet, self.scheduler = (
            load_stable_diffusion(sd_version=sd_version, precision_t=self.dtype)
        )
        self.scheduler.set_timesteps(self.ddim_steps)
        sample_size = self.unet.config.sample_size

        # Init style transfer module
        cfg = DotDict()
        cfg.sd_version = sd_version

        self.unet_wrapper = style_transfer_module(
            self.unet,
            self.vae,
            self.text_encoder,
            self.tokenizer,
            self.scheduler,
            cfg,
            style_transfer_params=self.style_transfer_params,
        )

        # Get style image tokens
        denoise_kwargs = self.unet_wrapper.get_text_condition(self.style_text)

        self.unet_wrapper.trigger_get_qkv = True  # get attention features (key, value)
        self.unet_wrapper.trigger_modify_qkv = False

        style_image = cv2.imread(self._style_path)[:, :, ::-1]
        normalized_style_image = (
            normalize(style_image).repeat(1, 1, 1, 1).to(device=self.vae.device, dtype=self.dtype)
        )
        print(normalized_style_image.shape)
        if invert:
            normalized_style_image = 1 - normalized_style_image
        style_latent = encode_latent(normalized_style_image, self.vae)
        # style_latent = encode_latent(torch.tensor(style_image).unsqueeze(0).permute((0,3,1,2)).to(device=self.vae.device, dtype=self.dtype), self.vae)

        # invert process
        print("Invert style image...")
        images, latents = self.unet_wrapper.invert_process(
            style_latent, denoise_kwargs=denoise_kwargs
        )  # reverse process save activations such as attn, res
        style_latent = latents[-1]

        # ================= IMPORTANT =================
        # save key value from style image
        self.style_features = copy.deepcopy(self.unet_wrapper.attn_features)
        # =============================================

    def style(self, camera_views: torch.Tensor) -> torch.Tensor:
        # Get content image tokens
        denoise_kwargs = self.unet_wrapper.get_text_condition(self.content_text)

        self.unet_wrapper.trigger_get_qkv = True
        self.unet_wrapper.trigger_modify_qkv = False
        content_latent = encode_latent(
            camera_views.to(device=self.vae.device, dtype=self.dtype), self.vae
        )
        print("content_latent.shape", content_latent.shape)

        # invert process
        print("Invert content image...")
        print(denoise_kwargs["encoder_hidden_states"].shape)
        # denoise_kwargs["encoder_hidden_states"] = denoise_kwargs["encoder_hidden_states"].repeat(5,1,1)
        images, latents = self.unet_wrapper.invert_process(
            content_latent, denoise_kwargs=denoise_kwargs
        )  # reverse process save activations such as attn, res
        content_latent = latents[-1]

        # ================= IMPORTANT =================
        # save res feature from content image
        content_features = copy.deepcopy(self.unet_wrapper.attn_features)

        # print(content_features["layer7_attn"][21][2].shape)
        # =============================================
        # ================= IMPORTANT =================
        # Set modify features
        for layer_name in self.style_features.keys():
            self.unet_wrapper.attn_features_modify[layer_name] = {}
            for t in self.scheduler.timesteps:
                t = t.item()
                self.unet_wrapper.attn_features_modify[layer_name][t] = (
                    content_features[layer_name][t][0],
                    self.style_features[layer_name][t][1],
                    self.style_features[layer_name][t][2],
                )  # content as q / style as kv
        # =============================================

        self.unet_wrapper.trigger_get_qkv = False
        # self.unet_wrapper.trigger_modify_qkv = not cfg.without_attn_injection # modify attn feature (key value)
        self.unet_wrapper.trigger_modify_qkv = True

        # Generate style transferred image
        denoise_kwargs = self.unet_wrapper.get_text_condition(self.content_text)

        latent_cs = content_latent

        # print(denoise_kwargs)
        # reverse process
        print("Style transfer...")
        images, latents = self.unet_wrapper.reverse_process(
            latent_cs, denoise_kwargs=denoise_kwargs
        )  # reverse process save activations such as attn, res
        return images[1]
