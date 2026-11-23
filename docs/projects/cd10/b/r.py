# cd10 renderer: «нейросеть рисует пикселями, код — формулами». Pillow, 25 fps, 1080x1920.
import sys, os, json, math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib import *
import scene as SC
from edge import lineart
ROOT=os.path.dirname(os.path.abspath(__file__)); P=lambda *a: os.path.join(ROOT,*a)
TL=json.load(open(P('timeline.json')))       # phrases, words, avatar segments
PH=TL['phrases']; WD=TL['words']; TOT=TL['tot']; AV=TL.get('avatar')
COVER=3                                        # cover frames before t=0
NF=COVER+int(round(TOT*FPS))
def pt(i,k=0): return PH[i][k]
def wt(word,ph,k=0,end=False):
    """time of the k-th word in phrase ph that starts with `word`"""
    n=0
    for w in WD:
        if w[3]==ph and w[2].lower().strip('.,!?…—:«»').startswith(word.lower()):
            if n==k: return w[1] if end else w[0]
            n+=1
    raise KeyError((word,ph))
# ---------------- avatar ----------------
_avc={}
REF=Image.open('/home/user/explainer-video-releases/docs/assets/ref_markus.png').convert('RGBA')
def av_frame(t):
    """frame of the HeyGen clip for timeline time t (falls back to the reference photo)"""
    if AV:
        for seg in AV['segs']:
            if seg['t0']-0.6<=t<=seg['t1']+0.6:
                i=int(round((t-seg['t0']+seg['src0']+AV.get('lag',0))*FPS))+1
                i=max(1,min(AV['n'],i)); fn=P('av',f'f{i:04d}.jpg')
                if fn in _avc: return _avc[fn]
                im=Image.open(fn).convert('RGBA').resize((1080,1920),Image.BICUBIC)
                if len(_avc)>40: _avc.clear()
                _avc[fn]=im; return im
    bg=Image.new('RGBA',REF.size,(38,38,42,255)); bg.alpha_composite(REF); return bg
