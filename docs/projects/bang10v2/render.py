import sys,os,math,json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from lib import W,H,FPS,clamp,eo,eio,eob,comp,kb,line,stamp
FD='/usr/share/fonts/truetype/sand-box/google/'
# ---- bang10v2 look: "cosmic rewind tape" ----
VOID=(9,11,20); STAR=(226,232,244); GOLD=(240,186,92); RED=(230,57,70); TEAL=(63,206,194)
TOT=59.0; NF=int(round(TOT*FPS)); X0,X1=120,780; CX=450; SAFE=(120,270,780,1250)
_fc={}
def font(k,s):
    s=int(s); key=(k,s)
    if key in _fc: return _fc[key]
    if k=='ant': f=ImageFont.truetype(FD+'Oswald/Oswald-VariableFont_wght.ttf',s); f.set_variation_by_axes([700])
    else: f=ImageFont.truetype(FD+'Geist Mono/GeistMono-VariableFont_wght.ttf',s); f.set_variation_by_axes([600])
    _fc[key]=f; return f
def P(t,a,d): return clamp((t-a)/d)
# ---------- shots ----------
SH='shots/'; AV='/workspace/bang10/av/'
LAG=0.023; SEG={'B':(20.66,25.32),'C':(48.52,51.22),'D':(56.12,58.62)}
# (t0, src, z0, z1, px, py)
S=[(0.00,'30450505',1.0,1.12,0,0),(2.30,'39577076r',1.05,1.2,0,0),(4.86,'39576850r',1.0,1.15,0,0),(6.42,'g_collapse',1.0,1.1,0,0),
(8.64,'39599449',1.0,1.2,0,0),(10.24,'37988519',1.1,1.0,0,0),(12.64,'30424690',1.0,1.12,0,0),(14.70,'img:webb',1.0,1.4,0,0),
(20.66,'39604947',1.0,1.12,0,0),(23.11,'35288148',1.0,1.1,0,0),(25.49,'g_clock',1.0,1.1,0,0),(30.37,'39433173',1.0,1.15,0,0),
(33.13,'30056318',1.15,1.0,0,0),(34.93,'35383824',1.0,1.15,0,0),(37.89,'6916040',1.0,1.1,0,0),(39.25,'38610228',1.0,1.15,0,0),
(42.47,'g_breath',1.0,1.08,0,0),(46.01,'5275699',1.0,1.1,0,0),(47.17,'39266727',1.0,1.2,0,0),(48.52,'40261183',1.05,1.15,0,0),
(51.33,'37723948',1.0,1.1,0,0),(52.55,'img:wmap',1.0,1.6,0,0),(54.11,'18308552',1.0,1.12,0,0),(56.12,'30450505',1.12,1.0,0,0)]
TR={2.30:'rw',4.86:'pz',6.42:'pz',8.64:'fl',10.24:'pz',12.64:'rw',14.70:'pz',20.66:'rw',23.11:'pz',25.49:'rw',30.37:'pz',33.13:'pz',34.93:'rw',37.89:'pz',
39.25:'pz',42.47:'rw',46.01:'pz',47.17:'pz',48.52:'rw',51.33:'pz',52.55:'fl',54.11:'pz',56.12:'rw'}
CAP=[(0.06,'А ЧТО БЫЛО',0),(0.88,'ДО САМОГО НАЧАЛА?',1),(2.30,'ОТМОТАЙ НАЗАД',1),(3.94,'КАК КИНО',0),(4.86,'ГАЛАКТИКИ СБЛИЖАЮТСЯ',0),
(6.42,'ВСЁ СЖИМАЕТСЯ',0),(7.36,'В ГОРЯЧУЮ ТОЧКУ',1),(8.64,None,0),(10.24,None,0),(12.64,'НЕ ВЗРЫВ БОМБЫ',0),(13.82,'В ПУСТОТЕ',0),
(14.70,'КАК ИЗЮМ В ТЕСТЕ',0),(16.86,'РАСТЁТ САМО ПРОСТРАНСТВО',1),(18.28,'ИЗЮМИНКИ РАЗЪЕЗЖАЮТСЯ',0),
(20.76,'ТАК ЧТО БЫЛО ДО?',1),(22.37,'ЧЕСТНО:',0),(23.11,'НИКТО НЕ ЗНАЕТ',1),(24.23,'ЕСТЬ НЕСКОЛЬКО ИДЕЙ',0),
(25.49,None,0),(26.21,'«РАНЬШЕ» ПРОСТО НЕ БЫЛО',0),(28.01,'ВРЕМЯ НАЧАЛОСЬ',1),(29.03,'ВМЕСТЕ СО ВСЕЛЕННОЙ',0),
(30.37,'ЧТО СЕВЕРНЕЕ',0),(31.37,'СЕВЕРНОГО ПОЛЮСА?',1),(33.13,None,0),(33.91,'ДАЛЬШЕ ПУТИ НЕТ',0),
(34.93,None,0),(35.73,'ЗА ДОЛИ СЕКУНДЫ',0),(36.69,'РАЗДУЛАСЬ',1),(37.89,'КАК ВОЗДУШНЫЙ ШАРИК',0),(39.25,'А ДО ЭТОГО?',0),(40.39,'РАЗДУВАНИЕ БЕЗ КОНЦА',1),
(42.47,None,0),(44.79,'СЖАЛАСЬ',0),(45.45,'ОТСКОЧИЛА',1),(46.01,'КАК МЯЧ ОТ ПОЛА',0),(47.17,'И СНОВА РАСШИРЯЕТСЯ',1),
(48.61,'КАКАЯ ИДЕЯ ВЕРНА?',1),(49.85,'ПОКА НЕ ЗНАЕТ НИКТО',0),(51.33,'ОТВЕТ ИЩУТ',0),(52.07,'В САМОМ ДРЕВНЕМ СВЕТЕ',1),
(54.11,'ЕМУ ПОЧТИ 14 МЛРД ЛЕТ',0),(56.12,'А ЧТО БЫЛО',0),(56.69,'ДО САМОГО НАЧАЛА?',1)]
CHAP=[(0,'СЕЙЧАС'),(2.30,'ПЕРЕМОТКА'),(8.64,'T = 0'),(12.64,'РАСШИРЕНИЕ'),(20.76,'ДО T = 0 ?'),(25.49,'ИДЕЯ 1/3'),(34.93,'ИДЕЯ 2/3'),(42.47,'ИДЕЯ 3/3'),(48.61,'ПОИСК'),(56.12,'ДО T = 0 ?')]
_img={}; NFR={}
def vframe(sid,i):
    if sid.startswith('img:'):
        n=sid[4:]
        if n not in _img:
            p=[f for f in os.listdir('img') if f.startswith(n)][0]; im=Image.open('img/'+p).convert('RGB')
            if n=='wmap':  # crop oval center, upright strip
                im=im.crop((1280,300,2560,1620))
            _img[n]=im
        return _img[n]
    if sid not in NFR: NFR[sid]=len(os.listdir(SH+sid))
    n=NFR[sid]; i=i%(2*n-2); i=i if i<n else 2*n-2-i
    return Image.open(SH+sid+'/f%04d.jpg'%(i+1)).convert('RGB')
