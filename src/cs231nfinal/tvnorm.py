import torch


def tv_volume_loss_isotropic(x: torch.Tensor, eps=1e-8):
    diff_x = x[1:, :, :] - x[:-1, :, :]
    diff_y = x[:, 1:, :] - x[:, :-1, :]
    diff_z = x[:, :, 1:] - x[:, :, :-1]

    grad_magnitude = torch.stack(
        [
            diff_x[:, 1:, 1:],
            diff_y[1:, :, 1:],
            diff_z[1:, 1:, :],
        ],
        dim=-1,
    )

    return torch.sqrt((grad_magnitude**2).sum(-1) + eps).sum()


def tv_image_loss_isotropic(x: torch.Tensor):
    diff_x = x[1:, :] - x[:-1, :]
    diff_y = x[:, 1:] - x[:, :-1]

    tv_x = torch.pow(diff_x, 2)
    tv_y = torch.pow(diff_y, 2)

    return torch.sqrt(tv_x[:, 1:] + tv_y[1:, :]).sum()
