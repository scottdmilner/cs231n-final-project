from __future__ import annotations

import torch
import StyleID
from StyleID.run_styleid import load_model_from_config, load_img
from pytorch_lightning import seed_everything
from torch import autocast
from contextlib import nullcontext
from omegaconf import OmegaConf
from StyleID.ldm.models.diffusion.ddim import DDIMSampler
import numpy as np
import os
from pathlib import Path
import pickle
import copy
from einops import rearrange

from .base import Stylizer, StylizerArgs


class InjectionStylizer(Stylizer):
    def __init__(self, resolution: tuple[int, int], image_path: str, invert: bool = False) -> None:
        model_config_str = "models/ldm/stable-diffusion-v1/v1-inference.yaml"
        model_weights_str = "models/ldm/stable-diffusion-v1/model.ckpt"
        self.self_attn_output_block_indices = [6, 7, 8, 9, 10, 11]
        self.ddim_inversion_steps = 50
        self.save_feature_timesteps = self.ddim_steps = 50
        self.ddim_eta = 0.0
        self.device = torch.device("mps")
        self.gamma = 0.75
        self.T = 1.5
        self.start_step = 49
        self.precision = "autocast"  # ["full", "autocast"]
        C = 4  # latent channels
        H = resolution[0]
        W = resolution[1]
        f = 8  # downsampling factor
        feat_path_root = "./features"
        self.feat_maps = []

        seed_everything(22)

        model_config = OmegaConf.load(model_config_str)
        self.model = load_model_from_config(model_config, model_weights_str)

        self.model = self.model.to(self.device)

        self.unet_model = self.model.model.diffusion_model

        self.sampler = DDIMSampler(self.model)
        self.sampler.make_schedule(
            ddim_num_steps=self.ddim_steps, ddim_eta=self.ddim_eta, verbose=False
        )
        time_range = np.flip(self.sampler.ddim_timesteps)
        self.idx_time_dict = {}
        self.time_idx_dict = {}
        for i, t in enumerate(time_range):
            self.idx_time_dict[t] = i
            self.time_idx_dict[i] = t

        seed = torch.initial_seed()

        # global feat_maps
        self.feat_maps = [{"config": {"gamma": self.gamma, "T": self.T}} for _ in range(50)]

        self.precision_scope = autocast if self.precision == "autocast" else nullcontext
        self.uc = self.model.get_learned_conditioning([""])
        self.shape = [C, H // f, W // f]

        # sty_img_list = sorted(os.listdir(opt.sty))
        # cnt_img_list = sorted(os.listdir(opt.cnt))

        sty_image_list = [image_path]
        img_path = Path(image_path)
        # sty_name_ = os.path.join(opt.sty, sty_name)

        sty_name_ = str(img_path)
        # init_sty = load_img(sty_name_).to(self.device)
        cam_view_num = 8
        init_sty = load_img(sty_name_).to(self.device)  # .repeat((cam_view_num,1,1,1))
        seed = -1
        # sty_feat_name = os.path.join(feat_path_root, os.path.basename(sty_name).split('.')[0] + '_sty.pkl')
        sty_feat_name = os.path.join(feat_path_root, img_path.stem + f"_{invert}_sty.pkl")
        sty_z_enc = None
        # print(sty_feat_name)

        if len(feat_path_root) > 0 and os.path.isfile(sty_feat_name):
            print("Precomputed style feature loading: ", sty_feat_name)
            with open(sty_feat_name, "rb") as h:
                sty_feat = pickle.load(h)
                sty_z_enc = torch.clone(sty_feat[0]["z_enc"])
        else:
            init_sty = self.model.get_first_stage_encoding(self.model.encode_first_stage(init_sty))
            sty_z_enc, _ = self.sampler.encode_ddim(
                init_sty.clone(),
                num_steps=self.ddim_inversion_steps,
                unconditional_conditioning=self.uc,
                end_step=self.time_idx_dict[self.ddim_inversion_steps - 1 - self.start_step],
                callback_ddim_timesteps=self.save_feature_timesteps,
                img_callback=self.ddim_sampler_callback,
            )
            sty_feat = copy.deepcopy(self.feat_maps)
            sty_z_enc = self.feat_maps[0]["z_enc"]

        if len(feat_path_root) > 0:
            print("Save features")
            if not os.path.isfile(sty_feat_name):
                with open(sty_feat_name, "wb") as h:
                    pickle.dump(sty_feat, h)

        self.sty_feat = sty_feat

        super().__init__(resolution)

    def style(self, camera_views: torch.Tensor) -> torch.Tensor:
        # sty_z_enc = self._sty_z_enc
        # model = self._model
        init_cnt = camera_views[0].unsqueeze(0)
        # ddim_inversion_steps = self._ddim_inversion_steps
        # save_feature_timesteps = self._save_feature_timesteps
        # start_step = self._start_step

        init_cnt = self.model.get_first_stage_encoding(self.model.encode_first_stage(init_cnt))
        B = camera_views.shape[0]
        # cnt_z_enc_layers = []
        # for b in range(B):
        #     cnt_z_enc, z = self.sampler.encode_ddim(init_cnt[b].clone()[torch.newaxis,:,:,:], num_steps=self.ddim_inversion_steps, unconditional_conditioning=self.uc, \
        #                                     end_step=self.time_idx_dict[self.ddim_inversion_steps-1-self.start_step], \
        #                                     callback_ddim_timesteps=self.save_feature_timesteps,
        #                                     img_callback=self.ddim_sampler_callback)
        #     cnt_z_enc_layers.append(cnt_z_enc)
        #     print(cnt_z_enc.shape)
        # cnt_z_enc = torch.cat(cnt_z_enc_layers, dim=0)
        # print("hello", cnt_z_enc.shape)
        cnt_z_enc, _ = self.sampler.encode_ddim(
            init_cnt.clone(),
            num_steps=self.ddim_inversion_steps,
            unconditional_conditioning=self.uc,
            end_step=self.time_idx_dict[self.ddim_inversion_steps - 1 - self.start_step],
            callback_ddim_timesteps=self.save_feature_timesteps,
            img_callback=self.ddim_sampler_callback,
        )

        cnt_feat = copy.deepcopy(self.feat_maps)
        cnt_z_enc = self.feat_maps[0]["z_enc"]

        # print(cnt_feat)
        # print(self.sty_feat)

        with torch.no_grad():
            with self.precision_scope("mps"):
                with self.model.ema_scope():
                    # inversion
                    # output_name = f"{os.path.basename(cnt_name).split('.')[0]}_stylized_{os.path.basename(sty_name).split('.')[0]}.png"

                    # print(f"Inversion end: {time.time() - begin}")
                    # if opt.without_init_adain:
                    #     adain_z_enc = cnt_z_enc
                    # else:
                    #     adain_z_enc = adain(cnt_z_enc, sty_z_enc)
                    adain_z_enc = cnt_z_enc
                    # print(cnt_feat, self.sty_feat)
                    self.feat_maps = self.feat_merge(
                        self.gamma,
                        self.T,
                        cnt_feat,
                        self.sty_feat,
                        start_step=self.start_step,
                    )

                    # if opt.without_attn_injection:
                    #     feat_maps = None

                    # inference
                    print(self.feat_maps)
                    samples_ddim, intermediates = self.sampler.sample(
                        S=self.ddim_steps,
                        batch_size=1,
                        shape=self.shape,
                        verbose=False,
                        unconditional_conditioning=self.uc,
                        eta=self.ddim_eta,
                        x_T=adain_z_enc,
                        injected_features=self.feat_maps,
                        start_step=self.start_step,
                    )

                    x_samples_ddim = self.model.decode_first_stage(samples_ddim)
                    x_samples_ddim = torch.clamp((x_samples_ddim + 1.0) / 2.0, min=0.0, max=1.0)
                    x_samples_ddim = x_samples_ddim.cpu().permute(0, 2, 3, 1).numpy()
                    x_image_torch = torch.from_numpy(x_samples_ddim).permute(0, 3, 1, 2)
                    # x_sample = 255. * rearrange(x_image_torch[0].cpu().numpy(), 'c h w -> h w c')
                    # img = Image.fromarray(x_sample.astype(np.uint8))

                    # img.save(os.path.join(output_path, output_name))
                    style_mask = camera_views.cpu() < (1.0 - 1e-6)
                    return x_image_torch * style_mask + (1 - style_mask.to(torch.float32))

    def ddim_sampler_callback(self, pred_x0, xt, i):
        self.save_feature_maps_callback(i)
        self.save_feature_map(xt, "z_enc", i)
        # print("xt", xt.shape)

    def save_feature_maps(self, blocks, i, feature_type="input_block"):
        block_idx = 0
        for block_idx, block in enumerate(blocks):
            if len(block) > 1 and "SpatialTransformer" in str(type(block[1])):
                if block_idx in self.self_attn_output_block_indices:
                    # self-attn
                    q = block[1].transformer_blocks[0].attn1.q
                    k = block[1].transformer_blocks[0].attn1.k
                    v = block[1].transformer_blocks[0].attn1.v
                    self.save_feature_map(q, f"{feature_type}_{block_idx}_self_attn_q", i)
                    self.save_feature_map(k, f"{feature_type}_{block_idx}_self_attn_k", i)
                    self.save_feature_map(v, f"{feature_type}_{block_idx}_self_attn_v", i)
            block_idx += 1

    def save_feature_maps_callback(self, i):
        self.save_feature_maps(self.unet_model.output_blocks, i, "output_block")

    def save_feature_map(self, feature_map, filename, time):
        # global feat_maps
        cur_idx = self.idx_time_dict[time]
        self.feat_maps[cur_idx][f"{filename}"] = feature_map

    @staticmethod
    def feat_merge(gamma, T, cnt_feats, sty_feats, start_step=0):
        feat_maps = [
            {
                "config": {
                    "gamma": gamma,
                    "T": T,
                    "timestep": _,
                }
            }
            for _ in range(50)
        ]

        for i in range(len(feat_maps)):
            if i < (50 - start_step):
                continue
            cnt_feat = cnt_feats[i]
            sty_feat = sty_feats[i]
            ori_keys = sty_feat.keys()

            for ori_key in ori_keys:
                if ori_key[-1] == "q":
                    feat_maps[i][ori_key] = cnt_feat[ori_key]
                if ori_key[-1] == "k" or ori_key[-1] == "v":
                    feat_maps[i][ori_key] = sty_feat[ori_key]
        return feat_maps
