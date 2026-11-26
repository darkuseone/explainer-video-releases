# Shared renderer pieces for ai27a / ai27b (AI 2027 shorts). Pillow, 25 fps, 1080x1920.
import os, json, math, subprocess, sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
W,H,FPS=1080,1920,25
FD='/home/user/explainer-video-releases/docs/fonts/'
from PIL import ImageFont
_fc={}
def font(kind,size):
    k=(kind,int(size))
    if k in _fc: return _fc[k]
    if kind=='disp': f=ImageFont.truetype(FD+'FiraSansExtraCondensed-Black.ttf',int(size))
    elif kind=='dispb': f=ImageFont.truetype(FD+'FiraSansExtraCondensed-ExtraBold.ttf',int(size))
    elif kind in ('mono','monor'):
        f=ImageFont.truetype(FD+'JetBrainsMono-VariableFont_wght.ttf',int(size))
        try: f.set_variation_by_axes([700 if kind=='mono' else 500])
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
# palette (brandbook Markus Brown)
VOID=(14,15,18); DARK=(11,15,23); BURG=(55,19,44); PURP=(79,38,88); VIOL=(108,61,138); MAG=(169,52,93)
HI=(243,226,244); RED=(230,57,70); GOLD=(228,179,90); TEAL=(63,206,194); YEL=(255,211,77); WHITE=(255,255,255); INK=(10,8,14)
GREEN=(84,214,140); PAPER=(236,226,214)
def clamp(x,a=0.,b=1.): return max(a,min(b,x))
def eo(x): x=clamp(x); return 1-(1-x)**3
def eio(x): x=clamp(x); return 3*x*x-2*x**3
def eob(x,s=1.4): x=clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def lerp(a,b,p): return a+(b-a)*p
def comp(base,layer,xy,alpha=1.0):
    if alpha<=0.003: return
    x,y=int(round(xy[0])),int(round(xy[1])); lw,lh=layer.size
    if x>=base.width or y>=base.height or x+lw<=0 or y+lh<=0: return
    if alpha<1:
        layer=layer.copy(); layer.putalpha(layer.getchannel('A').point(lambda v:int(v*alpha)))
    sx0=max(0,-x); sy0=max(0,-y); sx1=min(lw,base.width-x); sy1=min(lh,base.height-y)
    if sx0 or sy0 or sx1<lw or sy1<lh: layer=layer.crop((sx0,sy0,sx1,sy1))
    base.alpha_composite(layer,(x+sx0,y+sy0))
def rrect_mask(w,h,r,ss=3):
    m=Image.new('L',(w*ss,h*ss),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w*ss-1,h*ss-1),r*ss,fill=255)
    return m.resize((w,h),Image.LANCZOS)