CROP=(150,250,1050,1290)   # head + mic region of the 1080x1920 avatar frame
def av_card(t,w,h,crop=CROP,border=CYAN,bw=6,radius=36,mode=None,p=0.0):
    fr=av_frame(t); c=fr.crop(crop).resize((w,h),Image.BICUBIC)
    if mode=='pix' and p>0:            # mosaic dissolve
        b=max(1,int(p*48)); c=c.resize((max(1,w//b),max(1,h//b)),Image.BILINEAR).resize((w,h),Image.NEAREST)
    if mode=='line' and p>0:
        la=lineart(c,thr=10,blur=1.0); dark=Image.new('RGBA',(w,h),(8,12,26,255)); dark.alpha_composite(la)
        c=Image.blend(c,dark,p)
    m=rrect_mask(w,h,radius); out=Image.new('RGBA',(w,h),(0,0,0,0)); out.paste(c,(0,0),m)
    if bw:
        o=Image.new('RGBA',(w,h),(0,0,0,0)); ImageDraw.Draw(o).rounded_rectangle((1,1,w-2,h-2),radius,outline=border+(255,),width=bw)
        out.alpha_composite(o)
    return out
def put_card(base,card,cx,cy,scale=1.0,alpha=1.0,glowc=None):
    if scale!=1: card=card.resize((max(1,int(card.width*scale)),max(1,int(card.height*scale))),Image.BICUBIC)
    if glowc:
        g=Image.new('RGBA',(card.width+120,card.height+120),(0,0,0,0)); ImageDraw.Draw(g).rounded_rectangle((60,60,60+card.width,60+card.height),40,fill=glowc+(170,))
        comp(base,g.filter(ImageFilter.GaussianBlur(30)),(cx-g.width/2,cy-g.height/2),alpha)
    comp(base,card,(cx-card.width/2,cy-card.height/2),alpha)
# ---------------- background ----------------
_bgc=None
def background(t):
    global _bgc
    if _bgc is None:
        yy=np.linspace(0,1,H)[:,None]; c0=np.array((6,9,22)); c1=np.array((14,16,40))
        arr=(c0*(1-yy)+c1*yy)[:,None,:].repeat(W,1).astype(np.uint8)
        _bgc=Image.fromarray(arr).convert('RGBA')
    b=_bgc.copy(); d=ImageDraw.Draw(b); off=(t*18)%60
    for y in np.arange(-60,H+60,60):
        for x in np.arange(-60,W+60,60):
            d.point((x+off*0.5,y+off),fill=(40,52,92,255))
    return b
# ---------------- captions ----------------
KEY={'пикселями','формулами','зуме','каша','ни','шума','шаг','миллион','инструкцию','круг','радиус','жёлтый','билборд',
     'правки','голубую','всё','другие','одну','строчку','время','ожила','лицо','фотограф','чертёжник','кодом','меня','наверное','svg','нарисовать','подпишись'}
def cap_chunks():
    out=[]
    for i in range(len(PH)):
        ws=[w for w in WD if w[3]==i]; cur=[]
        for k,w in enumerate(ws):
            cur.append(w)
            raw=w[2]; end=raw[-1] in '.,?!…:—' or k==len(ws)-1
            if len(cur)>=3 or (end and len(cur)>=1) or sum(len(x[2]) for x in cur)>16:
                out.append((cur[0][0],cur[-1][1],[x[2] for x in cur])); cur=[]
        if cur: out.append((cur[0][0],cur[-1][1],[x[2] for x in cur]))
    res=[]
    for c in out:
        if res and len(c[2])==1 and len(res[-1][2])<=3 and c[0]-res[-1][1]<0.25 and sum(len(w) for w in res[-1][2]+c[2])<=20:
            p=res.pop(); res.append((p[0],c[1],p[2]+c[2]))
        else: res.append(c)
    return res
CAPS=None
def caption(base,t,y=1450):
    global CAPS
    if CAPS is None: CAPS=cap_chunks()
    cur=None
    for k,(a,b,ws) in enumerate(CAPS):
        nxt=CAPS[k+1][0] if k+1<len(CAPS) else TOT
        if a-0.05<=t<min(nxt,b+0.6): cur=(a,ws)
    if not cur: return
    a,ws=cur; size=74
    words=[w.strip('«».,:—…') for w in ws if w.strip('«».,:—…')]
    MAP={'Стэйбл':'Stable','Диффьюжн':'Diffusion','Клод':'Claude','Код':'Code','эс-вэ-гэ':'SVG','интэрнэт':'интернет'}
    if 'Клод' in words: words=[MAP.get(w,w) for w in words]
    else: words=[MAP.get(w,w) if w!='Код' else w for w in words]
    def layers(sz): return [text_layer(w.upper(),sz,'disp',YEL if w.lower().strip('.,!?…—:') in KEY else WHITE,stroke=7,sfill=INK)[0] for w in words]
    ls=layers(size); sp=int(size*0.18); tw=sum(l.width for l in ls)-56*len(ls)+sp*(len(ls)-1)
    while tw>880 and size>52:
        size-=4; ls=layers(size); sp=int(size*0.18); tw=sum(l.width for l in ls)-56*len(ls)+sp*(len(ls)-1)
    u=eo((t-a)/0.15); x=540-tw/2-28
    for l in ls:
        if u<1: l=l.resize((int(l.width*(0.9+0.1*u)),int(l.height*(0.9+0.1*u))),Image.BICUBIC)
        comp(base,l,(x,y-l.height/2+18*(1-u)),u); x+=l.width-56*(0.9+0.1*u)+sp
# ---------------- shared bits ----------------
def label(base,s,cx,cy,col,size=54,alpha=1.0,scale=1.0):
    f=font('disp',size); tw=f.getlength(s); w=int(tw+56); h=int(size*1.25)
    chip=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(chip)
    d.rounded_rectangle((1,1,w-2,h-2),h//2,fill=(8,10,22,225),outline=col+(255,),width=4)
    d.text((28,h/2),s,font=f,fill=col+(255,),anchor='lm')
    if scale!=1: chip=chip.resize((int(w*scale),int(h*scale)),Image.BICUBIC)
    comp(base,chip,(cx-chip.width/2,cy-chip.height/2),alpha)
def panel(img,w,h,col,radius=30,bw=5):
    m=rrect_mask(w,h,radius); out=Image.new('RGBA',(w,h),(0,0,0,0)); out.paste(img.resize((w,h)) if img.size!=(w,h) else img,(0,0),m)
    ImageDraw.Draw(out).rounded_rectangle((1,1,w-2,h-2),radius,outline=col+(255,),width=bw); return out
def code_layer(lines,w,h,typed=None,hl=None,size=34,cursor=True,t=0,bg=EDIT):
    """editor panel; lines = list of [(text,color),...]; typed = number of chars visible"""
    im=Image.new('RGBA',(w,h),bg+(240,)); d=ImageDraw.Draw(im); f=font('mono',size); lh=int(size*1.45)
    d.rectangle((0,0,w,46),fill=(22,27,36,255))
    for i,c in enumerate([(255,95,86),(255,189,46),(39,201,63)]): d.ellipse((20+i*30,14,38+i*30,32),fill=c)
    d.text((w-24,23),'moon.svg',font=font('monor',24),fill=(140,150,170),anchor='rm')
    left=typed if typed is not None else 10**9; y=70; cx=cy=None
    for li,ln in enumerate(lines):
        x=26
        d.text((x-4,y),f'{li+1:>2}',font=font('monor',size-8),fill=(70,80,100)); x+=58
        for seg,col in ln:
            if left<=0: break
            s=seg[:left]; left-=len(s)
            if hl and (li,seg) in hl:
                a=hl[(li,seg)]; bb=d.textbbox((x,y),s,font=f); d.rounded_rectangle((bb[0]-6,bb[1]-6,bb[2]+6,bb[3]+6),8,fill=(255,211,77,int(90*a)),outline=(255,211,77,int(255*a)),width=3)
            d.text((x,y),s,font=f,fill=col); x+=f.getlength(s); cx,cy=x,y
        if left<=0: break
        y+=lh
    if cursor and cx is not None and (int(t*2.5)%2==0):
        d.rectangle((cx+2,cy+2,cx+5,cy+size+2),fill=(230,230,240,255))
    return im
TAG=(255,123,114); ATT=(121,192,255); STR=(165,214,255); PUN=(201,209,217); NUM=(255,166,87); YELC=(255,211,77)
SVG_LINES=[
 [('<svg ',TAG),('viewBox=',ATT),('"0 0 1000 1000"',STR),('>',TAG)],
 [('  <rect ',TAG),('fill=',ATT),('"url(#night)"',STR),('/>',TAG)],
 [('  <circle ',TAG),('cx=',ATT),('"690" ',NUM),('cy=',ATT),('"260"',NUM)],
 [('          r=',ATT),('"120" ',NUM),('fill=',ATT),('"#FFD34D"',YELC),('/>',TAG)],
 [('  <path ',TAG),('d=',ATT),('"M0 470 Q120 360…"',STR),('/>',TAG)],
 [('</svg>',TAG)],
]
def nchars(lines,upto_line): return sum(len(s) for ln in lines[:upto_line] for s,_ in ln)
# ---------------- 3D helper ----------------
def persp_coeffs(src,dst):
    A=[];B=[]
    for (x,y),(X,Y) in zip(dst,src):
        A.append([x,y,1,0,0,0,-X*x,-X*y]); B.append(X)
        A.append([0,0,0,x,y,1,-Y*x,-Y*y]); B.append(Y)
    return np.linalg.solve(np.array(A,float),np.array(B,float)).tolist()
def project(layer,cx,cy,size,yaw,pitch,z,f=1600):
    """place square RGBA layer (world plane at depth z) rotated by yaw/pitch, return (img,offset)"""
    s=size/2; pts=[]
    cyw,syw=math.cos(yaw),math.sin(yaw); cp,sp=math.cos(pitch),math.sin(pitch)
    for X,Y in [(-s,-s),(s,-s),(s,s),(-s,s)]:
        x,y,zz=X,Y,z
        x,zz=x*cyw+zz*syw,-x*syw+zz*cyw
        y,zz=y*cp-zz*sp,y*sp+zz*cp
        k=f/(f+zz); pts.append((cx+x*k,cy+y*k))
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    x0,y0=int(min(xs))-2,int(min(ys))-2; x1,y1=int(max(xs))+2,int(max(ys))+2
    dst=[(p[0]-x0,p[1]-y0) for p in pts]; L=layer.width
    co=persp_coeffs([(0,0),(L,0),(L,L),(0,L)],dst)
    return layer.transform((x1-x0,y1-y0),Image.PERSPECTIVE,co,resample=Image.BICUBIC),(x0,y0)
# ---------------- scenes ----------------
def flash(base,t,t0,col=(220,240,255),a0=0.55,d=0.14):
    if t0<=t<t0+d:
        a=a0*(1-(t-t0)/d); comp(base,Image.new('RGBA',(W,H),col+(255,)),(0,0),a)
GLY=['<path','r=120','#FFD34D','cx=690','</svg>','fill=','M0 470','Q120','<circle','{ }','sin(t)']
def hook(base,t):
    a0,a1=pt(0,0),pt(0,1); u=t-a0
    tz=wt('зуме',0)
    ent=eo(prog(u,0,0.3)); split=eo(prog(u,0,0.22))*(1-eio(prog(u,0.95,0.4)))
    pp=1-eo(prog(u,0.1,1.1))       # pixel / line strength
    cw,ch=760,878; cx,cy=540,790
    out=prog(t,tz,0.5)              # fly-away into the zoom scene
    sc=(1.45-0.45*ent)*(1-0.55*eio(out)); alpha=1-eio(prog(t,tz+0.25,0.3))
    if alpha<=0: return
    full=av_card(t,cw,ch,bw=0)
    pix=av_card(t,cw,ch,bw=0,mode='pix',p=pp) if pp>0.02 else full
    lin=av_card(t,cw,ch,bw=0,mode='line',p=min(1,pp*1.3)) if pp>0.02 else full
    left=pix.crop((0,0,cw//2,ch)); right=lin.crop((cw//2,0,cw,ch))
    card=Image.new('RGBA',(cw+int(160*split),ch),(0,0,0,0))
    card.alpha_composite(left,(0,0)); card.alpha_composite(right,(cw//2+int(160*split),0))
    # echo copies («двойники»)
    if u<0.9:
        e=1-prog(u,0,0.9)
        for k,(col,dx) in enumerate([(CORAL,-1),(CYAN,1)]):
            ghost=full.copy(); tint=Image.new('RGBA',ghost.size,col+(255,)); ghost=Image.blend(ghost,tint,0.45)
            ghost.putalpha(full.getchannel('A').point(lambda v:int(v*0.55*e)))
            gs=sc*(1+0.25*(1-e))
            gg=ghost.resize((int(cw*gs),int(ch*gs)),Image.BICUBIC)
            comp(base,gg,(cx+dx*260*(1-e)*1.2-gg.width/2,cy-gg.height/2),1)
    # particles: noise squares from the left, code glyphs from the right
    rng=np.random.RandomState(4); d=ImageDraw.Draw(base)
    if split>0.05:
        for k in range(70):
            sx=rng.uniform(-1,0); sy=rng.uniform(-1,1); sp=rng.uniform(150,520); sz=rng.uniform(10,34)
            px=cx-60*split+sx*cw*0.5*sc - sp*u*split; py=cy+sy*ch*0.5*sc+rng.uniform(-60,60)*u
            c=tuple(int(v) for v in rng.randint(40,255,3))
            d.rectangle((px,py,px+sz,py+sz),fill=c+(int(220*split),))
        for k,g in enumerate(GLY*2):
            sy=rng.uniform(-1,1); sp=rng.uniform(150,520)
            px=cx+60*split+cw*0.25*sc+sp*u*split+rng.uniform(0,120); py=cy+sy*ch*0.5*sc
            d.text((px,py),g,font=font('mono',int(rng.uniform(24,40))),fill=(CYAN if k%2 else GREEN)+(int(235*split),))
    put_card(base,card,cx,cy,sc,alpha,glowc=CYAN)
    # seam
    if split>0.05:
        sx=cx; ln=Image.new('RGBA',(30,int(ch*sc)+40),(0,0,0,0)); ImageDraw.Draw(ln).rectangle((12,0,18,ln.height),fill=(255,255,255,255))
        comp(base,glow(ln,8,1.5),(sx-15,cy-ln.height/2),split*alpha); comp(base,ln,(sx-15,cy-ln.height/2),split*alpha)
    tp=wt('пикс',0); tf=wt('формул',0)
    if t>=tp: label(base,'ПИКСЕЛИ',290,300,CORAL,62,alpha*(1-prog(t,tz,0.2))*eo(prog(t,tp,0.2)),0.8+0.2*eob(prog(t,tp,0.25)))
    if t>=tf: label(base,'ФОРМУЛЫ',790,300,CYAN,62,alpha*(1-prog(t,tz,0.2))*eo(prog(t,tf,0.2)),0.8+0.2*eob(prog(t,tf,0.25)))
    flash(base,t,a0,a0=0.8,d=0.2)
_rast={}
def rast(key,variant=0,col=YEL,res=256,seed=3):
    if key not in _rast: _rast[key]=SC.raster(variant,col,res,seed)
    return _rast[key]
def zoom_split(base,t):
    t0=wt('зуме',0); t1=wt('лини',1,end=True)
    z=math.exp(lerp(math.log(0.5),math.log(42),eio(prog(t,t0+0.2,t1-t0-0.2))))
    pw,ph_=500,1000; ty=300
    # zoom target: moon's left edge
    fx,fy=SC.MOON[0]-SC.MR*0.985,SC.MOON[1]+18
    blend=eio(prog(z,0.5,4))
    cxw=lerp(500,fx,blend); cyw=lerp(430,fy,blend)
    L=SC.show_raster(rast('a'),pw,ph_,(cxw,cyw,z),smooth=0.0)
    R=SC.render(pw,ph_,(cxw,cyw,z),ss=2)
    ent=eo(prog(t,t0+0.15,0.35))
    comp(base,panel(L,pw,ph_,CORAL),(20,ty+60*(1-ent)),ent)
    comp(base,panel(R,pw,ph_,CYAN),(560,ty+60*(1-ent)),ent)
    label(base,'НЕЙРОСЕТЬ',270,ty,CORAL,50,ent); label(base,'КОД',810,ty,CYAN,50,ent)
    zs=f'ЗУМ ×{z:.0f}' if z>=1.5 else 'ЗУМ ×1'
    label(base,zs,540,ty+ph_+60,YEL,54,ent)
    tk=wt('каша',1)
    if t>=tk:
        a=eo(prog(t,tk,0.2)); txt(base,'КАША',270,ty+480,150,'disp',CORAL,stroke=8,alpha=a,scale=1.3-0.3*eob(prog(t,tk,0.25)),rot=8)
    tn=wt('ни',1)
    if t>=tn:
        a=eo(prog(t,tn,0.2)); txt(base,'РЕЗКО',810,ty+480,150,'disp',CYAN,stroke=8,alpha=a,scale=1.3-0.3*eob(prog(t,tn,0.25)),rot=-8)
    flash(base,t,t0+0.15,a0=0.35)
# --- diffusion ---
_diff={}
def diff_frames(key,variant,col):
    if key in _diff: return _diff[key]
    tgt=np.asarray(SC.render(256,256,(500,500,0.256),variant,col,ss=3).convert('RGB')).astype(np.float32)/255
    rng=np.random.RandomState(9+variant)
    noise=rng.normal(0,1,(256,256,3)).astype(np.float32)
    co=np.asarray(Image.fromarray(np.uint8(np.clip(rng.normal(0.5,0.25,(16,16,3)),0,1)*255)).resize((256,256),Image.BICUBIC)).astype(np.float32)/255-0.5
    fr=[]
    for k in range(31):
        s=k/30; ab=math.sin(s*math.pi/2)**2
        sig=(1-s)**1.5*14
        b=np.asarray(Image.fromarray(np.uint8(tgt*255)).filter(ImageFilter.GaussianBlur(sig))).astype(np.float32)/255 if sig>0.3 else tgt
        x=math.sqrt(ab)*b+math.sqrt(1-ab)*(0.35*noise+0.9*co)+0.5*(1-math.sqrt(ab))
        fr.append(Image.fromarray(np.uint8(np.clip(x,0,1)*255)).convert('RGBA'))
    _diff[key]=fr; return fr
def show_diff(fr,s,size):
    k=s*30; i=int(k); a=k-i
    im=fr[i] if i>=30 else Image.blend(fr[i],fr[i+1],a)
    return im.resize((size,size),Image.BILINEAR if s>0.85 else Image.NEAREST)
PROMPT='ночные горы, луна, звёзды'
_big=None
def diffusion(base,t):
    p0,p1=pt(2,0),pt(2,1); ts=wt('шума',2); tst=wt('шаг',2); tk=wt('картинк',2,end=True); tm=wt('миллион',2)
    size=900; cx,cy=540,820
    ent=eo(prog(t,p0,0.3))
    # prompt box
    typed=int(len(PROMPT)*prog(t,p0+0.1,1.2))
    pb=Image.new('RGBA',(900,96),(0,0,0,0)); d=ImageDraw.Draw(pb); d.rounded_rectangle((1,1,898,94),24,fill=(14,16,32,235),outline=CORAL+(255,),width=4)
    d.text((26,48),'ПРОМПТ ›',font=font('disp',44),fill=CORAL,anchor='lm'); d.text((210,48),PROMPT[:typed]+('|' if int(t*3)%2 else ''),font=font('mono',40),fill=(235,235,245),anchor='lm')
    comp(base,pb,(90,250),ent)
    fr=diff_frames('a',0,YEL)
    s=0.0
    if t>=tst: s=eio(prog(t,tst,max(0.6,tk-tst)))
    if t<tm-0.2:
        im=show_diff(fr,s,size)
        comp(base,panel(im,size,size,CORAL),(cx-size/2,cy-size/2+40*(1-ent)),ent)
        stp=int(round(s*30))
        label(base,f'ШАГ {max(1,stp) if t>=tst else 0}/30',540,cy+size/2+50,YEL,52,ent)
    else:
        # zoom into the pixel grid of a 1024x1024 picture
        global _big
        if _big is None: _big=SC.raster(0,YEL,1024,5)
        zp=eio(prog(t,tm-0.2,1.4)); z=math.exp(lerp(math.log(0.9),math.log(26),zp))
        fx,fy=lerp(500,SC.MOON[0]-SC.MR+6,zp),lerp(500,SC.MOON[1]+30,zp)
        im=SC.show_raster(_big,size,size,(fx,fy,z),0)
        if z>8:
            d=ImageDraw.Draw(im); step=z*1024/1000/1.0*1000/1024
            px=z*1.024*0.977
            gx0=(size/2-((fx*1.024)%1)*px)%px
            ga=int(min(1,(z-8)/8)*140)
            x=gx0
            while x<size: d.line((x,0,x,size),fill=(0,0,0,ga),width=2); x+=px
            y=gx0
            while y<size: d.line((0,y,size,y),fill=(0,0,0,ga),width=2); y+=px
        comp(base,panel(im,size,size,CORAL),(cx-size/2,cy-size/2),1)
        n=int(1048576*eo(prog(t,tm,1.0)))
        nt=f'{n:,}'.replace(',',' ')
        txt(base,nt,540,cy-60,150,'disp',YEL,stroke=10)
        txt(base,'ЦВЕТНЫХ ТОЧЕК',540,cy+70,84,'disp',WHITE,stroke=8,alpha=eo(prog(t,tm+0.2,0.3)))
        label(base,'1024 × 1024',540,cy+size/2+50,CORAL,52)
    flash(base,t,p0,a0=0.35)
# --- code ---
def code_canvas(stage,size,moon_fill,ridge_p,rad_p):
    """stage: 0 empty,1 sky, 2 moon outline, 3 moon filled, 4 ridges"""
    sc=size/1000; layers=['sky','stars'] if stage>=1 else []
    im=SC.render(size,size,(500,500,sc),layers=tuple(layers),ss=2) if layers else Image.new('RGBA',(size,size),(18,22,40,255))
    if stage<1:
        d=ImageDraw.Draw(im)
        for k in range(0,size,40): d.line((k,0,k,size),fill=(30,36,60)); d.line((0,k,size,k),fill=(30,36,60))
    d=ImageDraw.Draw(im); X,Y,R=SC.MOON[0]*sc,SC.MOON[1]*sc,SC.MR*sc
    if stage>=2:
        if moon_fill>0:
            m=SC.render(size,size,(500,500,sc),moon_col=mixc((40,46,80),YEL,moon_fill),layers=('moon',),ss=2)
            im.alpha_composite(m)
        d=ImageDraw.Draw(im); d.ellipse((X-R,Y-R,X+R,Y+R),outline=CYAN+(int(255*(1-moon_fill*0.6)),),width=4)
        if rad_p>0:
            ex=X+R*rad_p; d.line((X,Y,ex,Y),fill=(255,255,255,255),width=5); d.ellipse((X-7,Y-7,X+7,Y+7),fill=(255,255,255,255))
            d.text(((X+ex)/2,Y-28),'120',font=font('mono',38),fill=(255,255,255),anchor='mm')
    if stage>=4 and ridge_p>0:
        r=SC.render(size,size,(500,500,sc),layers=('ridges','lake'),ss=2)
        m=Image.new('L',(size,size),0); ImageDraw.Draw(m).rectangle((0,0,int(size*ridge_p),size),fill=255)
        im.paste(r,(0,0),Image.composite(r.getchannel('A'),Image.new('L',(size,size),0),m))
    return im
def code_scene(base,t):
    p0,p1=pt(3,0),pt(3,1); ti=wt('инструк',3); tc=wt('круг',3); tr=wt('радиус',3); ty_=wt('жёлт',3); tb=wt('браузер',3); tbb=wt('билборд',3)
    ent=eo(prog(t,p0,0.3))
    # typing schedule (chars)
    n1=nchars(SVG_LINES,2); n2=nchars(SVG_LINES,3); n3=nchars(SVG_LINES,4); n4=nchars(SVG_LINES,5); nall=nchars(SVG_LINES,6)
    if t<tc: typed=int(n1*prog(t,p0+0.1,max(0.3,ti-p0)))
    elif t<tr: typed=int(lerp(n1,n2,prog(t,tc,0.35)))
    elif t<tb: typed=int(lerp(n2,n3,prog(t,tr,0.5)))
    else: typed=int(lerp(n3,nall,prog(t,tb-0.6,0.7)))
    hl={}
    if t>=tc: hl[(2,'  <circle ')]=eo(prog(t,tc,0.15))*(1-prog(t,tr,0.2))
    if t>=tr: hl[(3,'"120" ')]=eo(prog(t,tr,0.15))*(1-prog(t,ty_,0.2))
    if t>=ty_: hl[(3,'"#FFD34D"')]=eo(prog(t,ty_,0.15))*(1-prog(t,tb,0.3))
    stage=1 if typed>=nchars(SVG_LINES,2)-2 else 0
    if t>=tc: stage=2
    if t>=ty_: stage=3
    if typed>=n4-3: stage=4
    mf=eo(prog(t,ty_,0.3)) if t>=ty_ else 0
    rp=eo(prog(t,tr,0.35)) if t>=tr else 0
    rdp=prog(t,tb-0.5,0.8) if stage>=4 else 0
    bb=prog(t,tbb-0.35,0.7)
    size=int(lerp(620,620,bb))
    cv=code_canvas(stage,620,mf,rdp,rp*(1-prog(t,ty_,0.3)))
    if bb<=0:
        comp(base,panel(cv,620,620,CYAN),(230,280+40*(1-ent)),ent)
        ed=code_layer(SVG_LINES,1000,440,typed=typed,hl=hl,size=33,t=t)
        comp(base,panel(ed,1000,440,(60,70,96),24,3),(40,940),ent)
    else:
        billboard(base,t,cv,bb,tbb)
    flash(base,t,p0,a0=0.35)
def billboard(base,t,cv,bb,tbb):
    # city night, billboard on posts, tiny person -> shows scale; art stays crisp
    e=eio(bb); d=ImageDraw.Draw(base)
    gy=1240
    d.rectangle((0,gy,W,gy+300),fill=(10,12,24,255))
    for k,(x,w,h) in enumerate([(0,150,380),(140,120,300),(860,220,420),(980,120,260)]):
        d.rectangle((x,gy-h,x+w,gy),fill=(16,20,38,255))
        for yy in range(gy-h+20,gy-10,40):
            for xx in range(x+14,x+w-14,34):
                if (xx*7+yy*3)%5<2: d.rectangle((xx,yy,xx+12,yy+18),fill=(60,58,40,255))
    bw=int(lerp(620,940,e)); bh=bw; bx=540-bw/2; by=lerp(280,260,e)
    d.rectangle((540-bw*0.32-14,by+bh,540-bw*0.32+14,gy),fill=(40,44,60,255)); d.rectangle((540+bw*0.32-14,by+bh,540+bw*0.32+14,gy),fill=(40,44,60,255))
    art=cv.resize((bw,bh),Image.LANCZOS)
    hi=SC.render(bw,bh,(500,500,bw/1000),ss=2)
    art=Image.blend(art,hi,e)
    comp(base,panel(art,bw,bh,(200,200,215),12,8),(bx,by),1)
    # person 1.8 m vs ~ 10 m board
    px,py=760,gy; s=lerp(0,1,e)
    if s>0:
        ph=int(95*s); d.ellipse((px-9*s,py-ph-16*s,px+9*s,py-ph+2*s),fill=(230,230,240,255)); d.rounded_rectangle((px-11*s,py-ph,px+11*s,py),radius=6,fill=(230,230,240,255))
        label(base,'ЭТО ЧЕЛОВЕК',px+170,py-70,WHITE,44,e)
    label(base,'×100 — БЕЗ РАЗМЫТИЯ',540,gy+90,CYAN,56,eo(prog(t,tbb,0.3)))
# --- edit ---
EDIT_LINES=[[('<circle ',TAG),('cx=',ATT),('"690" ',NUM),('cy=',ATT),('"260"',NUM)],
            [('        r=',ATT),('"120" ',NUM),('fill=',ATT),('"#FFD34D"',YELC),('/>',TAG)]]
BLUE=(110,200,255)
def edit_scene(base,t):
    p0,p1=pt(4,0),pt(4,1); tg=wt('голуб',4); tn=wt('нейросеть',4); tgo=wt('горы',4); tc=wt('коде',4); to=wt('одну',4); tos=wt('остальн',4)
    ent=eo(prog(t,p0,0.3)); size=490; y0=360
    label(base,'НЕЙРОСЕТЬ',285,y0-50,CORAL,48,ent); label(base,'КОД',795,y0-50,CYAN,48,ent)
    # left panel
    fr1=diff_frames('a',0,YEL); fr2=diff_frames('b',2,BLUE)
    if t<tn: Limg=show_diff(fr1,1.0,size)
    else:
        q=prog(t,tn,max(0.8,tgo-tn))
        if q<0.4: Limg=show_diff(fr1,1-eio(q/0.4),size)
        else: Limg=show_diff(fr2,eio((q-0.4)/0.6),size)
    comp(base,panel(Limg,size,size,CORAL),(40,y0+40*(1-ent)),ent)
    if t>=tgo:
        a=eo(prog(t,tgo,0.25)); ov=Image.new('RGBA',(size,size),(0,0,0,0)); d=ImageDraw.Draw(ov)
        for (x,y,r) in [(120,250,70),(330,300,80)]:
            d.ellipse((x-r,y-r,x+r,y+r),outline=(255,70,70,255),width=7)
        comp(base,ov,(40,y0),a); label(base,'ГОРЫ ДРУГИЕ',285,y0+size+50,(255,90,90),46,a)
    # right panel
    blue=eo(prog(t,to+0.15,0.25)) if t>=to else 0
    col=mixc(YEL,BLUE,blue)
    R=SC.render(size,size,(500,500,size/1000),moon_col=col,ss=2)
    comp(base,panel(R,size,size,CYAN),(550,y0+40*(1-ent)),ent)
    if t>=tos:
        a=eo(prog(t,tos,0.25)); label(base,'✓ ОСТАЛЬНОЕ НА МЕСТЕ'.replace('✓ ',''),795,y0+size+50,GREEN,44,a)
    # request chip
    if t>=tg: label(base,'«СДЕЛАЙ ЛУНУ ГОЛУБОЙ»',540,y0+size+130,WHITE,50,eo(prog(t,tg,0.2)),0.85+0.15*eob(prog(t,tg,0.25)))
    # code editor with the one changed line
    if t>=tc-0.3:
        a=eo(prog(t,tc-0.3,0.25)); lines=[l[:] for l in EDIT_LINES]
        if t>=to:
            k=prog(t,to,0.3); old='#FFD34D'; new='#6EC8FF'; n=int(round(k*7))
            s='"'+new[:n+1 if n<7 else 7]+old[n+1:]+'"' if n<7 else '"'+new+'"'
            lines[1][3]=(s,mixc(YELC,BLUE,k))
        hl={(1,lines[1][3][0]):1.0} if t>=to else {}
        ed=code_layer(lines,1000,200,hl=hl,size=34,t=t)
        comp(base,panel(ed,1000,200,(60,70,96),24,3),(40,1060),a)
        if t>=to: label(base,'1 СТРОКА',900,1035,GREEN,44,eo(prog(t,to,0.2)),0.8+0.2*eob(prog(t,to,0.25)))
    flash(base,t,p0,a0=0.35)
# --- animate (exploded 3D layers) ---
_lay=None
def anim_scene(base,t):
    global _lay
    p0,p1=pt(5,0),pt(5,1); tv=wt('время',5); to=wt('ожил',5)
    ent=eo(prog(t,p0,0.3)); L=900
    an=t-tv if t>=tv else 0
    rise=40*math.sin(an*2.2) if t>=tv else 0
    order=[('sky',),('stars',),('moon',),('ridges',),('lake',)]
    ex=eio(prog(t,to,0.7))       # explode amount
    yaw=math.radians(-22*ex*math.sin(0.5+an*0.9)); pitch=math.radians(10*ex)
    cx,cy=540,760
    for k,ly in enumerate(order):
        im=SC.render(L,L,(500,500,L/1000),layers=ly,t=(an if t>=tv else None),rise=rise,ss=1 if ly!=('moon',) else 2)
        z=(2-k)*170*ex
        if ex>0.01:
            pim,(ox,oy)=project(im,cx,cy,L,yaw,pitch,z)
            if ex>0.05 and k>0:
                g=pim.copy(); g.putalpha(pim.getchannel('A').point(lambda v:int(v*0.25)))
            comp(base,pim,(ox,oy+40*(1-ent)),ent)
        else:
            comp(base,im,(cx-L/2,cy-L/2+40*(1-ent)),ent)
    if ex<0.05:
        o=Image.new('RGBA',(L,L),(0,0,0,0)); ImageDraw.Draw(o).rounded_rectangle((1,1,L-2,L-2),30,outline=CYAN+(255,),width=5); comp(base,o,(cx-L/2,cy-L/2+40*(1-ent)),ent*(1-ex*20))
    code=[[('cy',ATT),(' = ',PUN),('260',NUM),(' − ',PUN),('40',NUM),('·',PUN),('sin(',TAG),('t',YELC),(')',TAG)]]
    typed=int(19*prog(t,p0+0.05,max(0.3,tv-p0)))
    ed=code_layer(code,760,140,typed=typed,size=44,t=t)
    comp(base,panel(ed,760,140,(60,70,96),24,3),(160,1260),ent)
    flash(base,t,p0,a0=0.35)
# --- balance: photographer vs draftsman ---
def icon_camera(p,col,s=1.0):
    im=Image.new('RGBA',(420,340),(0,0,0,0)); d=ImageDraw.Draw(im); w=10
    segs=[('rr',(30,90,390,320)),('r',(130,50,250,90)),('e',(130,135,290,295)),('e',(170,175,250,255)),('e',(320,115,350,145))]
    n=len(segs); q=p*n
    for i,(k,b) in enumerate(segs):
        a=clamp(q-i)
        if a<=0: break
        c=col+(int(255*a),)
        if k=='rr': d.rounded_rectangle(b,36,outline=c,width=w)
        elif k=='r': d.rectangle(b,outline=c,width=w)
        else: d.ellipse(b,outline=c,width=w)
    return im
def icon_compass(p,col):
    im=Image.new('RGBA',(420,340),(0,0,0,0)); d=ImageDraw.Draw(im); w=10
    segs=[((210,30),(110,300)),((210,30),(310,300)),((150,190),(270,190)),((40,320),(380,320))]
    q=p*(len(segs)+1)
    for i,(a,b) in enumerate(segs):
        f=clamp(q-i)
        if f<=0: break
        d.line((a,(a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f)),fill=col+(255,),width=w)
    if q>len(segs): d.ellipse((190,10,230,50),outline=col+(255,),width=w)
    for x in range(60,380,40):
        if q>3.5: d.line((x,320,x,300),fill=col+(255,),width=5)
    return im
def balance(base,t):
    p0=pt(6,0); tf=wt('фотограф',6); tc=wt('чертёж',6); tl=wt('лицо',6)
    ent=eo(prog(t,p0,0.3))
    label(base,'НЕЙРОСЕТЬ',285,330,CORAL,50,ent); label(base,'КОД',795,330,CYAN,50,ent)
    ci=icon_camera(eio(prog(t,p0+0.1,1.0)),CORAL); comp(base,ci.resize((380,308)),(95,450),ent)
    cc=icon_compass(eio(prog(t,p0+0.3,1.0)),CYAN); comp(base,cc.resize((380,308)),(605,450),ent)
    if t>=tl:
        a=eo(prog(t,tl,0.3))
        for k,s in enumerate(['ЛИЦА','ФОТО','ТЕКСТУРЫ']): label(base,s,285,850+k*80,WHITE,40,a*eo(prog(t,tl+k*0.12,0.2)))
    if t>=tc-0.4:
        a=eo(prog(t,tc-0.4,0.3))
        for k,s in enumerate(['СХЕМЫ','ЛОГОТИПЫ','АНИМАЦИЯ']): label(base,s,795,850+k*80,WHITE,40,a*eo(prog(t,tc-0.4+k*0.12,0.2)))
    if t>=tf: txt(base,'ФОТОГРАФ',285,1190,96,'disp',CORAL,stroke=8,alpha=eo(prog(t,tf,0.2)),scale=1.2-0.2*eob(prog(t,tf,0.25)))
    if t>=tc: txt(base,'ЧЕРТЁЖНИК',795,1190,96,'disp',CYAN,stroke=8,alpha=eo(prog(t,tc,0.2)),scale=1.2-0.2*eob(prog(t,tc,0.25)))
    flash(base,t,p0,a0=0.35)
# --- ending ---
SRC=[l.rstrip() for l in open(__file__,encoding='utf-8').read().splitlines() if l.strip()]
def code_wall(base,t,bright=0.3):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); f=font('monor',22); lh=30
    off=(t*60)%lh; start=int(t*60/lh)
    for k in range(H//lh+2):
        s=SRC[(start+k)%len(SRC)][:80]; y=k*lh-off
        d.text((24,y),s,font=f,fill=(CYAN if k%3 else GREEN)+(int(255*bright),))
    comp(base,lay,(0,0),1)
def ending(base,t):
    p0=pt(7,0); tv=wt('всё',7); tk=wt('кодом',7); tm=wt('меня',7); tn=wt('наверн',7)
    p8=pt(8,0); tw=wt('напиши',8); ts=wt('подпиш',8); tsv=WD[-1][0]
    br=0.18+0.25*eo(prog(t,tk,0.3))-0.1*eo(prog(t,p8,0.5))
    code_wall(base,t,br)
    band=Image.new('RGBA',(W,360),(0,0,0,0)); bd=ImageDraw.Draw(band)
    for i in range(360): bd.line((0,i,W,i),fill=(6,9,22,int(235*math.sin(math.pi*i/360)**0.6)))
    comp(base,band,(0,1270),1)
    ent=eo(prog(t,p0,0.35)); cw,ch=760,878; cx,cy=540,800
    mode=None; pp=0
    if tn<=t<tn+0.35: mode,pp='line',1.0
    if t>=tsv-0.25: mode,pp='line',eio(prog(t,tsv-0.25,0.6))
    card=av_card(t,cw,ch,border=YEL if tm<=t<tm+0.5 else CYAN,mode=mode,p=pp)
    put_card(base,card,cx,cy,0.85+0.15*eob(prog(t,p0,0.4)),ent,glowc=CYAN)
    if tm<=t<tm+0.18: flash(base,t,tm,col=(255,230,150),a0=0.3,d=0.18)
    if t>=tw:
        a=eo(prog(t,tw,0.25)); b=Image.new('RGBA',(840,130),(0,0,0,0)); d=ImageDraw.Draw(b)
        d.rounded_rectangle((2,2,836,108),40,fill=(255,255,255,240)); d.polygon([(120,106),(170,106),(110,128)],fill=(255,255,255,240))
        d.text((420,56),'ЧТО НАРИСОВАТЬ КОДОМ?',font=font('disp',58),fill=INK,anchor='mm')
        comp(base,b,(120,240+20*(1-a)),a)
    if t>=ts:
        a=eo(prog(t,ts,0.2)); label(base,'ПОДПИСАТЬСЯ',540,1300,(255,60,70),58,a,0.8+0.2*eob(prog(t,ts,0.25)))
    if t>=tsv-0.25:
        a=eo(prog(t,tsv-0.25,0.3)); txt(base,'<svg>',540,cy,180,'mono',CYAN,stroke=8,alpha=a)
    flash(base,t,p0,a0=0.4)
# ---------------- cover ----------------
def cover():
    b=background(0); code_wall(b,3.0,0.22)
    cw,ch=760,878; full=av_card(0.5,cw,ch,bw=0); pix=av_card(0.5,cw,ch,bw=0,mode='pix',p=0.55); lin=av_card(0.5,cw,ch,bw=0,mode='line',p=1.0)
    card=Image.new('RGBA',(cw+60,ch),(0,0,0,0)); card.alpha_composite(pix.crop((0,0,cw//2,ch)),(0,0)); card.alpha_composite(lin.crop((cw//2,0,cw,ch)),(cw//2+60,0))
    put_card(b,card,540,980,0.95,1,glowc=YEL)
    txt(b,'НЕЙРОСЕТЬ',540,330,190,'disp',CORAL,stroke=12)
    txt(b,'ПРОТИВ КОДА',540,520,170,'disp',CYAN,stroke=12)
    label(b,'ЧЕМ РИСУЕТ CLAUDE CODE',540,1470,YEL,70)
    return b
# ---------------- frame ----------------
def frame(fi):
    if fi<COVER: return cover()
    t=(fi-COVER)/FPS
    b=background(t)
    if t<pt(1,0): hook(b,t)
    if wt('зуме',0)<=t<pt(2,0): zoom_split(b,t)
    if pt(2,0)<=t<pt(3,0): diffusion(b,t)
    if pt(3,0)<=t<pt(4,0): code_scene(b,t)
    if pt(4,0)<=t<pt(5,0): edit_scene(b,t)
    if pt(5,0)<=t<pt(6,0): anim_scene(b,t)
    if pt(6,0)<=t<pt(7,0): balance(b,t)
    if t>=pt(7,0): ending(b,t)
    caption(b,t)
    b.alpha_composite(VIG)
    return b
VIG=vignette(None,0.5)
if __name__=='__main__':
    a=sys.argv[1]
    if a=='png':
        out=sys.argv[2]; ts=[float(x) for x in sys.argv[3].split(',')]
        ims=[frame(COVER+int(round(x*FPS))) if x>=0 else frame(0) for x in ts]
        n=len(ims); cols=min(n,4); rows=(n+cols-1)//cols; sh=Image.new('RGB',(cols*360,rows*640))
        for i,im in enumerate(ims): sh.paste(im.convert('RGB').resize((360,640)),((i%cols)*360,(i//cols)*640))
        sh.save(out)
    elif a=='one':
        frame(COVER+int(round(float(sys.argv[3])*FPS))).convert('RGB').save(sys.argv[2])
    else:
        f0,f1,out=int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
        p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','25','-i','-','-c:v','ffv1','-level','3','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
        for fi in range(f0,min(f1,NF)): p.stdin.write(frame(fi).convert('RGB').tobytes())
        p.stdin.close(); p.wait()
