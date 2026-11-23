# line-art («SVG trace») of an image, done in numpy: Sobel edges -> thin cyan strokes
import numpy as np
from PIL import Image, ImageFilter
def lineart(img,col=(57,213,255),thr=40,blur=1.2):
    g=img.convert('L').filter(ImageFilter.GaussianBlur(blur)); a=np.asarray(g).astype(np.float32)
    gx=np.zeros_like(a); gy=np.zeros_like(a)
    gx[:,1:-1]=a[:,2:]-a[:,:-2]; gy[1:-1,:]=a[2:,:]-a[:-2,:]
    m=np.sqrt(gx*gx+gy*gy); m=np.clip((m-thr)/(thr*1.5),0,1)
    out=np.zeros(a.shape+(4,),np.uint8); out[...,:3]=col; out[...,3]=(m*255).astype(np.uint8)
    return Image.fromarray(out,'RGBA')