def text_layer(s,size,kind='disp',fill=WHITE,stroke=0,sfill=INK,shadow=True,glowc=None):
    f=font(kind,size); asc,desc=f.getmetrics(); tw=int(math.ceil(f.getlength(s))); pad=stroke+28
    lay=Image.new('RGBA',(tw+2*pad,asc+desc+2*pad),(0,0,0,0))
    if shadow:
        sh=Image.new('RGBA',lay.size,(0,0,0,0)); ImageDraw.Draw(sh).text((pad,pad+6),s,font=f,fill=(0,0,0,200),stroke_width=stroke+4,stroke_fill=(0,0,0,200))
        lay=Image.alpha_composite(lay,sh.filter(ImageFilter.GaussianBlur(10)))
    if glowc:
        g=Image.new('RGBA',lay.size,(0,0,0,0)); ImageDraw.Draw(g).text((pad,pad),s,font=f,fill=glowc+(255,),stroke_width=stroke+2,stroke_fill=glowc+(255,))
        lay=Image.alpha_composite(lay,g.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(lay).text((pad,pad),s,font=f,fill=fill+(255,),stroke_width=stroke,stroke_fill=sfill+(255,))
    return lay,pad
def fit(s,size,kind,maxw):
    while font(kind,size).getlength(s)>maxw and size>24: size-=2
    return size
def txt(base,s,cx,cy,size,kind='disp',fill=WHITE,stroke=0,alpha=1,scale=1,anchor='mm',glowc=None,maxw=900):
    size=fit(s,size,kind,maxw); lay,pad=text_layer(s,size,kind,fill,stroke,glowc=glowc)
    if scale!=1: lay=lay.resize((max(1,int(lay.width*scale)),max(1,int(lay.height*scale))),Image.BICUBIC)
    lw,lh=lay.size
    xy=(cx-lw/2,cy-lh/2) if anchor=='mm' else ((cx-pad*scale,cy-lh/2) if anchor=='lm' else (cx-lw+pad*scale,cy-lh/2))
    comp(base,lay,xy,alpha)
def chip(base,s,cx,cy,col=GOLD,size=44,alpha=1.0,fill=(12,10,20,232),tc=None,scale=1.0,kind='disp'):
    size=fit(s,size,kind,700); f=font(kind,size); tw=f.getlength(s); asc,desc=f.getmetrics(); h=asc+desc+36; w=int(tw+64)
    L=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle((1,1,w-2,h-2),h//2,fill=fill,outline=col+(255,),width=4); d.text((w/2,h/2),s,font=f,fill=(tc or col)+(255,),anchor='mm')
    if scale!=1: L=L.resize((max(1,int(w*scale)),max(1,int(h*scale))),Image.BICUBIC)
    comp(base,L,(cx-L.width/2,cy-L.height/2),alpha)
def stamp(base,s,cx,cy,col=RED,size=90,alpha=1.0,rot=-6,scale=1.0):
    size=fit(s,size,'disp',760); f=font('disp',size); tw=f.getlength(s); asc,desc=f.getmetrics(); w=int(tw+70); h=asc+desc+40
    L=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle((4,4,w-5,h-5),14,outline=col+(255,),width=10); d.rounded_rectangle((16,16,w-17,h-17),8,outline=col+(255,),width=3)
    d.text((w/2,h/2),s,font=f,fill=col+(255,),anchor='mm')
    a=np.array(L); rng=np.random.default_rng(7); m=rng.random(a.shape[:2])<0.06; a[m,3]=(a[m,3]*0.25).astype(np.uint8); L=Image.fromarray(a)
    if scale!=1: L=L.resize((max(1,int(w*scale)),max(1,int(h*scale))),Image.BICUBIC)
    L=L.rotate(rot,resample=Image.BICUBIC,expand=True); comp(base,L,(cx-L.width/2,cy-L.height/2),alpha)
def flash(base,t,t0,dur=0.14,a=0.8,col=(255,244,246)):
    p=(t-t0)/dur
    if 0<=p<1: base.alpha_composite(Image.new('RGBA',(W,H),col+(int(255*a*(1-p)),)))
def darken(base,a,col=(6,6,12)):
    if a>0: base.alpha_composite(Image.new('RGBA',(W,H),col+(int(255*a),)))
def glitch(base,t,t0,n=3):
    f=int(round((t-t0)*FPS))
    if 0<=f<n:
        a=np.array(base); rng=np.random.default_rng(f+11)
        a[...,0]=np.roll(a[...,0],14,1); a[...,2]=np.roll(a[...,2],-14,1)
        for _ in range(7):
            y=int(rng.integers(0,H-60)); h=int(rng.integers(10,60)); a[y:y+h]=np.roll(a[y:y+h],int(rng.integers(-90,90)),1)
        base.paste(Image.fromarray(a))
# ---------------- vignette & background ----------------
def make_vig(strength=0.6):
    yy,xx=np.mgrid[0:H,0:W]; d=np.sqrt(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.72))**2)
    v=np.clip((d-0.55)/0.6,0,1)**1.5*strength; L=Image.new('RGBA',(W,H),(0,0,0,255)); L.putalpha(Image.fromarray((v*200).astype(np.uint8))); return L
VIG=make_vig(0.85)
_bg=None
def bg_void(t,tint=None):
    global _bg
    if _bg is None:
        yy=np.linspace(0,1,H)[:,None]; c0=np.array(DARK); c1=np.array((24,14,30))
        _bg=Image.fromarray((c0*(1-yy)+c1*yy)[:,None,:].repeat(W,1).astype(np.uint8)).convert('RGBA')
    b=_bg.copy(); d=ImageDraw.Draw(b); off=(t*25)%120
    for x in range(-120,W+120,120): d.line((x+off,0,x+off,H),fill=(28,24,36,255),width=1)
    for y in range(-120,H+120,120): d.line((0,y+off,W,y+off),fill=(28,24,36,255),width=1)
    if tint: b.alpha_composite(Image.new('RGBA',(W,H),tint))
    return b
