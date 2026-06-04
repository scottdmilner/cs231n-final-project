"""
Gatys NST Implementation as implemented in 
https://github.com/leongatys/PytorchNeuralStyleTransfer
Collected from notebook form into single Python file, tweaked for modern 
pytorch.
"""

import os 
from pathlib import Path

import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
from torch import optim

from torchvision import transforms

from PIL import Image

MODEL_DIR = Path(__file__).parent / "weights"

#vgg definition that conveniently let's you grab the outputs from any layer
class VGG(nn.Module):
    def __init__(self, pool='max'):
        super(VGG, self).__init__()
        #vgg modules
        self.conv1_1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.conv1_2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.conv2_1 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv2_2 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        self.conv3_1 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.conv3_2 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.conv3_3 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.conv3_4 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
        self.conv4_1 = nn.Conv2d(256, 512, kernel_size=3, padding=1)
        self.conv4_2 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.conv4_3 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.conv4_4 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.conv5_1 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.conv5_2 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.conv5_3 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        self.conv5_4 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
        if pool == 'max':
            self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
            self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
            self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)
            self.pool4 = nn.MaxPool2d(kernel_size=2, stride=2)
            self.pool5 = nn.MaxPool2d(kernel_size=2, stride=2)
        elif pool == 'avg':
            self.pool1 = nn.AvgPool2d(kernel_size=2, stride=2)
            self.pool2 = nn.AvgPool2d(kernel_size=2, stride=2)
            self.pool3 = nn.AvgPool2d(kernel_size=2, stride=2)
            self.pool4 = nn.AvgPool2d(kernel_size=2, stride=2)
            self.pool5 = nn.AvgPool2d(kernel_size=2, stride=2)
            
    def forward(self, x, out_keys):
        out = {}
        out['r11'] = F.relu(self.conv1_1(x))
        out['r12'] = F.relu(self.conv1_2(out['r11']))
        out['p1'] = self.pool1(out['r12'])
        out['r21'] = F.relu(self.conv2_1(out['p1']))
        out['r22'] = F.relu(self.conv2_2(out['r21']))
        out['p2'] = self.pool2(out['r22'])
        out['r31'] = F.relu(self.conv3_1(out['p2']))
        out['r32'] = F.relu(self.conv3_2(out['r31']))
        out['r33'] = F.relu(self.conv3_3(out['r32']))
        out['r34'] = F.relu(self.conv3_4(out['r33']))
        out['p3'] = self.pool3(out['r34'])
        out['r41'] = F.relu(self.conv4_1(out['p3']))
        out['r42'] = F.relu(self.conv4_2(out['r41']))
        out['r43'] = F.relu(self.conv4_3(out['r42']))
        out['r44'] = F.relu(self.conv4_4(out['r43']))
        out['p4'] = self.pool4(out['r44'])
        out['r51'] = F.relu(self.conv5_1(out['p4']))
        out['r52'] = F.relu(self.conv5_2(out['r51']))
        out['r53'] = F.relu(self.conv5_3(out['r52']))
        out['r54'] = F.relu(self.conv5_4(out['r53']))
        out['p5'] = self.pool5(out['r54'])
        return [out[key] for key in out_keys]


# gram matrix and loss
class GramMatrix(nn.Module):
    def forward(self, input):
        b,c,h,w = input.size()
        F = input.view(b, c, h*w)
        G = torch.bmm(F, F.transpose(1,2)) 
        G.div_(h*w)
        return G

class GramMSELoss(nn.Module):
    def forward(self, input, target):
        out = nn.MSELoss()(GramMatrix()(input), target)
        return(out)
    

# pre and post processing for images
# img_size = 512 
# prep = transforms.Compose([transforms.Resize(img_size),
#                            transforms.ToTensor(),
#                            transforms.Lambda(lambda x: x[torch.LongTensor([2,1,0])]), #turn to BGR
#                            transforms.Normalize(mean=[0.40760392, 0.45795686, 0.48501961], #subtract imagenet mean
#                                                 std=[1,1,1]),
#                            transforms.Lambda(lambda x: x.mul_(255)),
#                           ])
postpa = transforms.Compose([transforms.Lambda(lambda x: x.mul_(1./255)),
                           transforms.Normalize(mean=[-0.40760392, -0.45795686, -0.48501961], #add imagenet mean
                                                std=[1,1,1]),
                           transforms.Lambda(lambda x: x[torch.LongTensor([2,1,0])]), #turn to RGB
                           ])
# def postp(tensor): # to clip results in the range [0,1]
#     t = postpa(tensor)
#     t[t>1] = 1    
#     t[t<0] = 0
#     img = postpb(t)
#     return img


