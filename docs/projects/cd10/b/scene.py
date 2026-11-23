# The «night mountains + moon» artwork, drawn from geometry (vector) at any zoom.
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
MOON=(690,260); MR=120
SKY0=(8,12,38); SKY1=(70,40,118); LAKE0=(22,18,52); LAKE1=(5,6,18)
RIDGE_COL=[(58,44,110),(36,28,78),(18,14,44)]
def ridge(xs,layer,variant):
    rng=np.random.RandomState(11+layer*7+variant*101)
    base=[470,560,630][layer]; amp=[95,80,70][layer]
    y=np.full_like(xs,base,dtype=float)
    for k in range(5):
        f=rng.uniform(0.004,0.02)*(1+k*0.6); ph=rng.uniform(0,6.28); a=amp/(1+k*0.9)*rng.uniform(0.6,1.2)
        y-=a*np.abs(np.sin(xs*f+ph))**(1.3 if k==0 else 1)
    return y
_rng=np.random.RandomState(5)
STARS=[(_rng.uniform(0,1000),_rng.uniform(0,520)**1.0,_rng.uniform(1.2,3.6),_rng.uniform(0,6.28),_rng.uniform(1.5,4)) for _ in range(150)]
CRATERS=[(-40,-30,26),(35,20,18),(-10,55,14),(50,-50,12),(-60,30,10)]
def render(ow,oh,view=(500,500,1.0),variant=0,moon_col=(255,211,77),t=None,ss=2,layers=('sky','stars','moon','ridges','lake'),rise=0.0):
    cx,cy,sc=view; S=sc*ss; W2,H2=ow*ss,oh*ss
    def P(x,y): return ((x-cx)*S+W2/2,(y-cy)*S+H2/2)
    img=Image.new('RGBA',(W2,H2),(0,0,0,0))
    if 'sky' in layers:
        rows=np.arange(H2); wy=(rows-H2/2)/S+cy
        p=np.clip(wy/700,0,1)[:,None]; q=np.clip((wy-700)/300,0,1)[:,None]
        sky=np.array(SKY0)*(1-p)+np.array(SKY1)*p
        lake=np.array(LAKE0)*(1-q)+np.array(LAKE1)*q
        col=np.where(wy[:,None]<700,sky,lake)
        arr=np.repeat(col[:,None,:],W2,axis=1).astype(np.uint8)
        img=Image.fromarray(np.dstack([arr,np.full((H2,W2,1),255,np.uint8)]).astype(np.uint8),'RGBA')
    d=ImageDraw.Draw(img)
    if 'stars' in layers:
        for x,y,r,ph,f in STARS:
            b=1.0 if t is None else 0.55+0.45*math.sin(t*f+ph)
            X,Y=P(x,y); R=max(0.6,r*S*0.5)
            if -10<X<W2+10 and -10<Y<H2+10:
                c=int(150+105*b); d.ellipse((X-R,Y-R,X+R,Y+R),fill=(c,c,min(255,c+20),255))
    my=MOON[1]-rise
    if 'moon' in layers:
        X,Y=P(MOON[0],my); R=MR*S
        g=Image.new('RGBA',(W2,H2),(0,0,0,0)); gd=ImageDraw.Draw(g)
        for k in range(10,0,-1):
            rr=R*(1+k*0.12); a=int(10*(11-k)/10*2.2)
            gd.ellipse((X-rr,Y-rr,X+rr,Y+rr),fill=moon_col+(a,))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(max(2,R*0.15))))
        n=max(64,int(R*0.8)); n=min(n,6000)
        ang=np.linspace(0,2*np.pi,n,endpoint=False); pts=list(zip(X+R*np.cos(ang),Y+R*np.sin(ang)))
        d=ImageDraw.Draw(img); d.polygon(pts,fill=moon_col+(255,))
        dark=tuple(int(c*0.86) for c in moon_col)
        for ox,oy,cr in CRATERS:
            Xc,Yc=P(MOON[0]+ox,my+oy); Rc=cr*S
            if Xc+Rc<0 or Xc-Rc>W2 or Yc+Rc<0 or Yc-Rc>H2: continue
            m=max(32,min(3000,int(Rc*0.8))); a2=np.linspace(0,2*np.pi,m,endpoint=False)
            d.polygon(list(zip(Xc+Rc*np.cos(a2),Yc+Rc*np.sin(a2))),fill=dark+(255,))
    if 'ridges' in layers:
        x0=cx-W2/2/S-20; x1=cx+W2/2/S+20
        xs=np.linspace(x0,x1,max(200,min(4000,int((x1-x0)*S/3))))
        for L in range(3):
            par=0 if t is None else (L+1)*6*math.sin(t*0.7)
            ys=ridge(xs+par,L,variant)
            pts=[P(x,y) for x,y in zip(xs,ys)]+[P(x1,700),P(x0,700)]
            d.polygon(pts,fill=RIDGE_COL[L]+(255,))
    if 'lake' in layers:
        # reflection of moon: shimmering streaks
        X,_=P(MOON[0],0)
        for i in range(14):
            yy=715+i*18; w=(MR*0.9)*(1-i/16)*(0.75+0.25*math.sin(i*1.7+(0 if t is None else t*3)))
            A,B=P(MOON[0]-w,yy); C,D=P(MOON[0]+w,yy+5)
            d.rounded_rectangle((A,B,C,D),radius=max(1,int(2.5*S)),fill=moon_col+(int(170*(1-i/15)),))
        A,B=P(-5000,700); C,D=P(6000,703)
        d.rectangle((A,B,C,D),fill=(120,90,170,120))
    if ss>1: img=img.resize((ow,oh),Image.LANCZOS)
    return img
def raster(variant=0,moon_col=(255,211,77),res=96,seed=3):
    """«neural» output: the same picture as a low-res grid of pixels with painterly jitter"""
    im=render(res,res,(500,500,res/1000),variant,moon_col,ss=4)
    a=np.asarray(im.convert('RGB')).astype(np.float32)
    rng=np.random.RandomState(seed); a+=rng.normal(0,7,a.shape)
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert('RGBA')
def show_raster(r,ow,oh,view=(500,500,1.0),smooth=0.0):
    """display raster r (covering world 0..1000) under a view; nearest-neighbour blocks, optional bilinear blend"""
    cx,cy,sc=view; res=r.width; k=res/1000
    # inverse affine: out pixel -> raster pixel
    a=1/(sc)*k; xo=(cx-ow/2/sc)*k; yo=(cy-oh/2/sc)*k
    nn=r.transform((ow,oh),Image.AFFINE,(a,0,xo,0,a,yo),resample=Image.NEAREST)
    if smooth>0:
        bl=r.transform((ow,oh),Image.AFFINE,(a,0,xo-0.5,0,a,yo-0.5),resample=Image.BILINEAR)
        nn=Image.blend(nn,bl,smooth)
    return nn
