import math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,25
FD='/home/user/explainer-video-releases/docs/fonts/'
BG=(9,12,26); NAVY=(16,22,48); WHITE=(255,255,255); YEL=(255,211,77)
CYAN=(57,213,255); GREEN=(77,255,166); CORAL=(255,94,126); ORANGE=(255,160,60)
INK=(6,8,16); EDIT=(13,17,23)
_fc={}
def font(kind,size):
    k=(kind,int(size))
    if k in _fc: return _fc[k]
    if kind=='disp': f=ImageFont.truetype(FD+'FiraSansExtraCondensed-Black.ttf',int(size))
    elif kind=='dispb': f=ImageFont.truetype(FD+'FiraSansExtraCondensed-ExtraBold.ttf',int(size))
    elif kind=='mono':
        f=ImageFont.truetype(FD+'JetBrainsMono-VariableFont_wght.ttf',int(size))
        try: f.set_variation_by_axes([700])
        except Exception: pass
    elif kind=='monor':
        f=ImageFont.truetype(FD+'JetBrainsMono-VariableFont_wght.ttf',int(size))
        try: f.set_variation_by_axes([500])
        except Exception: pass
    elif kind=='tek':
        f=ImageFont.truetype(FD+'Tektur-VariableFont_wdth,wght.ttf',int(size))
        try: f.set_variation_by_axes([100,800])
        except Exception: pass
    else:
        f=ImageFont.truetype(FD+'Inter-VariableFont_opsz,wght.ttf',int(size))
        try: f.set_variation_by_axes([28,800])
        except Exception: pass
    _fc[k]=f; return f
def clamp(x,a=0.,b=1.): return max(a,min(b,x))
def eo(x): x=clamp(x); return 1-(1-x)**3
def ei(x): x=clamp(x); return x**3
def eio(x): x=clamp(x); return 3*x*x-2*x**3
def eob(x,s=1.4): x=clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def prog(t,t0,d): return clamp((t-t0)/d) if d>0 else float(t>=t0)
def lerp(a,b,p): return a+(b-a)*p
def mixc(a,b,p): return tuple(int(round(a[i]+(b[i]-a[i])*p)) for i in range(3))
def comp(base,layer,xy,alpha=1.0):
    if alpha<=0.003: return
    x,y=int(round(xy[0])),int(round(xy[1])); lw,lh=layer.size
    if x>=base.width or y>=base.height or x+lw<=0 or y+lh<=0: return
    if alpha<1:
        layer=layer.copy(); layer.putalpha(layer.getchannel('A').point(lambda v:int(v*alpha)))
    sx0=max(0,-x); sy0=max(0,-y); sx1=min(lw,base.width-x); sy1=min(lh,base.height-y)
    if sx0 or sy0 or sx1<lw or sy1<lh: layer=layer.crop((sx0,sy0,sx1,sy1))
    base.alpha_composite(layer,(x+sx0,y+sy0))
def text_layer(s,size,kind='disp',fill=WHITE,stroke=0,sfill=INK,shadow=True):
    f=font(kind,size); asc,desc=f.getmetrics(); tw=int(math.ceil(f.getlength(s)))
    pad=stroke+28
    lay=Image.new('RGBA',(tw+2*pad,asc+desc+2*pad),(0,0,0,0)); d=ImageDraw.Draw(lay)
    if shadow:
        sh=Image.new('RGBA',lay.size,(0,0,0,0)); ImageDraw.Draw(sh).text((pad,pad+6),s,font=f,fill=(0,0,0,200),stroke_width=stroke+4,stroke_fill=(0,0,0,200))
        lay=Image.alpha_composite(lay,sh.filter(ImageFilter.GaussianBlur(10))); d=ImageDraw.Draw(lay)
    d.text((pad,pad),s,font=f,fill=fill+(255,) if len(fill)==3 else fill,stroke_width=stroke,stroke_fill=sfill+(255,))
    return lay,pad
def txt(base,s,cx,cy,size,kind='disp',fill=WHITE,stroke=0,alpha=1,scale=1,anchor='mm',shadow=True,rot=0):
    lay,pad=text_layer(s,size,kind,fill,stroke,shadow=shadow)
    if scale!=1: lay=lay.resize((max(1,int(lay.width*scale)),max(1,int(lay.height*scale))),Image.BICUBIC)
    if rot: lay=lay.rotate(rot,resample=Image.BICUBIC,expand=True)
    lw,lh=lay.size
    if anchor=='mm': xy=(cx-lw/2,cy-lh/2)
    elif anchor=='lm': xy=(cx-pad*scale,cy-lh/2)
    else: xy=(cx-lw+pad*scale,cy-lh/2)
    comp(base,lay,xy,alpha)
def rrect_mask(w,h,r,ss=3):
    m=Image.new('L',(w*ss,h*ss),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w*ss-1,h*ss-1),r*ss,fill=255)
    return m.resize((w,h),Image.LANCZOS)
def glow(layer,r,a=1.0):
    g=layer.filter(ImageFilter.GaussianBlur(r))
    if a!=1: g.putalpha(g.getchannel('A').point(lambda v:min(255,int(v*a))))
    return g
def vignette(img,strength=0.55):
    yy,xx=np.mgrid[0:H,0:W]; d=np.sqrt(((xx-W/2)/(W*0.62))**2+((yy-H/2)/(H*0.6))**2)
    v=np.clip((d-0.55)/0.6,0,1)**1.6*strength
    a=(v*255).astype(np.uint8); lay=Image.new('RGBA',(W,H),(0,0,0,255)); lay.putalpha(Image.fromarray(a))
    return lay
