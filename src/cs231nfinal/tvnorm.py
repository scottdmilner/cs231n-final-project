import torch

def tv_volume_loss_anisotropic(x: torch.Tensor):
    diff_x = x[1:,:,:] - x[:-1,:,:]
    diff_y = x[:,1:,:] - x[:,:-1,:]
    diff_z = x[:,:,1:] - x[:,:,:-1]

    tv_x = torch.pow(diff_x, 2).sum()
    tv_y = torch.pow(diff_y, 2).sum()
    tv_z = torch.pow(diff_z, 2).sum()

    return tv_x + tv_y + tv_z

def tv_image_loss_anisotropic(x: torch.Tensor):
    diff_x = x[1:,:] - x[:-1,:]
    diff_y = x[:,1:] - x[:,:-1]

    tv_x = torch.pow(diff_x, 2).sum()
    tv_y = torch.pow(diff_y, 2).sum()

    return tv_x + tv_y
