import torch
import numpy as np
import slangpy as spy

from glm import mat4, vec4
from cs248a_renderer import setup_device, RendererModules
from cs248a_renderer.model.volumes import DenseVolume
from cs248a_renderer.model.transforms import Transform3D
from cs248a_renderer.renderer.core_renderer import Renderer, RendererModules

slang_device = setup_device([])
renderer_modules = RendererModules(slang_device)


def make_dense_volume(
    volume_tensor, voxel_size: float, transform: Transform3D | None = None
) -> DenseVolume:
    if transform is None:
        transform = Transform3D()

    return DenseVolume(
        name="volume",
        # transform=Transform3D(rotation=glm.quatLookAt((0, -1, 0), (0, 0, 1))),
        transform=transform,
        data=volume_tensor.detach().numpy().astype(np.float32),
        properties={
            "pivot": (0.5, 0.5, 0.5),
            "voxel_size": voxel_size,
            # "voxel_size": dataset.voxel_size,
            # "voxel_size": 0.03,
        },
    )


class DiffRenderer:
    renderer: Renderer
    image: spy.Texture

    def __init__(self, resolution: tuple[int, int]) -> None:
        self.image = slang_device.create_texture(
            type=spy.TextureType.texture_2d,
            format=spy.Format.r32_float,
            usage=spy.TextureUsage.unordered_access,
            width=resolution[0],
            height=resolution[1],
        )
        self.renderer = Renderer(
            device=slang_device, render_texture=self.image, render_modules=renderer_modules
        )
        self.renderer.sqrt_spp = 1
        self.renderer._ambientColor = vec4(1.0, 1.0, 1.0, 1.0)

    def set_volume(
        self, volume_tensor: torch.Tensor, voxel_size: float, transform: Transform3D | None = None
    ):
        with torch.no_grad():
            dense_volume = make_dense_volume(volume_tensor, voxel_size, transform)
            self.renderer.load_volume(dense_volume)


class DiffRenderFunction(torch.autograd.Function):
    @staticmethod
    def forward(
        ctx,
        input_tensor: torch.Tensor,
        diffrenderer: DiffRenderer,
        view_mat: mat4,
        fov: float,
    ):
        ctx.save_for_backward(input_tensor)
        ctx.diffrenderer = diffrenderer
        ctx.view_mat = view_mat
        ctx.fov = fov

        diffrenderer.renderer.render(view_mat, fov)
        return torch.tensor(np.flipud(diffrenderer.image.to_numpy()).copy())

    @staticmethod
    def backward(ctx, *grad_outputs):
        (input_tensor,) = ctx.saved_tensors
        image_grad, *_ = grad_outputs

        ctx.diffrenderer.renderer.render_volume_backward(
            view_mat=ctx.view_mat, fov=ctx.fov, out_grad=torch.flipud(image_grad)
        )
        d_volume = torch.tensor(
            ctx.diffrenderer.renderer.get_d_volume().reshape(input_tensor.shape)
        )

        # if torch.isnan(d_volume).any():
        #     print(f"NaN detected in d_volume! Setting to zero.")
        #     d_volume = torch.nan_to_num(d_volume, nan=0.0)

        return (
            d_volume,
            None,
            None,
            None,
        )