def cur(t):
    k=0
    for j,s in enumerate(S):
        if t>=s[0]: k=j
    return k
def nxt(k): return S[k+1][0] if k+1<len(S) else TOT
def shot(t,k):
    t0,src,z0,z1,px,py=S[k]; d=nxt(k)-t0
    im=vframe(src,int((t-t0)*FPS))
    if src.startswith('img:'):
        b=kb(im,t,t0,d,z0,z1,px=px,py=py)
        # living still: slow twinkle shimmer
        a=np.asarray(b).astype(np.float32); ph=math.sin(t*7)*0.04; a[...,:3]*=1+ph*np.sin(np.linspace(0,9,H))[:,None,None]
        return Image.fromarray(a.clip(0,255).astype(np.uint8))
    return kb(im,t,t0,d,z0,z1)
# ---------- grade / texture ----------
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
VIG=np.clip((np.sqrt(((xx-W/2)/(W*0.78))**2+((yy-H/2)/(H*0.7))**2)-0.5)*1.2,0,0.75)[...,None]
def grade(im):
    a=np.asarray(im.convert('RGB')).astype(np.float32)/255
    lum=a.mean(2,keepdims=True)
    sh=np.array(VOID,np.float32)/255; hi=np.array([1.0,0.93,0.8],np.float32)
    a=a*(0.82+0.18*hi*lum)+sh*(1-lum)*0.35
    a=a*(1-VIG)+sh*VIG
    return Image.fromarray((a.clip(0,1)*255).astype(np.uint8)).convert('RGBA')
