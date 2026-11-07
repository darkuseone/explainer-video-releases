import sys,os,math,subprocess,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from lib import W,H,FPS,clamp,eo,eio,eob,comp,kb,line
from shots import S,TOT
from caps import CAP,COOL
FD='/usr/share/fonts/truetype/sand-box/google/'
# ---- dc10 look: "THERMAL GRID": graphite, ice-cyan (cooling), hot amber (heat), warm off-white ----
GRA=(16,19,23); ICE=(127,227,255); HOT=(255,122,26); OFF=(242,238,230); DIM=(128,134,142)
NF=int(round(TOT*FPS)); X0,X1=120,780; CX=450; SAFE=(120,270,780,1250)
_fc={}
def font(k,s):
    s=int(s); key=(k,s)
    if key in _fc: return _fc[key]
    if k=='ro': f=ImageFont.truetype(FD+'Russo One/RussoOne-Regular.ttf',s)
    elif k=='mr': f=ImageFont.truetype(FD+'Manrope/Manrope-VariableFont_wght.ttf',s); f.set_variation_by_axes([800])
    else: f=ImageFont.truetype(FD+'IBM Plex Mono/IBMPlexMono-SemiBold.ttf',s)
    _fc[key]=f; return f
def P(t,a,d): return clamp((t-a)/d)
# ---- avatar ----
AVD='/workspace/dc10/av/fr/'; SEG=json.load(open('/workspace/dc10/av/seg.json')); LAG=0.023
AVN=len(os.listdir(AVD))
OFFS={k:v['tl'][0]-v['clip'][0] for k,v in SEG.items()}
def avframe(t,seg):
    i=int(round((t-OFFS[seg]+LAG)*FPS)); i=max(0,min(AVN-1,i))
    return Image.open(AVD+'f%04d.jpg'%(i+1)).convert('RGB')
NFR={}
def vframe(k,i):
    d='shots/%02d_%s/'%(k,S[k][1])
    if d not in NFR: NFR[d]=len(os.listdir(d))
    n=NFR[d]; i=i%(2*n-2); i=i if i<n else 2*n-2-i
    return Image.open(d+'f%04d.jpg'%(i+1)).convert('RGB')
STILL={}
def cur(t):
    k=0
    for j,s in enumerate(S):
        if t>=s[0]: k=j
    return k
def nxt(k): return S[k+1][0] if k+1<len(S) else TOT
def shot(t,k):
    t0,key,f,ss,cx,z0,z1=S[k]
    if key=='AVA': return kb(avframe(t,'A'),t,t0,nxt(k)-t0,1.10,1.14,cx=0.57,cy=0.40)
    if key=='AVC': return kb(avframe(t,'C'),t,t0,nxt(k)-t0,1.14,1.10,cx=0.57,cy=0.40)
    if f.endswith('.jpg'):
        if f not in STILL: STILL[f]=Image.open(f).convert('RGB')
        return kb(STILL[f],t,t0,nxt(k)-t0,z0,z1,cx=cx,cy=0.45)
    return kb(vframe(k,int((t-t0)*FPS)),t,t0,nxt(k)-t0,z0,z1)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
VIG=np.clip((np.sqrt(((xx-W/2)/(W*0.8))**2+((yy-H/2)/(H*0.72))**2)-0.5)*1.2,0,0.7)[...,None]
G=np.array(GRA,np.float32)/255
def grade(im,t,avatar=False):
    a=np.asarray(im.convert('RGB')).astype(np.float32)/255
    if avatar:
        a=G*0.6+a*(1-G*0.6); a=a*(1-VIG*0.7)
        return Image.fromarray((a.clip(0,1)*255).astype(np.uint8)).convert('RGBA')
    lum=a.mean(2,keepdims=True)
    a=lum+(a-lum)*0.88                               # slight desat
    a=np.clip((a-0.03)/0.95,0,1)**1.06
    sh=(1-lum)**3; hi=lum**3
    a=a+sh*np.array([-0.01,0.012,0.03],np.float32)+hi*np.array([0.03,0.012,-0.02],np.float32)  # cool shadows, warm highlights
    a=G+a*(1-G)                                       # graphite floor
    a=a*(1-VIG)
    return Image.fromarray((a.clip(0,1)*255).astype(np.uint8)).convert('RGBA')