# ---------------- project context ----------------
class Ctx:
    def __init__(self,root,cover_frames=3,lag=0.02,acrop=(130,220,950,1040)):
        self.root=root; P=lambda *a: os.path.join(root,*a); self.P=P
        tl=json.load(open(P('timeline.json'))); self.PH=tl['phrases']; self.WD=tl['words']; self.TOT=tl['tot']
        self.AVM=json.load(open(P('..','v','av_meta.json'))); self.AVN=len(os.listdir(P('av'))); self.LAG=lag; self.ACROP=acrop
        self.SHN=json.load(open(P('shots','meta.json'))); self.WEB=json.load(open(P('web','meta.json')))
        self.COVER=cover_frames; self.NF=cover_frames+int(round(self.TOT*FPS))
        self._fc={}; self._avc={}; self._web={}; self._mask={}
    def wt(self,word,k=0,end=False):
        n=0
        for w in self.WD:
            if w[2].lower().strip('.,!?…—:«»').startswith(word.lower()):
                if n==k: return w[1] if end else w[0]
                n+=1
        raise KeyError(word)
    def pt(self,i,k=0): return self.PH[i][k]
    # footage
    def shot(self,name,lt):
        n=self.SHN[name]; i=int(lt*FPS); i=i%(2*n-2) if n>1 else 0
        if i>=n: i=2*n-2-i
        fn=self.P('shots',name,f'f{i+1:04d}.jpg')
        if fn not in self._fc:
            if len(self._fc)>40: self._fc.clear()
            self._fc[fn]=Image.open(fn).convert('RGBA')
        return self._fc[fn]
    def vfill(self,name,t,t0,z0=1.0,z1=1.08,cx=0.5,cy=0.5,dur=4.0):
        return kb(self.shot(name,t-t0),lerp(z0,z1,eio((t-t0)/dur)),cx,cy)
    # avatar
    def av_frame(self,t):
        for s in self.AVM:
            if s['t0']-0.6<=t<=s['t1']+0.6:
                i=int(math.floor((t-s['t0']+s['src0']+self.LAG)*FPS+1e-6))+1; i=max(1,min(self.AVN,i)); fn=self.P('av',f'f{i:04d}.jpg')
                if fn not in self._avc:
                    if len(self._avc)>30: self._avc.clear()
                    self._avc[fn]=Image.open(fn).convert('RGBA')
                return self._avc[fn]
        return None
    def cmask(self,d):
        if d not in self._mask:
            m=Image.new('L',(d*3,d*3),0); ImageDraw.Draw(m).ellipse((0,0,d*3-1,d*3-1),fill=255); self._mask[d]=m.resize((d,d),Image.LANCZOS)
        return self._mask[d]
    def avatar(self,base,t,cx,cy,D,alpha=1.0,ring=RED,amp=0.0):
        fr=self.av_frame(t)
        if fr is None or D<8: return
        D=int(D); c=fr.crop(self.ACROP).resize((D,D),Image.BICUBIC)
        out=Image.new('RGBA',(D,D),(0,0,0,0)); out.paste(c,(0,0),self.cmask(D))
        pad=int(D*0.24); L=Image.new('RGBA',(D+2*pad,D+2*pad),(0,0,0,0)); d=ImageDraw.Draw(L)
        bw=max(4,int((12+7*amp)*D/640)); d.ellipse((pad-bw,pad-bw,pad+D+bw,pad+D+bw),outline=ring+(255,),width=bw*2)
        gl=L.filter(ImageFilter.GaussianBlur(max(6,int(20*D/640)))); L=Image.alpha_composite(gl,L); L=Image.alpha_composite(L,gl)
        d=ImageDraw.Draw(L); c0=pad+D/2
        for (rk,sp,ln,wd,col) in ((1.15,60,110,7,MAG),(1.21,-45,70,4,GOLD)):
            r=D/2*rk; a0=(t*sp)%360; d.arc((c0-r,c0-r,c0+r,c0+r),a0,a0+ln,fill=col+(235,),width=max(2,int(wd*D/640)+1))
        L.alpha_composite(out,(pad,pad)); d.ellipse((pad,pad,pad+D-1,pad+D-1),outline=(255,225,230,255),width=max(2,int(3*D/640)))
        comp(base,L,(cx-L.width/2,cy-L.height/2),alpha)
    # website screenshot card with marker highlight
    def web(self,name):
        if name not in self._web: self._web[name]=Image.open(self.P('web',name+'.png')).convert('RGBA')
        return self._web[name]
    def doc(self,base,name,cx,cy,t,t0,key=None,crop=None,w=980,h=640,hl_t=None,hl_col=(255,211,77),zoom=(1.0,1.08),src='ai-2027.com',alpha=1.0,dark=False,hl_dur=0.6):
        im=self.web(name); rects=self.WEB.get(key) if key else None
        if crop is None:
            if rects:
                x,y,ww,hh=rects[0]; cxp=(x+ww/2)*2; cyp=(y+hh/2)*2
            else: cxp,cyp=640,900
            cw=1240; ch=int(cw*h/w); crop=(cxp-cw/2,cyp-ch/2,cxp+cw/2,cyp+ch/2)
        x0,y0,x1,y1=crop; x0=max(0,min(x0,im.width-(x1-x0))); x1=x0+(crop[2]-crop[0]); y0=max(0,min(y0,im.height-(y1-y0))); y1=y0+(crop[3]-crop[1])
        z=lerp(zoom[0],zoom[1],eio((t-t0)/4.0)); fcx,fcy=(x0+x1)/2,(y0+y1)/2
        if rects:
            fcx=lerp(fcx,(rects[0][0]+rects[0][2]/2)*2,0.35*eio((t-t0)/4.0)); fcy=lerp(fcy,(rects[0][1]+rects[0][3]/2)*2,0.35*eio((t-t0)/4.0))
        cw,ch=(x1-x0)/z,(y1-y0)/z; s=w/cw; ax0=fcx-cw/2; ay0=fcy-ch/2
        L=im.transform((w,h),Image.AFFINE,(1/s,0,ax0,0,1/s,ay0),resample=Image.BICUBIC)
        if dark: L=ImageEnhance.Brightness(L).enhance(0.9)
        if rects and hl_t is not None and t>=hl_t:
            p=eo((t-hl_t)/hl_dur); hl=Image.new('RGBA',(w,h),(0,0,0,0)); dd=ImageDraw.Draw(hl); tot=sum(r[2] for r in rects); acc=0
            for (rx,ry,rw,rh) in rects:
                seg=clamp((p*tot-acc)/rw); acc+=rw
                if seg<=0: continue
                X0=(rx*2-ax0)*s; Y0=(ry*2-ay0)*s; X1=((rx+rw*seg)*2-ax0)*s; Y1=((ry+rh)*2-ay0)*s
                dd.rectangle((X0-4,Y0+2,X1+4,Y1+2),fill=hl_col+(120,))
            L=Image.alpha_composite(L,hl)
        m=rrect_mask(w,h,22); card=Image.new('RGBA',(w,h),(0,0,0,0)); card.paste(L,(0,0),m)
        ImageDraw.Draw(card).rounded_rectangle((1,1,w-2,h-2),22,outline=(255,255,255,90),width=2)
        sh=Image.new('RGBA',(w+120,h+120),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((60,70,60+w,70+h),26,fill=(0,0,0,210))
        comp(base,sh.filter(ImageFilter.GaussianBlur(24)),(cx-w/2-60,cy-h/2-60),alpha)
        comp(base,card,(cx-w/2,cy-h/2),alpha)
        if src: txt(base,src,cx-w/2+8,cy+h/2+34,28,'mono',(200,190,210),anchor='lm',alpha=alpha*0.85)
        return (cx-w/2,cy-h/2,w,h)
def kb(im,z,cx=0.5,cy=0.5,outw=W,outh=H):
    w,h=im.size; s=max(outw/w,outh/h)*z; cw,ch=outw/s,outh/s
    x0=min(max(cx*w-cw/2,0),w-cw); y0=min(max(cy*h-ch/2,0),h-ch)
    return im.transform((outw,outh),Image.AFFINE,(1/s,0,x0,0,1/s,y0),resample=Image.BICUBIC)
# ---------------- captions ----------------
def cap_chunks(WD):
    ws=[]
    for w in WD:
        if ws and (w[2] in ('000','000,') or w[2].startswith('000')) and ws[-1][2].isdigit(): ws[-1]=[ws[-1][0],w[1],ws[-1][2]+' '+w[2],w[3]]; continue
        if w[2] in ('—','–') : continue
        ws.append(list(w))
    out=[];cur=[]
    for k,w in enumerate(ws):
        cur.append(w); end=w[2][-1] in '.,?!…:' or k==len(ws)-1 or ws[k+1][3]!=w[3]
        if len(cur)>=3 or end or sum(len(x[2]) for x in cur)>15:
            out.append((cur[0][0],cur[-1][1],[x[2] for x in cur])); cur=[]
    res=[]
    for c in out:
        if res and len(c[2])==1 and len(res[-1][2])<=2 and res[-1][2][-1][-1] not in '.?!…' and c[0]-res[-1][1]<0.2 and sum(len(w) for w in res[-1][2]+c[2])<=17:
            p=res.pop(); res.append((p[0],c[1],p[2]+c[2]))
        else: res.append(c)
    return res
class Captions:
    def __init__(self,ctx,key): self.C=cap_chunks(ctx.WD); self.key=key; self.TOT=ctx.TOT
    def draw(self,base,t,y=1400,hide=False):
        if hide: return
        cur=None
        for k,(a,b,ws) in enumerate(self.C):
            nxt=self.C[k+1][0] if k+1<len(self.C) else self.TOT
            if a-0.05<=t<min(nxt,b+0.5): cur=(a,ws)
        if not cur: return
        a,ws=cur; size=84; words=[w.strip('«».,:—…?!') for w in ws]; words=[w for w in words if w]
        def lay(sz): return [text_layer(w.upper(),sz,'disp',YEL if w.lower().rstrip('-йгому') in self.key or w.lower() in self.key else WHITE,stroke=8,sfill=INK,glowc=None)[0] for w in words]
        ls=lay(size); sp=int(size*0.2); tw=sum(l.width for l in ls)-56*len(ls)+sp*(len(ls)-1)
        while tw>900 and size>54: size-=4; ls=lay(size); sp=int(size*0.2); tw=sum(l.width for l in ls)-56*len(ls)+sp*(len(ls)-1)
        u=eo((t-a)/0.15); x=540-tw/2-28
        for l in ls:
            s=0.88+0.12*u
            if u<1: l=l.resize((int(l.width*s),int(l.height*s)),Image.BICUBIC)
            comp(base,l,(x,y-l.height/2+14*(1-u)),u); x+=l.width-56*s+sp
def hud(base,t,s,alpha=1.0,col=RED):
    L=Image.new('RGBA',(W,80),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.text((140,40),s,font=font('mono',28),fill=(230,220,236,int(210*alpha)),anchor='lm')
    if int(t*2)%2==0: d.ellipse((108,32,124,48),fill=col+(int(230*alpha),))
    base.alpha_composite(L,(0,262))
# ---------------- infographic widgets ----------------
def dots(base,cx,cy,cols,rows,n_on,col,off=(60,56,72),r=9,gap=28,alpha=1.0,pulse=None):
    L=Image.new('RGBA',(cols*gap+20,rows*gap+20),(0,0,0,0)); d=ImageDraw.Draw(L)
    k=0
    for j in range(rows):
        for i in range(cols):
            on=k<n_on; c=col if on else off; rr=r
            d.ellipse((10+i*gap+gap/2-rr,10+j*gap+gap/2-rr,10+i*gap+gap/2+rr,10+j*gap+gap/2+rr),fill=c+(255,)); k+=1
    if pulse is not None: L=Image.alpha_composite(L.filter(ImageFilter.GaussianBlur(6)),L)
    comp(base,L,(cx-L.width/2,cy-L.height/2),alpha)
def counter(base,val,cx,cy,size,col=YEL,alpha=1.0,suffix='',fmt='{:,}'):
    s=fmt.format(int(val)).replace(',',' ')+suffix; txt(base,s,cx,cy,size,'disp',col,stroke=10,alpha=alpha,glowc=None)
def run_frames(frame_fn,NF):
    a=sys.argv[1]
    if a=='png':
        out=sys.argv[2]; ts=[float(x) for x in sys.argv[3].split(',')]
        ims=[frame_fn(int(round(x*FPS))+3) if x>=0 else frame_fn(0) for x in ts]
        n=len(ims); cols=min(n,5); rows=(n+cols-1)//cols; sh=Image.new('RGB',(cols*360,rows*640))
        for i,im in enumerate(ims): sh.paste(im.convert('RGB').resize((360,640)),((i%cols)*360,(i//cols)*640))
        sh.save(out)
    elif a=='one': frame_fn(int(round(float(sys.argv[3])*FPS))+3).convert('RGB').save(sys.argv[2])
    else:
        f0,f1,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
        p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','25','-i','-','-c:v','ffv1','-level','3','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
        for fi in range(f0,min(f1,NF)): p.stdin.write(frame_fn(fi).convert('RGB').tobytes())
        p.stdin.close(); p.wait()