class Gatys:

    def prep(self, img: torch.Tensor):
        t = transforms.Compose([
            transforms.Resize(self.size),
            transforms.Lambda(lambda x: x[torch.LongTensor([2,1,0])]), #turn to BGR
            transforms.Normalize(mean=[0.40760392, 0.45795686, 0.48501961], #subtract imagenet mean
                                std=[1,1,1]),
            transforms.Lambda(lambda x: x.mul_(255)),
        ])
        return t(img).unsqueeze(0)
    
    def postp(self, img: torch.Tensor):
        t = postpa(img)
        t[t>1] = 1    
        t[t<0] = 0
        return t
    
    def __init__(self, size, style_img_path: str, device="cpu"):
        self.size = size
        self.device = device
        #get network
        self.vgg = VGG()
        self.vgg.load_state_dict(torch.load(MODEL_DIR / 'vgg_conv.pth'))

        for param in self.vgg.parameters():
            param.requires_grad = False

        self.vgg.to(device)

        self.style_image = self.prep(transforms.ToTensor()(Image.open(style_img_path))).to(self.device)

        #define layers, loss functions, weights and compute optimization targets
        self.style_layers = ['r11','r21','r31','r41', 'r51'] 
        self.content_layers = ['r42']
        self.loss_layers = self.style_layers + self.content_layers
        loss_fns = [GramMSELoss()] * len(self.style_layers) + [nn.MSELoss()] * len(self.content_layers)
        self.loss_fns = [loss_fn.to(self.device) for loss_fn in loss_fns]

        #these are good weights settings:
        style_weights = [1e3/n**2 for n in [64,128,256,512,512]]
        content_weights = [1e0]
        self.weights = style_weights + content_weights

        #compute optimization targets
        self.style_targets = [GramMatrix()(A).detach() for A in self.vgg(self.style_image, self.style_layers)]
    
    def do_style(self, content_img: torch.Tensor, max_iter: int = 500):
        content_image = self.prep(content_img).to(self.device)
        opt_img = Variable(content_image.data.clone(), requires_grad=True)

        content_targets = [A.detach() for A in self.vgg(content_image, self.content_layers)]
        targets = self.style_targets + content_targets

        #run style transfer
        show_iter = 50
        optimizer = optim.LBFGS([opt_img]);
        n_iter=[0]

        while n_iter[0] <= max_iter:

            def closure():
                optimizer.zero_grad()
                out = self.vgg(opt_img, self.loss_layers)
                layer_losses = torch.stack([self.weights[a] * self.loss_fns[a](A, targets[a]) for a,A in enumerate(out)])
                loss = layer_losses.sum()
                loss.backward()
                n_iter[0]+=1

                if n_iter[0]%show_iter == (show_iter-1):
                    print('Iteration: %d, loss: %f'%(n_iter[0]+1, loss.item()))
                return loss
            
            optimizer.step(closure)

        out_img = self.postp(opt_img.detach().data[0].cpu().squeeze())
        return out_img


# def main():
    # #load images, ordered as [style_image, content_image]
    # img_dirs = [image_dir, image_dir]
    # img_names = ['vangogh_starry_night.jpg', 'Tuebingen_Neckarfront.jpg']
    # imgs = [Image.open(img_dirs[i] + name) for i,name in enumerate(img_names)]
    # imgs_torch = [prep(img) for img in imgs]

    # device = torch.device("mps")

    # imgs_torch = [Variable(img.unsqueeze(0).to(device)) for img in imgs_torch]

    # style_image, content_image = imgs_torch

    # # opt_img = Variable(torch.randn(content_image.size()).type_as(content_image.data), requires_grad=True) #random init
    # opt_img = Variable(content_image.data.clone(), requires_grad=True)

    #define layers, loss functions, weights and compute optimization targets
    # style_layers = ['r11','r21','r31','r41', 'r51'] 
    # content_layers = ['r42']
    # loss_layers = style_layers + content_layers
    # loss_fns = [GramMSELoss()] * len(style_layers) + [nn.MSELoss()] * len(content_layers)
    # loss_fns = [loss_fn.to(device) for loss_fn in loss_fns]
        
    # #these are good weights settings:
    # style_weights = [1e3/n**2 for n in [64,128,256,512,512]]
    # content_weights = [1e0]
    # weights = style_weights + content_weights

    # #compute optimization targets
    # style_targets = [GramMatrix()(A).detach() for A in vgg(style_image, style_layers)]
    # content_targets = [A.detach() for A in vgg(content_image, content_layers)]
    # targets = style_targets + content_targets

    # #run style transfer
    # max_iter = 50
    # show_iter = 50
    # optimizer = optim.LBFGS([opt_img]);
    # n_iter=[0]

    # while n_iter[0] <= max_iter:

    #     def closure():
    #         optimizer.zero_grad()
    #         out = vgg(opt_img, loss_layers)
    #         layer_losses = torch.stack([weights[a] * loss_fns[a](A, targets[a]) for a,A in enumerate(out)])
    #         loss = layer_losses.sum()
    #         loss.backward()
    #         n_iter[0]+=1

    #         if n_iter[0]%show_iter == (show_iter-1):
    #             print('Iteration: %d, loss: %f'%(n_iter[0]+1, loss.item()))
    #         return loss
        
    #     optimizer.step(closure)

    # out_img = postp(opt_img.detach().data[0].cpu().squeeze())
    # return out_img
