import math, numpy as np, os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
W,H,FPS=1080,1920,25
VOID=(14,15,18); BURG=(55,19,44); PURP=(79,38,88); VIOL=(108,61,138); LILAC=(150,106,169)
MAG=(169,52,93); PINK=(213,148,217); HI=(243,226,244); RED=(230,57,70); GOLD=(228,179,90)
FD='/usr/share/fonts/truetype/sand-box/google/'
_fc={}
def font(kind,size):
    k=(kind,size)
    if k in _fc: return _fc[k]
    if kind=='disp': f=ImageFont.truetype(FD+'Fira Sans Extra Condensed/FiraSansExtraCondensed-Black.ttf',size)
    elif kind=='dispb': f=ImageFont.truetype(FD+'Fira Sans Extra Condensed/FiraSansExtraCondensed-ExtraBold.ttf',size)
    elif kind=='tek':
        f=ImageFont.truetype(FD+'Tektur/Tektur-VariableFont_wdth,wght.ttf',size)
        try: f.set_variation_by_axes([100,850])
        except Exception as e: print('tek axes',e)
    elif kind=='tekm':
        f=ImageFont.truetype(FD+'Tektur/Tektur-VariableFont_wdth,wght.ttf',size)
        try: f.set_variation_by_axes([100,600])
        except Exception: pass
    elif kind=='mono':
        f=ImageFont.truetype(FD+'JetBrains Mono/JetBrainsMono-VariableFont_wght.ttf',size)
        try: f.set_variation_by_axes([700])
        except Exception: pass
    else:
        f=ImageFont.truetype(FD+'Inter/Inter-VariableFont_opsz,wght.ttf',size)
        try: f.set_variation_by_axes([28,800])
        except Exception: pass
    _fc[k]=f; return f
def clamp(x,a=0,b=1): return max(a,min(b,x))
def eo(x): x=clamp(x); return 1-(1-x)**3
def eio(x): x=clamp(x); return 3*x*x-2*x**3
def eob(x,s=1.6):
    x=clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def prog(t,t0,d): return clamp((t-t0)/d)
def mix(a,b,p): return tuple(int(a[i]+(b[i]-a[i])*p) for i in range(3))
def comp(base,layer,xy,alpha=1.0):
    """alpha-composite RGBA layer onto RGBA/RGB base at top-left xy (handles clipping)"""
    if alpha<=0: return
    x,y=int(round(xy[0])),int(round(xy[1]))
    lw,lh=layer.size
    if x>=base.width or y>=base.height or x+lw<=0 or y+lh<=0: return
    if alpha<1:
        a=layer.getchannel('A').point(lambda v:int(v*alpha)); layer=layer.copy(); layer.putalpha(a)
    sx0=max(0,-x); sy0=max(0,-y); sx1=min(lw,base.width-x); sy1=min(lh,base.height-y)
    if sx0>0 or sy0>0 or sx1<lw or sy1<lh: layer=layer.crop((sx0,sy0,sx1,sy1))
    x+=sx0; y+=sy0
    if base.mode=='RGBA': base.alpha_composite(layer,(x,y))
    else: base.paste(layer,(x,y),layer)
def txt(base,s,cx,cy,size,kind='disp',fill=HI,alpha=1,scale=1,rot=0,stroke=0,sfill=VOID,glow=None,gr=24,ga=0.7,anchor='mm',sp=0,outline_only=False):
    f=font(kind,int(size))
    # measure
    if sp:
        widths=[f.getlength(c) for c in s]; tw=int(sum(widths)+sp*(len(s)-1))
    else: tw=int(f.getlength(s))
    asc,desc=f.getmetrics(); th=asc+desc
    pad=int(stroke+gr*2+8) if glow else int(stroke+8)
    lay=Image.new('RGBA',(tw+pad*2,th+pad*2),(0,0,0,0)); d=ImageDraw.Draw(lay)
    fl=fill+(255,) if len(fill)==3 else fill
    if outline_only:
        d.text((pad,pad),s,font=f,fill=(0,0,0,0),stroke_width=stroke,stroke_fill=fl) if sp==0 else None
    elif sp:
        x=pad
        for c,w in zip(s,widths):
            d.text((x,pad),c,font=f,fill=fl,stroke_width=stroke,stroke_fill=sfill+(255,)); x+=w+sp
    else:
        d.text((pad,pad),s,font=f,fill=fl,stroke_width=stroke,stroke_fill=sfill+(255,))
    if glow:
        g=Image.new('RGBA',lay.size,(0,0,0,0)); gd=ImageDraw.Draw(g)
        gd.text((pad,pad),s,font=f,fill=glow+(255,),stroke_width=max(stroke,2))
        g=g.filter(ImageFilter.GaussianBlur(gr)); a=g.getchannel('A').point(lambda v:min(255,int(v*ga*1.6))); g.putalpha(a)
        lay=Image.alpha_composite(g,lay)
    if scale!=1: lay=lay.resize((max(1,int(lay.width*scale)),max(1,int(lay.height*scale))),Image.BICUBIC)
    if rot: lay=lay.rotate(rot,resample=Image.BICUBIC,expand=True)
    lw,lh=lay.size
    if anchor=='mm': xy=(cx-lw/2,cy-lh/2)
    elif anchor=='lm': xy=(cx-pad*scale,cy-lh/2)
    elif anchor=='rm': xy=(cx-lw+pad*scale,cy-lh/2)
    comp(base,lay,xy,alpha)
    return tw
