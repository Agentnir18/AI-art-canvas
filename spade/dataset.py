"""
Copyright (C) 2019 NVIDIA Corporation.  All rights reserved.
Licensed under the CC BY-NC-SA 4.0 license (https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).
"""

import torchvision.transforms as transforms
from PIL import Image

def __scale_width(img, target_width, method=Image.BICUBIC):
  ow, oh = img.size
  if (ow == target_width):
    return img
  w = target_width
  h = int(target_width * oh / ow)
  return img.resize((w, h), method)

def get_transform(opt, method=Image.BICUBIC, normalize=True):
  transform_list = []
  #The first transformation resizes the image to have a width of opt['load_size'], while preserving the aspect ratio
  #of the original image. The resizing method used is specified by the method argument, which defaults to bicubic 
  #interpolation.
  transform_list.append(transforms.Lambda(lambda img: __scale_width(img, opt['load_size'], method)))
  #The second transformation converts the resized image to a PyTorch tensor.
  transform_list += [transforms.ToTensor()]
  #The third transformation normalizes the pixel values of the tensor to have a mean of 0.5 and a standard deviation 
  #of 0.5 for each color channel. This step is optional and can be disabled by setting the normalize argument to False.
  if normalize:
    transform_list += [transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
  
  return transforms.Compose(transform_list)