def grainf(i):
    rs=np.random.RandomState(i); n=rs.randint(0,255,(H//2,W//2)).astype(np.uint8); z=np.zeros((H//2,W//2,4),np.uint8); z[...,0]=n;z[...,1]=n;z[...,2]=n;z[...,3]=9
    return Image.fromarray(z).resize((W,H))
GR=[grainf(i) for i in range(6)]
REG=[]; TOP=[]; WARN=[]
def inside(a,c,p=0): return a[0]>=c[0]+p-0.5 and a[1]>=c[1]+p-0.5 and a[2]<=c[2]-p+0.5 and a[3]<=c[3]-p+0.5
def ovl(a,b): return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]
def check(f):
    bad=[]
    for n,ink,c,p in REG:
        if not inside(ink,c,p): bad.append(f'TEXT {n!r} ink={tuple(int(v) for v in ink)} cont={tuple(int(v) for v in c)}')
        if not inside(ink,SAFE): bad.append(f'TEXT {n!r} outside safe')
    for i,(n,bx) in enumerate(TOP):
        if not inside(bx,SAFE): bad.append(f'BOX {n} {tuple(int(v) for v in bx)} outside safe')
        for m,by in TOP[i+1:]:
            if ovl(bx,by): bad.append(f'OVERLAP {n} x {m}')
    if bad: raise SystemExit(f'TEXT-FIT FAIL frame {f} t={f/FPS:.2f}:\n  '+'\n  '.join(bad))
def text(b,s,k,size,cx,cy,col,alpha=1.0,maxw=X1-X0,shadow=True,name=None,cont=None,pad=0,minsz=22,left=None):
    size=int(size)
    while size>minsz and font(k,size).getlength(s)>maxw: size-=2
    if font(k,size).getlength(s)>maxw: WARN.append(f'{s} too wide')
    f=font(k,size); anc='mm' if left is None else 'lm'; l,tp,r,bt=f.getbbox(s,anchor=anc)
    x=cx if left is None else left; ink=(x+l,cy+tp,x+r,cy+bt)
    if alpha>0.003:
        g=22 if shadow else 4
        lay=Image.new('RGBA',(int(r-l)+2*g+8,int(bt-tp)+2*g+8),(0,0,0,0)); ox,oy=g+4-l,g+4-tp
        if shadow:
            sh=Image.new('RGBA',lay.size,(0,0,0,0)); ImageDraw.Draw(sh).text((ox,oy+3),s,font=f,fill=(0,0,0,170),anchor=anc,stroke_width=3)
            lay=Image.alpha_composite(lay,sh.filter(ImageFilter.GaussianBlur(9)))
        ImageDraw.Draw(lay).text((ox,oy),s,font=f,fill=col+(255,),anchor=anc)
        comp(b,lay,(x-ox,cy-oy),alpha)
    REG.append((name or s,ink,cont or SAFE,pad)); return ink,size
def panel(b,box,alpha,fill=GRA,fa=0.82,edge=None,r=14,ew=2):
    if alpha<=0.003: return
    x0,y0,x1,y1=[int(round(v)) for v in box]; lay=Image.new('RGBA',(x1-x0,y1-y0),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((0,0,x1-x0-1,y1-y0-1),r,fill=fill+(int(255*fa),),outline=(edge+(230,)) if edge else None,width=ew)
    comp(b,lay,(x0,y0),alpha)
def thermbar(w,h):
    x=np.linspace(0,1,w)[None,:,None]
    stops=[(0,(40,70,160)),(0.3,ICE),(0.55,OFF),(0.8,HOT),(1,(255,60,40))]
    c=np.zeros((1,w,3))
    for (a,ca),(bb,cb) in zip(stops[:-1],stops[1:]):
        m=(x[...,0]>=a)&(x[...,0]<=bb); p=((x[...,0]-a)/(bb-a))[...,None]
        c=np.where(m[...,None],np.array(ca)*(1-p)+np.array(cb)*p,c)
    return np.repeat(c,h,0).astype(np.uint8)
TB=Image.fromarray(thermbar(X1-X0,6)).convert('RGBA')
LUT=thermbar(256,1)[0].astype(np.float32)
# ---------- HUD ----------
CHAP=[(0,'01 · СТРОЙКА'),(9.72,'02 · ЧТО ЭТО'),(15.02,'03 · ЗАЧЕМ'),(21.60,'04 · ГИГАВАТТ'),(31.10,'05 · ТУРБИНЫ'),(38.90,'06 · ТЕПЛО'),(45.45,'07 · ИТОГ'),(50.45,'08 · ВОПРОС')]
ILL=[(21.60,24.30),(31.10,38.90)]
def hud(b,t,k):
    ch=[s for a,s in CHAP if t>=a][-1]
    ink,_=text(b,'SPACEX · ТЕХАС','mono',24,0,300,OFF,0.85,left=X0,name='hudl'); TOP.append(('hudl',ink))
    f=font('mono',22); w=f.getlength(ch)+32; box=(X1-w,281,X1,319)
    panel(b,box,1,fa=0.7,edge=HOT,r=19); text(b,ch,'mono',22,(box[0]+box[2])/2,300,OFF,shadow=False,name='chip',cont=box,pad=5); TOP.append(('chip',box))
    if any(a<=t<c for a,c in ILL):
        s='ИЛЛЮСТРАЦИЯ'; f=font('mono',20); w=f.getlength(s)+28; box=(X0,336,X0+w,368)
        panel(b,box,0.9,fa=0.6,edge=DIM,r=16); text(b,s,'mono',20,(box[0]+box[2])/2,352,(205,208,214),0.9,shadow=False,name='ill',cont=box,pad=4); TOP.append(('ill',box))
    for (px,py,dx,dy) in [(X0-50,255,1,1),(X1+50,255,-1,1),(X0-50,1265,1,-1),(X1+50,1265,-1,-1)]:
        line(b,(px,py),(px+dx*30,py),OFF,2,0.4); line(b,(px,py),(px,py+dy*30),OFF,2,0.4)
    # motif: thermal progress strip, heats up with time
    y=1236; p=t/TOT; wv=int((X1-X0)*p)
    panel(b,(X0,y-1,X1,y+7),1,fill=(40,44,50),fa=0.75,r=4)
    if wv>2: comp(b,TB.crop((0,0,wv,6)),(X0,y))
    lay=Image.new('RGBA',(16,16),(0,0,0,0)); ImageDraw.Draw(lay).ellipse((2,2,14,14),fill=OFF+(255,)); comp(b,lay,(X0+wv-8,y-5))
    TOP.append(('strip',(X0,1228,X1,1246)))
CAPY=1140
def caption(b,t):
    c=[x for x in CAP if t>=x[0]]
    if not c: return
    a0,s,key=c[-1]; p=eob(P(t,a0,0.22),1.2) if a0>0 else 1
    sz=50; f=font('mr',sz)
    while f.getlength(s)>X1-X0-70: sz-=2; f=font('mr',sz)
    l,tp,r,bt=f.getbbox(s,anchor='mm'); hw=(r-l)/2+30
    hh=44*(0.9+0.1*p); box=(CX-hw,CAPY-hh,CX+hw,CAPY+hh)
    panel(b,box,1,fill=GRA,fa=0.88,r=44)
    a=clamp(0.45+0.55*P(t,a0,0.1)) if a0>0 else 1
    if key and key in s:
        x=CX-(r-l)/2; parts=s.split(' ')
        for wd in parts:
            ww=f.getlength(wd); col=(ICE if wd in COOL else HOT) if key==wd else OFF
            text(b,wd,'mr',sz,x+ww/2,CAPY,col,a,shadow=False,name='cap',cont=box,pad=8,maxw=9999)
            x+=ww+f.getlength(' ')
    else: text(b,s,'mr',sz,CX,CAPY,OFF,a,shadow=False,name='cap',cont=box,pad=8)
    TOP.append(('caption',box))
def title(b,t,s,t0,cy,size,col=OFF,name='title',t1=None,instant=False,k='ro'):
    a=1 if instant else clamp(P(t,t0,0.12))
    if t1: a*=1-P(t,t1-0.2,0.2)
    sc=1 if instant else 0.88+0.12*eob(P(t,t0,0.3),1.4)
    ink,sz=text(b,s,k,size*sc,CX,cy,col,a,name=name,minsz=34)
    TOP.append((name,ink)); return ink
def counter(b,t,t0,d,v0,v1,fmt,cy,lab,t_end,sub=None,col=OFF):
    a=clamp(P(t,t0-0.1,0.12))*(1-P(t,t_end-0.2,0.2))
    if a<=0: return
    p=eio(P(t,t0,d)); v=v0+(v1-v0)*p; iv=int(round(v)) if p<1 else v1
    s=fmt(iv); ink,_=text(b,s,'ro',140,CX,cy,col,a,name='count'); TOP.append(('count',(X0+10,cy-95,X1-10,cy+95)))
    comp(b,TB,(X0,cy-108),a*0.9); comp(b,TB,(X0,cy+102),a*0.9)
    ink2,_=text(b,lab,'mono',30,CX,cy+150,ICE,a,name='countlab'); TOP.append(('countlab',ink2))
    if sub:
        ink3,_=text(b,sub,'mono',24,CX,cy+198,DIM if False else OFF,a*0.9,name='countsub'); TOP.append(('countsub',ink3))
def avcard(b,t,t0,t1):
    a=clamp(min((t-t0)/0.15,(t1-t)/0.15))
    if a<=0: return
    CW,CH=640,740; fx,fy=656,760; cw,ch=780,900
    im=avframe(t,'M').crop((fx-cw//2,fy-ch//2,fx+cw//2,fy+ch//2)).resize((CW,CH),Image.LANCZOS)
    a_=np.asarray(im).astype(np.float32)/255; a_=G*0.6+a_*(1-G*0.6); im=Image.fromarray((a_.clip(0,1)*255).astype(np.uint8)).convert('RGBA')
    m=Image.new('L',(CW,CH),0); ImageDraw.Draw(m).rounded_rectangle((0,0,CW-1,CH-1),radius=34,fill=255); im.putalpha(m)
    s=0.92+0.08*eob(P(t,t0,0.25),1.4)
    if s!=1: im=im.resize((int(CW*s),int(CH*s)),Image.BICUBIC)
    cx,cy=CX,710; w2,h2=im.width//2,im.height//2
    sh=Image.new('RGBA',(im.width+80,im.height+80),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((40,52,im.width+40,im.height+52),34,fill=(0,0,0,150))
    comp(b,sh.filter(ImageFilter.GaussianBlur(18)),(cx-w2-40,cy-h2-40),a); comp(b,im,(cx-w2,cy-h2),a)
    rl=Image.new('RGBA',(im.width+8,im.height+8),(0,0,0,0)); ImageDraw.Draw(rl).rounded_rectangle((2,2,im.width+5,im.height+5),36,outline=OFF+(200,),width=3)
    comp(b,rl,(cx-w2-4,cy-h2-4),a)
    TOP.append(('card',(cx-CW//2-6,cy-CH//2-6,cx+CW//2+6,cy+CH//2+6)))
def chip(b,t,t0,t1,s,y,col=ICE,name='src'):
    a=clamp(P(t,t0,0.15))*(1-P(t,t1-0.2,0.2))
    if a<=0: return
    f=font('mono',22); w=f.getlength(s)+36; box=(CX-w/2,y-22,CX+w/2,y+22)
    panel(b,box,a,fa=0.85,edge=col,r=22); text(b,s,'mono',22,CX,y,col,a,shadow=False,name=name,cont=box,pad=5); TOP.append((name,box))
def strike(b,t,t0,ink,col=ICE):
    p=eo(P(t,t0,0.22))
    if p<=0: return
    x0,y0,x1,y1=ink; y=(y0+y1)/2; line(b,(x0-14,y+6),(x0-14+(x1-x0+28)*p,y-6),col,12)
def chat(b,t,t0,t1):
    a=clamp(P(t,t0,0.18))*(1-P(t,t1-0.2,0.2))
    if a<=0: return
    box=(X0+30,470,X1-30,800); panel(b,box,a,fa=0.86,edge=ICE,r=28)
    text(b,'ЧАТ-БОТ GROK · xAI','mono',26,0,520,ICE,a,shadow=False,left=box[0]+36,name='chath',cont=box,pad=8)
    line(b,(box[0]+30,556),(box[2]-30,556),DIM,2,a*0.6)
    bb=(box[0]+36,600,box[0]+330,680); panel(b,bb,a,fill=(52,58,66),fa=1,r=30)
    for i in range(3):
        ph=(t*3.2-i*0.33)%1; r=10+4*max(0,math.sin(ph*math.pi))
        lay=Image.new('RGBA',(40,40),(0,0,0,0)); ImageDraw.Draw(lay).ellipse((20-r,20-r,20+r,20+r),fill=OFF+(int(150+100*max(0,math.sin(ph*math.pi))),))
        comp(b,lay,(bb[0]+70+i*70-20,640-20),a)
    text(b,'печатает…','mr',28,0,730,DIM,a,shadow=False,left=box[0]+36,name='chatt',cont=box,pad=8)
    TOP.append(('chat',box))
def vacancy(b,t,t0,t1):
    a=clamp(P(t,t0,0.18))*(1-P(t,t1-0.2,0.2))
    if a<=0: return
    p=eob(P(t,t0,0.3),1.3); dy=(1-p)*40
    box=(X0+20,430+dy,X1-20,760+dy); panel(b,box,a,fa=0.9,edge=ICE,r=24)
    text(b,'ВАКАНСИЯ · SPACEX','mono',24,0,480+dy,ICE,a,shadow=False,left=box[0]+34,name='v1',cont=box,pad=8)
    text(b,'Mechanical Engineer','mr',42,0,560+dy,OFF,a,shadow=False,left=box[0]+34,name='v2',cont=box,pad=8,maxw=box[2]-box[0]-70)
    text(b,'Data Center MEP Systems','mr',34,0,620+dy,OFF,a,shadow=False,left=box[0]+34,name='v3',cont=box,pad=8,maxw=box[2]-box[0]-70)
    text(b,'Starbase, Texas','mono',26,0,700+dy,DIM,a,shadow=False,left=box[0]+34,name='v4',cont=box,pad=8)
    TOP.append(('vac',(box[0],430,box[2],800)))
def scene(b,t):
    if t<2.90:
        title(b,t,'ЗАЧЕМ SPACEX',0,480,92,instant=True,name='h1'); title(b,t,'ЭЛЕКТРОСТАНЦИЯ?',0,600,80,col=HOT,instant=True,name='h2')
    elif t<4.62:
        ink=title(b,t,'НОВАЯ РАКЕТА?',2.96,520,84,name='rk'); strike(b,t,3.62,ink)
        if t>=3.62: title(b,t,'НЕТ',3.70,660,110,col=ICE,name='net')
    elif 9.72<=t<12.70:
        if t>=10.34: title(b,t,'ДАТА-ЦЕНТР',10.34,520,110,col=OFF,name='dc')
    elif 12.70<=t<15.02:
        if t>=13.54: title(b,t,'УЧИТ ИИ',13.54,520,110,col=HOT,name='ai')
    elif 15.02<=t<17.30: avcard(b,t,15.02,17.30)
    elif 17.30<=t<19.72:
        if t>=17.68: title(b,t,'SPACEX + xAI',17.68,520,100,name='buy'); chip(b,t,18.26,19.72,'СДЕЛКА · 02.02.2026',640,col=ICE,name='date')
    elif 19.72<=t<21.60: chat(b,t,19.80,21.60)
    elif 21.60<=t<24.30: chip(b,t,21.72,24.30,'ОЦЕНКА SEMIANALYSIS',520,col=ICE,name='sa')
    elif 24.30<=t<26.60:
        if t>=25.82: title(b,t,'> 1 ГВт',25.82,540,160,col=OFF,name='gw'); chip(b,t,26.0,26.60,'ДВА ОБЪЕКТА ВМЕСТЕ',700,col=OFF,name='two')
    elif 26.60<=t<28.62: counter(b,t,27.30,0.8,0,500000,lambda v:f'{v:,}'.replace(',',' '),560,'ЧАЙНИКОВ ПО 2 кВт',28.62)
    elif 28.62<=t<31.10:
        if t>=29.72: title(b,t,'ВЫКЛ?',29.80,560,130,col=ICE,name='off')
    elif 31.10<=t<33.10:
        if t>=31.96: title(b,t,'СЕТИ МАЛО',31.96,540,100,name='grid')
    elif 33.10<=t<35.40:
        chip(b,t,33.72,35.40,'THE 956 REPORT · 08.09.2026',520,col=ICE,name='956')
    elif 35.40<=t<38.90:
        if t>=36.9: counter(b,t,37.02,0.6,0,35,str,560,'ГАЗОВЫХ ТУРБИН',38.90,sub='~748 МВт · ЗАЯВКА, НЕ РАЗРЕШЕНИЕ',col=HOT)
    elif 38.90<=t<41.80:
        if t>=41.20: title(b,t,'ТЕПЛО',41.20,540,140,col=HOT,name='heat')
    elif 41.80<=t<45.45: vacancy(b,t,42.62,45.45)
    elif 45.45<=t<47.95:
        if t>=46.62: title(b,t,'СОГРЕТЬ',46.62,480,100,name='m1')
        if t>=47.14: title(b,t,'МАРС',47.14,620,140,col=HOT,name='m2')
    elif 47.95<=t<50.45:
        if t>=48.70: title(b,t,'ОХЛАДИТЬ',48.70,480,100,name='t1')
        if t>=49.24: title(b,t,'ТЕХАС',49.24,620,140,col=ICE,name='t2')
CUTS=[s[0] for s in S[1:]]
THERM={26.60,38.90,45.45}
def trans(im,t):
    for t0 in CUTS:
        dt=t-t0
        if -0.001<=dt<0.18:
            k=1-dt/0.18
            if t0 in THERM:
                a=np.asarray(im.convert('RGB')).astype(np.float32); l=(a.mean(2)).clip(0,255).astype(np.uint8)
                th=LUT[l]; a=a*(1-0.8*k)+th*0.8*k; im=Image.fromarray(a.clip(0,255).astype(np.uint8)).convert('RGBA'); continue
            z=1+0.06*k; c=im.resize((int(W*z),int(H*z)),Image.BICUBIC); im=c.crop(((c.width-W)//2,(c.height-H)//2,(c.width-W)//2+W,(c.height-H)//2+H))
            a=np.asarray(im).copy(); sh=(np.sin(np.arange(H)/23.0+t*40)*14*k).astype(int)
            for y0 in range(0,H,8): a[y0:y0+8]=np.roll(a[y0:y0+8],sh[y0],axis=1)
            im=Image.fromarray(a)
    return im
def frame(f):
    REG.clear(); TOP.clear(); t=f/FPS
    k=cur(t); key=S[k][1]
    b=grade(shot(t,k),t,avatar=key.startswith('AV'))
    if key=='cables': b=Image.blend(b,Image.new('RGBA',(W,H),GRA+(255,)),0.35)
    comp(b,GR[f%6],(0,0))
    scene(b,t); hud(b,t,k); caption(b,t)
    check(f)
    return trans(b,t).convert('RGB')
if __name__=='__main__':
    a,bb,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
    if out=='check':
        for f in range(a,min(bb,NF)): frame(f)
        print('ok',a,bb,sorted(set(WARN))); sys.exit()
    if out.endswith('.jpg') or out.endswith('.png'): frame(a).save(out); sys.exit()
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','25','-i','-','-c:v','ffv1','-level','3','-pix_fmt','yuv444p',out],stdin=subprocess.PIPE)
    try:
        for f in range(a,min(bb,NF)): p.stdin.write(frame(f).tobytes())
    finally: p.stdin.close(); p.wait()
    if WARN: print('warn',sorted(set(WARN)))