def tw_of(s,kind,size): return font(kind,int(size)).getlength(s)
def rrect(base,box,r=20,fill=None,outline=None,width=3,alpha=1.0):
    x0,y0,x1,y1=[int(v) for v in box]; w,h=x1-x0+1,y1-y0+1
    if w<2 or h<2: return
    lay=Image.new('RGBA',(w+2,h+2),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((0,0,w,h),r,fill=(fill if fill is None or len(fill)==4 else fill+(255,)),outline=(outline+(255,) if outline else None),width=width)
    comp(base,lay,(x0,y0),alpha)
def glowrect(base,box,col,gr=28,ga=0.6,r=20,width=4):
    x0,y0,x1,y1=[int(v) for v in box]; pad=gr*3
    lay=Image.new('RGBA',(x1-x0+pad*2,y1-y0+pad*2),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((pad,pad,pad+x1-x0,pad+y1-y0),r,outline=col+(255,),width=width+4)
    lay=lay.filter(ImageFilter.GaussianBlur(gr)); a=lay.getchannel('A').point(lambda v:min(255,int(v*ga*2.2))); lay.putalpha(a)
    comp(base,lay,(x0-pad,y0-pad))
def line(base,p0,p1,col,width=3,alpha=1.0):
    x0=int(min(p0[0],p1[0]))-width-2; y0=int(min(p0[1],p1[1]))-width-2
    x1=int(max(p0[0],p1[0]))+width+2; y1=int(max(p0[1],p1[1]))+width+2
    lay=Image.new('RGBA',(x1-x0,y1-y0),(0,0,0,0)); ImageDraw.Draw(lay).line([(p0[0]-x0,p0[1]-y0),(p1[0]-x0,p1[1]-y0)],fill=col+(255,),width=width)
    comp(base,lay,(x0,y0),alpha)
def poly_layer(base,pts,col,alpha=1.0,outline=None,width=3):
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]; x0=int(min(xs))-width-2; y0=int(min(ys))-width-2
    lay=Image.new('RGBA',(int(max(xs))-x0+width+4,int(max(ys))-y0+width+4),(0,0,0,0)); d=ImageDraw.Draw(lay)
    q=[(p[0]-x0,p[1]-y0) for p in pts]
    d.polygon(q,fill=(col+(255,) if col else None),outline=(outline+(255,) if outline else None))
    if outline and width>1: d.line(q+[q[0]],fill=outline+(255,),width=width)
    comp(base,lay,(x0,y0),alpha)
def bracket(base,box,col,L=60,w=6,alpha=1.0):
    x0,y0,x1,y1=box
    for (px,py,dx,dy) in [(x0,y0,1,1),(x1,y0,-1,1),(x0,y1,1,-1),(x1,y1,-1,-1)]:
        line(base,(px,py),(px+dx*L,py),col,w,alpha); line(base,(px,py),(px,py+dy*L),col,w,alpha)
def stamp(base,s,cx,cy,t,t0,col=RED,size=150,rot=-8,sub=None,alpha=1.0,hold=True):
    p=t-t0
    if p<0: return
    a=eo(p/0.08); sc=1+0.9*(1-eob(p/0.22,1.2)) if p<0.22 else 1
    kind='disp'; tw=tw_of(s,kind,size)
    lay=Image.new('RGBA',(int(tw+120),int(size*1.35+(50 if sub else 0))),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((6,6,lay.width-7,lay.height-7),14,outline=col+(255,),width=10)
    d.rounded_rectangle((22,22,lay.width-23,lay.height-23),8,outline=col+(255,),width=3)
    f=font(kind,size); d.text((lay.width/2,(size*1.35)/2+4),s,font=f,fill=col+(255,),anchor='mm')
    if sub: d.text((lay.width/2,size*1.35-4),sub,font=font('mono',26),fill=col+(255,),anchor='mm')
    # distress: knock out specks
    rng=np.random.RandomState(7); arr=np.array(lay)
    m=rng.rand(*arr.shape[:2])<0.06; arr[...,3]=np.where(m,(arr[...,3]*0.25).astype(np.uint8),arr[...,3]); lay=Image.fromarray(arr)
    if sc!=1: lay=lay.resize((int(lay.width*sc),int(lay.height*sc)),Image.BICUBIC)
    lay=lay.rotate(rot,resample=Image.BICUBIC,expand=True)
    comp(base,lay,(cx-lay.width/2,cy-lay.height/2),alpha*a*0.96)
    # impact shake offset returned
def shake(t,t0,amp=14,dur=0.28):
    p=t-t0
    if p<0 or p>dur: return (0,0)
    k=(1-p/dur)**2*amp
    return (math.sin(p*95)*k, math.cos(p*80)*k*0.6)