def grainf(i):
    rs=np.random.RandomState(i); n=rs.randint(0,255,(H//2,W//2)).astype(np.uint8); z=np.zeros((H//2,W//2,4),np.uint8); z[...,0]=n;z[...,1]=n;z[...,2]=n;z[...,3]=12
    return Image.fromarray(z).resize((W,H))
GR=[grainf(i) for i in range(6)]
# ---------- layout registry ----------
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
def text(b,s,k,size,cx,cy,col,alpha=1.0,maxw=X1-X0,glow=None,name=None,cont=None,pad=0,minsz=30,left=None,outline=False):
    while size>minsz and font(k,size).getlength(s)>maxw: size-=2
    if font(k,size).getlength(s)>maxw: WARN.append(f'{s} too wide')
    f=font(k,size); l,tp,r,bt=f.getbbox(s,anchor='mm' if left is None else 'lm')
    x=cx if left is None else left
    ink=(x+l,cy+tp,x+r,cy+bt)
    if alpha>0.003:
        g=24 if glow else 6
        lay=Image.new('RGBA',(int(r-l)+2*g+8,int(bt-tp)+2*g+8),(0,0,0,0)); ox,oy=g+4-l,g+4-tp
        if glow:
            gl=Image.new('RGBA',lay.size,(0,0,0,0)); ImageDraw.Draw(gl).text((ox,oy),s,font=f,fill=glow+(255,),anchor='mm' if left is None else 'lm',stroke_width=3)
            lay=Image.alpha_composite(lay,gl.filter(ImageFilter.GaussianBlur(14)))
        d=ImageDraw.Draw(lay)
        if outline: d.text((ox,oy),s,font=f,fill=(0,0,0,0),anchor='mm' if left is None else 'lm',stroke_width=3,stroke_fill=col+(255,))
        else: d.text((ox,oy),s,font=f,fill=col+(255,),anchor='mm' if left is None else 'lm')
        comp(b,lay,(x-ox,cy-oy),alpha)
    REG.append((name or s,ink,cont or SAFE,pad)); return ink,size
def panel(b,box,alpha,fill=VOID,fa=0.72,edge=None,r=14):
    if alpha<=0.003: return
    x0,y0,x1,y1=[int(v) for v in box]; lay=Image.new('RGBA',(x1-x0,y1-y0),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((0,0,x1-x0-1,y1-y0-1),r,fill=fill+(int(255*fa),),outline=(edge+(200,)) if edge else None,width=2)
    comp(b,lay,(x0,y0),alpha)
# ---------- HUD furniture ----------
def hud(b,t):
    ch=[s for a,s in CHAP if t>=a][-1]
    f=font('gm',24); w=f.getlength(ch)+36; box=(X1-w,276,X1,320)
    panel(b,box,1,fill=VOID,fa=0.6,edge=RED if ch=='ПЕРЕМОТКА' or '?' in ch else GOLD,r=22)
    text(b,ch,'gm',24,(box[0]+box[2])/2,298,STAR,name='chip',cont=box,pad=6)
    TOP.append(('chip',box))
    ink,_=text(b,'ДО БОЛЬШОГО ВЗРЫВА','gm',24,0,298,STAR,0.85,left=X0,maxw=box[0]-X0-20,name='hudl'); TOP.append(('hudl',ink))
    # crop marks
    for (px,py,dx,dy) in [(X0-40,250,1,1),(X1+40,250,-1,1),(X0-40,1270,1,-1),(X1+40,1270,-1,-1)]:
        line(b,(px,py),(px+dx*36,py),STAR,3,0.5); line(b,(px,py),(px,py+dy*36),STAR,3,0.5)
def scrub(b,t):
    y=1238; x0p=X0+130
    box=(X0,1222,X1,1250); TOP.append(('scrub',box))
    line(b,(x0p,y),(X1,y),STAR,3,0.7)
    for i in range(10):  # dashed "before" region
        xa=X0+i*13; line(b,(xa,y),(xa+6,y),RED,3,0.8)
    for i in range(6): xm=x0p+(X1-x0p)*i/5; line(b,(xm,y-7),(xm,y+7),STAR,2,0.5)
    if t<2.30: x=X1
    elif t<8.64: x=X1+(x0p-X1)*eio(P(t,2.30,6.3))
    elif t<20.76: x=x0p+(X1-x0p)*eo(P(t,8.64,11.5))
    elif t<25.49 or t>=56.12: x=X0+60+20*math.sin(t*3)
    else: x=X0+60+50*math.sin(t*1.3)
    col=RED if x<x0p-1 else GOLD
    lay=Image.new('RGBA',(60,60),(0,0,0,0)); d=ImageDraw.Draw(lay); d.ellipse((14,14,46,46),fill=col+(255,))
    comp(b,lay.filter(ImageFilter.GaussianBlur(6)),(x-30,y-30),0.9); d2=Image.new('RGBA',(24,24),(0,0,0,0)); ImageDraw.Draw(d2).ellipse((2,2,21,21),fill=(255,255,255,255)); comp(b,d2,(x-12,y-12))
CAPY=1150
def caption(b,t):
    c=[x for x in CAP if t>=x[0]]
    if not c or not c[-1][1]: return
    a0,s,key=c[-1]; p=eob(P(t,a0,0.2),1.3)
    f=font('ant',62); sz=62
    while f.getlength(s)>X1-X0-60: sz-=2; f=font('ant',sz)
    l,tp,r,bt=f.getbbox(s,anchor='mm'); box=(CX+l-28,CAPY+tp-16,CX+r+28,CAPY+bt+16)
    panel(b,box,clamp(p*1.5),fill=VOID,fa=0.78,edge=GOLD if key else None,r=12)
    text(b,s,'ant',sz,CX,CAPY-(1-p)*4,GOLD if key else STAR,clamp(p*1.5),name='cap',cont=box,pad=10)
    TOP.append(('caption',box))
def title(b,t,s,t0,cy,size,col=STAR,glow=GOLD,name='title',outline=False,t1=None):
    a=clamp(P(t,t0,0.15)); 
    if t1: a*=1-P(t,t1-0.2,0.2)
    sc=0.82+0.18*eob(P(t,t0,0.3),1.5)
    ink,sz=text(b,s,'ant',size*sc,CX,cy,col,a,glow=glow,name=name,outline=outline,minsz=40)
    TOP.append((name,ink)); return ink
# ---------- scenes ----------
def counter(b,t):   # 10.24-12.64 : 13,8 billion years, rolls 0.95 s
    t0=10.40; p=eio(P(t,t0,0.95)); v=13.8*p
    a=clamp(P(t,10.24,0.15))*(1-P(t,12.44,0.2))
    s=f'{v:.1f}'.replace('.',',')
    # picker-wheel feel: fractional digit slides
    frac=(v*10)%1 if p<1 else 0
    f=font('ant',230); cy=560
    ink,_=text(b,s,'ant',230,CX,cy-frac*30,STAR,a,glow=GOLD,name='count'); TOP.append(('count',(X0+60,cy-130,X1-60,cy+130)))
    line(b,(X0+80,cy-138),(X1-80,cy-138),GOLD,3,a*0.7); line(b,(X0+80,cy+136),(X1-80,cy+136),GOLD,3,a*0.7)
    ink2,_=text(b,'МЛРД ЛЕТ НАЗАД','gm',40,CX,cy+190,GOLD,a,name='countlab'); TOP.append(('countlab',ink2))
def notbomb(b,t):
    stamp(b,'НЕ БОМБА',CX,560,t,13.08,col=RED,size=110,rot=-7)
    if t>=13.08: TOP.append(('stamp',(CX-300,430,CX+300,690)))
def raisins(b,t):  # space itself grows: lattice + markers
    a=clamp(P(t,14.8,0.3))*(1-P(t,20.46,0.2)); 
    if a<=0: return
    g=1+0.9*eio(P(t,16.86,3.0)); cy=640; lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    sp=90*g
    for i in range(-8,9):
        x=CX+i*sp; d.line([(x,cy-420),(x,cy+300)],fill=STAR+(95,),width=2)
        y=cy+i*sp
        if cy-420<=y<=cy+300: d.line([(X0-60,y),(X1+60,y)],fill=STAR+(95,),width=2)
    pts=[(-1.5,-1.2),(1.3,-0.4),(-0.4,1.1)]
    P2=[(CX+u*sp,cy+v*sp) for u,v in pts]
    for i in range(3):
        for j in range(i+1,3): d.line([P2[i],P2[j]],fill=GOLD+(200,),width=3)
    for (x,y) in P2: d.ellipse((x-22,y-22,x+22,y+22),outline=GOLD+(255,),width=4); d.ellipse((x-7,y-7,x+7,y+7),fill=GOLD+(255,))
    comp(b,lay,(0,0),a)
    ink,_=text(b,f'×{g:.1f}'.replace('.',','),'gm',40,X1-70,368,GOLD,a,name='scale'); TOP.append(('scale',ink))
def avbadge(b,t,seg):
    t0,t1=SEG[seg]; a=clamp(min((t-t0)/0.15,(t1-t)/0.15)); sz=250
    i=int(round((t-t0+LAG)*FPS)); d=AV+'f'+seg+'/'; n=len(os.listdir(d)); i=max(0,min(n-1,i))
    im=Image.open(d+'f%04d.jpg'%(i+1)).convert('RGB').crop((250,220,910,880)).resize((sz,sz),Image.LANCZOS).convert('RGBA')
    m=Image.new('L',(sz,sz),0); ImageDraw.Draw(m).ellipse((0,0,sz-1,sz-1),fill=255); im.putalpha(m)
    s=0.8+0.2*eob(P(t,t0,0.25),1.4)
    if s!=1: im=im.resize((int(sz*s),int(sz*s)),Image.BICUBIC)
    cx,cy=CX,880; r=im.width//2
    rl=Image.new('RGBA',(im.width+40,im.height+40),(0,0,0,0)); ImageDraw.Draw(rl).ellipse((8,8,im.width+31,im.height+31),outline=GOLD+(255,),width=6)
    comp(b,rl.filter(ImageFilter.GaussianBlur(5)),(cx-r-20,cy-r-20),a); comp(b,rl,(cx-r-20,cy-r-20),a*0.8); comp(b,im,(cx-r,cy-r),a)
    TOP.append(('badge',(cx-sz//2-20,cy-sz//2-20,cx+sz//2+20,cy+sz//2+20)))
    f=font('gm',24); w=f.getlength('ВЕДУЩИЙ')+32; box=(cx-w/2,cy+sz//2+28,cx+w/2,cy+sz//2+66)
    panel(b,box,a,fill=GOLD,fa=0.95,r=19); text(b,'ВЕДУЩИЙ','gm',24,cx,(box[1]+box[3])/2,VOID,a,name='badgelab',cont=box,pad=4); TOP.append(('badgelab',box))
def northpole(b,t):
    a=clamp(P(t,30.5,0.3))*(1-P(t,32.93,0.2))
    if a<=0: return
    p=eo(P(t,31.37,1.0)); x=CX; y0=760; y1=y0-300*p
    for k in range(12):
        yy_=y0-k*25
        if yy_>y1: line(b,(x,yy_),(x,yy_-12),GOLD,5,a)
    lay=Image.new('RGBA',(60,60),(0,0,0,0)); ImageDraw.Draw(lay).polygon([(30,4),(6,52),(54,52)],fill=GOLD+(255,)); comp(b,lay,(x-30,y1-40),a)
    if t>=31.89: 
        ink,_=text(b,'N','ant',90,x,y1-110,STAR,a*clamp(P(t,31.89,0.15)),glow=GOLD,name='N'); TOP.append(('N',ink))
def rwicon(b,t):
    a=clamp(P(t,2.30,0.15))*(1-P(t,4.66,0.2)); sc=0.8+0.2*eob(P(t,2.30,0.3),1.5); cy=560; s=110*sc
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for k in (0,1):
        x=CX+s*(0.05+k*0.95)
        d.polygon([(x,cy-s*0.8),(x,cy+s*0.8),(x-s*1.1,cy)],fill=RED+(255,))
    g=lay.filter(ImageFilter.GaussianBlur(18)); comp(b,g,(0,0),a*0.8); comp(b,lay,(0,0),a)
    TOP.append(('rw',(CX-s*1.2,cy-s*0.85,CX+s*1.1,cy+s*0.85)))
def scene(b,t):
    if t<2.30: title(b,t,'ДО НАЧАЛА?',0.88,560,190,name='hook')
    elif t<4.86: rwicon(b,t)
    elif 8.64<=t<10.24: title(b,t,'БОЛЬШОЙ','8.7' and 9.12,470,170,name='bb1'); title(b,t,'ВЗРЫВ',9.60,650,230,col=GOLD,glow=RED,name='bb2')
    elif 10.24<=t<12.64: counter(b,t)
    elif 12.64<=t<14.70: notbomb(b,t)
    elif 14.70<=t<20.66: raisins(b,t)
    elif 20.66<=t<25.32:
        if t>=23.11: title(b,t,'НИКТО НЕ ЗНАЕТ',23.11,470,120,name='nk')
        elif t<22.37: title(b,t,'ДО?',20.90,470,200,col=RED,glow=RED,name='do')
        avbadge(b,t,'B')
    elif 25.49<=t<30.37:
        if t<26.21: title(b,t,'ИДЕЯ 1',25.49,520,170,name='i1')
        elif t>=28.01: title(b,t,'ВРЕМЕНИ НЕ БЫЛО',28.01,400,96,name='tm')
    elif 30.37<=t<33.13: northpole(b,t)
    elif 33.13<=t<34.93: title(b,t,'НИЧЕГО',33.13,560,200,outline=True,glow=None,name='nil')
    elif 34.93<=t<35.73: title(b,t,'ИДЕЯ 2',34.93,520,170,name='i2')
    elif 35.73<=t<37.89: title(b,t,'ИНФЛЯЦИЯ',36.69,500,150,col=GOLD,name='inf')
    elif 40.95<=t<42.47: title(b,t,'∞',40.95,520,260,col=GOLD,name='inf2')
    elif 42.47<=t<43.13: title(b,t,'ИДЕЯ 3',42.47,520,170,name='i3')
    elif 44.01<=t<46.01: title(b,t,'ДЫШИТ',44.01,480,180,col=GOLD,name='br')
    elif 48.52<=t<51.22:
        title(b,t,'?',48.61,470,170,col=RED,glow=RED,name='q'); avbadge(b,t,'C')
    elif 52.55<=t<54.11: title(b,t,'ДРЕВНИЙ СВЕТ',52.55,420,120,col=GOLD,name='cmb')
    elif t>=56.12:
        if t<58.62: avbadge(b,t,'D')
        title(b,t,'ДО НАЧАЛА?',56.69,470,150,name='end')
def trans(im,t):
    for t0,ty in TR.items():
        dt=t-t0
        if -0.001<=dt<0.2:
            k=1-dt/0.2
            if ty=='fl': im=Image.blend(im,Image.new('RGBA',(W,H),(255,244,220,255)),0.75*k)
            elif ty=='pz':
                z=1+0.08*k; c=im.resize((int(W*z),int(H*z)),Image.BICUBIC); im=c.crop(((c.width-W)//2,(c.height-H)//2,(c.width-W)//2+W,(c.height-H)//2+H))
            elif ty=='rw':  # tape-rewind slices + chroma split
                a=np.asarray(im).copy(); rs=np.random.RandomState(int(t*100))
                for _ in range(9):
                    y=rs.randint(0,H-80); h=rs.randint(20,120); a[y:y+h]=np.roll(a[y:y+h],int(rs.randint(-140,140)*k),axis=1)
                a[...,0]=np.roll(a[...,0],int(18*k),axis=1); a[...,2]=np.roll(a[...,2],-int(18*k),axis=1)
                im=Image.fromarray(a)
    return im
def frame(f):
    REG.clear(); TOP.clear(); t=f/FPS
    k=cur(t); b=grade(shot(t,k)); comp(b,GR[f%6],(0,0))
    scene(b,t); hud(b,t); scrub(b,t); caption(b,t)
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
