import sys,os,json,math,subprocess,random,numpy as np
from multiprocessing import Pool
from PIL import Image,ImageDraw,ImageFilter,ImageOps,ImageEnhance
from scipy.io import wavfile
from lib import *
R='/workspace/nuke/b/'; FT='/workspace/nuke/footage/'
TEAL=(63,206,194); DARK=(11,15,23)
WORDS=json.load(open('/workspace/nuke/v/words.json')); ONS=[w[1] for w in WORDS]
sr,vo=wavfile.read('/workspace/nuke/v/vo.wav'); vo=vo.astype(np.float32)/32768
DUR=len(vo)/sr; TOT=50.28; NF=int(round(TOT*25))
ENV=np.array([float(np.sqrt(np.mean(vo[int(f/25*sr):int((f+1)/25*sr)]**2)+1e-12)) if int(f/25*sr)<len(vo) else 0 for f in range(NF+2)])
ENV=np.clip(ENV/np.percentile(ENV,95),0,1.2)
_M=json.load(open('/workspace/nuke/v/seg/meta.json')); SEGS=[(k,_M[k]['t0'],_M[k]['t1']) for k in 'ABC']
LAG=float(os.environ.get('LAG','0'))
NFS={k:len(os.listdir(R+f'av_{k}')) for k,_,_ in SEGS if os.path.isdir(R+f'av_{k}')}
def P(t,a,d): return clamp((t-a)/d)
def avframe(t):
    for k,a,b in SEGS:
        if a-0.001<=t<=b+0.4 and k in NFS:
            i=int(round((t-a+LAG)*25))+1; i=max(1,min(i,NFS[k])); return Image.open(R+f'av_{k}/f{i:04d}.jpg').convert('RGB')
    return None
FACE=(600,700)
def av_full(t,z=1.0):
    im=avframe(t)
    if im is None: return Image.new('RGB',(W,H),VOID)
    if z==1.0: return im
    a=1/z; cx,cy=FACE
    return im.transform((W,H),Image.AFFINE,(a,0,cx*(1-a),0,a,cy*(1-a)),Image.BICUBIC)
_cm={}
def cmask(D):
    if D not in _cm:
        m=Image.new('L',(D*3,D*3),0); ImageDraw.Draw(m).ellipse((0,0,D*3-1,D*3-1),fill=255); _cm[D]=m.resize((D,D),Image.LANCZOS)
    return _cm[D]
def ring(D,t,env):
    R_=D/2; S=int(D*1.9); c=S/2; sc=D/640
    lay=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for o in ONS:
        q=(t-o)/0.55
        if 0<=q<1:
            rr=R_*(1.04+0.28*eo(q)); d.ellipse((c-rr,c-rr,c+rr,c+rr),outline=PINK+(int(150*(1-q)),),width=max(2,int(5*(1-q)*sc)+1))
    for rm,sp,ln,col,wd in [(1.15,60,110,MAG,7),(1.21,-45,70,GOLD,4)]:
        for m in range(2):
            a0=t*sp*(1+0.5*env)+m*180
            d.arc((c-R_*rm,c-R_*rm,c+R_*rm,c+R_*rm),a0,a0+ln,fill=col+(230,),width=int(wd*sc)+1)
    g=lay.filter(ImageFilter.GaussianBlur(10*sc+2))
    ml=Image.new('RGBA',(S,S),(0,0,0,0)); md=ImageDraw.Draw(ml)
    md.ellipse((c-R_*1.03,c-R_*1.03,c+R_*1.03,c+R_*1.03),outline=RED+(255,),width=int((12+7*env)*sc)+2)
    gm=ml.filter(ImageFilter.GaussianBlur(20*sc+2)); gm.putalpha(gm.getchannel('A').point(lambda v:min(255,int(v*2))))
    md.ellipse((c-R_,c-R_,c+R_,c+R_),outline=(255,225,230,235),width=max(2,int(3*sc)))
    out=Image.alpha_composite(gm,g); out=Image.alpha_composite(out,lay); return Image.alpha_composite(out,ml)
def circle(base,t,f,cx,cy,D,t0=None):
    if t0 is not None: D=D*eob(P(t,t0,0.35),1.2)
    D=int(D)
    if D<40: return
    im=avframe(t)
    if im is None: return
    sq=im.crop((170,280,1030,1140)).resize((D,D),Image.LANCZOS).convert('RGBA'); sq.putalpha(cmask(D))
    rl=ring(D,t,float(ENV[min(f,len(ENV)-1)])); comp(base,rl,(cx-rl.width/2,cy-rl.height/2)); comp(base,sq,(cx-D/2,cy-D/2))
_fc={}
def foot(sid,t,t0,z0=1.0,z1=1.08,cx=.5,cy=.5,speed=1.0):
    d=R+'shots/'+sid+'/'; n=len(os.listdir(d)); i=min(n,max(1,int(round((t-t0)*25*speed))+1))
    im=Image.open(d+f'f{i:04d}.jpg').convert('RGB'); z=z0+(z1-z0)*P(t,t0,3)
    if z!=1: 
        a=1/z; im=im.transform((W,H),Image.AFFINE,(a,0,W*cx*(1-a),0,a,H*cy*(1-a)),Image.BICUBIC)
    return im.convert('RGBA')
def grade(im,sat=0.85):
    im=ImageEnhance.Color(im.convert('RGB')).enhance(sat); im=ImageEnhance.Contrast(im).enhance(1.08)
    a=np.asarray(im).astype(np.float32); a[...,0]=a[...,0]*1.04+6; a[...,2]=a[...,2]*1.08+10; a[...,1]*=0.96
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
_img={}
def still(name,box=None,sat=0.85):
    k=(name,box)
    if k not in _img:
        im=Image.open(FT+name).convert('RGB')
        if box: im=im.crop(box)
        _img[k]=grade(im,sat)
    return _img[k]
def kb(im,t,t0,d,z0,z1,cx=.5,cy=.5,fill=True,px=0.0,py=0.0):
    # sub-pixel ken burns via affine (no integer resize stepping)
    iw,ih=im.size; s=max(W/iw,H/ih) if fill else min(W/iw,H/ih)
    q=eio(P(t,t0,d)); z=z0+(z1-z0)*q; s*=z
    ox=iw*cx+px*q*iw; oy=ih*cy+py*q*ih
    a=1/s
    out=im.transform((W,H),Image.AFFINE,(a,0,ox-W/2*a,0,a,oy-H/2*a),Image.BICUBIC,fillcolor=VOID)
    return out.convert('RGBA')
def bg_void(t):
    b=Image.new('RGBA',(W,H),VOID+(255,)); d=ImageDraw.Draw(b)
    off=(t*25)%120
    for y in range(-120,H+120,120): d.line([(0,y+off),(W,y+off)],fill=(28,24,36,255),width=2)
    for x in range(0,W,120): d.line([(x,0),(x,H)],fill=(28,24,36,255),width=2)
    return b
def paper(w,h,seed=1):
    rs=np.random.RandomState(seed); n=rs.rand(h//3+1,w//3+1).astype(np.float32)
    n=np.asarray(Image.fromarray((n*255).astype(np.uint8)).resize((w,h),Image.BICUBIC)).astype(np.float32)/255
    base=np.array([236,226,214],np.float32); a=base*(0.94+0.08*n[...,None]); return Image.fromarray(a.clip(0,255).astype(np.uint8)).convert('RGBA')
PAP={}
def plate(base,box,seed=1,alpha=1.0,dark=False):
    x0,y0,x1,y1=[int(v) for v in box]; w,h=x1-x0,y1-y0
    if w<4 or h<4: return
    k=(w,h,seed,dark)
    if k not in PAP:
        p=paper(w,h,seed) if not dark else Image.new('RGBA',(w,h),(24,18,30,235))
        m=Image.new('L',(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),22,fill=255); p.putalpha(m if not dark else m.point(lambda v:int(v*0.92))); PAP[k]=p
    sh=Image.new('RGBA',(w+60,h+60),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((30,40,w+30,h+40),22,fill=(0,0,0,120)); sh=sh.filter(ImageFilter.GaussianBlur(14))
    comp(base,sh,(x0-30,y0-30),alpha); comp(base,PAP[k],(x0,y0),alpha)
INK=(30,20,34)
# ---------- code-drawn depth cues ----------
def cube(base,t,t0,cx,cy,s,build=True):
    a=t*0.9; b=0.5+0.15*math.sin(t*0.7)
    V=[(x,y,z) for x in(-1,1) for y in(-1,1) for z in(-1,1)]
    def pr(v):
        x,y,z=v; x,z=x*math.cos(a)-z*math.sin(a),x*math.sin(a)+z*math.cos(a); y,z=y*math.cos(b)-z*math.sin(b),y*math.sin(b)+z*math.cos(b)
        k=4/(4+z); return (cx+x*s*k,cy+y*s*k)
    E=[(i,j) for i in range(8) for j in range(i+1,8) if sum(abs(V[i][q]-V[j][q]) for q in range(3))==2]
    n=len(E); p=P(t,t0,0.9) if build else 1
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for e,(i,j) in enumerate(E):
        q=clamp(p*n-e)
        if q<=0: continue
        A=pr(V[i]); B=pr(V[j]); Bq=(A[0]+(B[0]-A[0])*q,A[1]+(B[1]-A[1])*q)
        d.line([A,Bq],fill=(TEAL if e%3 else GOLD)+(255,),width=7)
    g=lay.filter(ImageFilter.GaussianBlur(12)); comp(base,g,(0,0)); comp(base,lay,(0,0))
def persp(base,t,t0):
    vp=(540,760); d=ImageDraw.Draw(base)
    for k in range(-6,7):
        d.line([vp,(540+k*260,H)],fill=(LILAC if k%2 else VIOL)+(255,),width=4)
    for i in range(10):
        y=760+(H-760)*((i+((t-t0)*1.2)%1)/10)**2
        d.line([(0,y),(W,y)],fill=(55,40,70,255),width=2)
    # equal posts receding
    for i,z in enumerate([1.0,0.6,0.38,0.25]):
        if t<t0+0.12*i: continue
        h=700*z; x=540+380*z; y=760+(H-760)*z*0.95
        rrect(base,(x-30*z,y-h,x+30*z,y),8,fill=GOLD+(255,))
        rrect(base,(1080-x-30*z,y-h,1080-x+30*z,y),8,fill=RED+(255,))
def shadows(base,t,t0):
    la=math.pi*(0.15+0.7*P(t,t0,0.5)); lx,ly=math.cos(la),-0.6
    cx,cy,rr=540,900,230
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).ellipse((cx-260-lx*150,1180,cx+260-lx*150,1290),fill=(0,0,0,200)); comp(base,sh.filter(ImageFilter.GaussianBlur(18)),(0,0))
    yy,xx=np.mgrid[-rr:rr,-rr:rr].astype(np.float32)/rr; m=xx**2+yy**2<1; zz=np.sqrt(np.clip(1-xx**2-yy**2,0,1))
    L=np.array([lx,ly,0.7]); L/=np.linalg.norm(L); sh_=np.clip(xx*L[0]+yy*L[1]+zz*L[2],0,1)
    col=np.stack([MAG[i]*0.25+(PINK[i]-MAG[i]*0.25)*sh_ for i in range(3)],-1)
    a=np.dstack([col,m*255]).astype(np.uint8); comp(base,Image.fromarray(a,'RGBA'),(cx-rr,cy-rr))
def occl(base,t,t0):
    p=eio(P(t,t0,0.8)); x=260+560*p
    rrect(base,(180,620,640,1080),28,fill=TEAL+(255,))
    rrect(base,(x-230,820,x+230,1280),28,fill=RED+(255,)) if p<0.5 else None
    if p>=0.5:
        rrect(base,(x-230,820,x+230,1280),28,fill=RED+(255,)); rrect(base,(180,620,640,1080),28,fill=TEAL+(255,))
def ames_room(base,t,t0):
    d=ImageDraw.Draw(base)
    poly=[(140,520),(940,520),(940,1320),(140,1320)]
    d.polygon(poly,fill=(36,22,46,255)); d.line(poly+[poly[0]],fill=LILAC+(255,),width=5)
    for i in range(1,8): d.line([(140,1320-i*16),(940,1320-i*16)],fill=(60,40,80,255),width=2)
    # perceived same room, giant left, dwarf right
    p=eob(P(t,t0,0.4),1.3)
    def person(x,yb,h,col):
        h*=p; hd=h*0.16; d.ellipse((x-hd,yb-h,x+hd,yb-h+hd*2),fill=col+(255,)); d.rounded_rectangle((x-hd*1.3,yb-h+hd*2.1,x+hd*1.3,yb),int(hd*0.6),fill=col+(255,))
    person(330,1300,700,RED); person(760,1300,290,TEAL)
def dots(base,t,t0,box):
    x0,y0,x1,y1=box; n=10; sx=(x1-x0)/n; k=int(clamp((t-t0)/0.8)*100)
    d=ImageDraw.Draw(base)
    for i in range(100):
        r_,c_=divmod(i,10); cx=x0+sx*(c_+.5); cy=y0+sx*(r_+.5); lit=i in (12,27,33,48,61,76,89)
        if i>k: continue
        col=RED if (lit and t>t0+0.9) else (150,130,150)
        rr=sx*0.32*(1.25 if lit and t>t0+0.9 else 1); d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=col+(255,))
# ---------- captions ----------
CAP=[(0.0,'ЗАКРОЙ ОДИН ГЛАЗ'),(1.32,'ПРЯМО СЕЙЧАС'),(2.24,'МИР СТАЛ ПЛОСКИМ?'),(3.32,'ПОЧТИ НЕТ'),(4.16,'А ДОЛЖЕН БЫЛ'),(5.28,'СЕТЧАТКА'),(6.02,'ТОНЬШЕ МИЛЛИМЕТРА'),(7.58,'КАРТИНКА ДВУМЕРНАЯ'),(8.94,'КАК ЭТОТ ЭКРАН'),
(9.82,'ГЛУБИНУ'),(10.2,'ДОСТРАИВАЕТ МОЗГ'),(11.52,'ГЛАЗА В 6 СМ'),(13.16,'ДРУГ ОТ ДРУГА'),(14.14,'ДВЕ КАРТИНКИ'),(15.96,'СТЕРЕОЗРЕНИЕ'),(17.38,'НО ПОДВОХ'),(18.26,'ТЫ ЗАКРЫЛ ГЛАЗ'),(19.28,'А ОБЪЁМ ОСТАЛСЯ'),(20.38,'ЗАПАСНЫЕ ПОДСКАЗКИ'),
(22.1,'ПЕРСПЕКТИВА'),(23.2,'ТЕНИ'),(23.68,'КТО КОГО ЗАСЛОНЯЕТ'),(24.76,'СДВИГ ФОНА'),(26.04,'ИХ МОЖНО ВЗЛОМАТЬ'),(27.24,'КОМНАТА ЭЙМСА'),(28.16,'ОДИНАКОВЫЕ ЛЮДИ'),(29.36,'ВЕЛИКАН И КАРЛИК'),(30.52,'ВОГНУТАЯ МАСКА'),(31.44,'КАЖЕТСЯ ВЫПУКЛОЙ'),
(32.9,'ОКОЛО 7% ВЗРОСЛЫХ'),(34.56,'БЕЗ СТЕРЕОЗРЕНИЯ'),(36.14,'И МНОГИЕ НЕ ЗНАЮТ'),(37.26,'МОЙ МОЗГ РЕНДЕРИТ'),(38.42,'В РЕАЛЬНОМ ВРЕМЕНИ'),(39.38,'НОУТБУК ВСПОТЕЛ'),(41.24,'ТЕСТ'),(41.54,'ОДНИМ ГЛАЗОМ'),(42.26,'СВЕДИ ПАЛЬЦЫ'),(43.66,'ПРОМАХНУЛСЯ — А'),(45.0,'ПОПАЛ — Б'),
(45.98,'ДАЛЬШЕ — НОВЫЕ ОБМАНЫ'),(48.0,'ПОДПИШИСЬ')]
KEYW={'СТЕРЕОЗРЕНИЕ','НО ПОДВОХ','ПОДПИШИСЬ','ТЕСТ','ВЕЛИКАН И КАРЛИК','ИХ МОЖНО ВЗЛОМАТЬ'}
def caption(base,t,y):
    cur=None
    for i,(a,s) in enumerate(CAP):
        if t>=a: cur=(i,a,s)
    if cur is None: return
    i,a,s=cur; p=t-a; sc=0.86+0.14*eob(P(t,a,0.18),1.6)
    key=s in KEYW; col=GOLD if key else HI
    size=104 if len(s)<14 else 84
    txt(base,s,540,y,size*sc,'disp',fill=col,stroke=9,sfill=(10,8,14),glow=(MAG if key else VIOL),gr=18,ga=0.6)
COV=None
def cover():
    b=bg_void(0).convert('RGBA'); d=ImageDraw.Draw(b)
    for k in range(-6,7): d.line([(540,700),(540+k*300,H)],fill=VIOL+(255,),width=3)
    m=Image.open('/workspace/ref_markus.png').convert('RGBA')
    gl=Image.new('RGBA',m.size,MAG+(255,)); gl.putalpha(m.getchannel('A').filter(ImageFilter.GaussianBlur(40)).point(lambda v:int(v*0.6)))
    comp(b,gl,(0,260)); comp(b,m,(0,260))
    txt(b,'ТЫ ВИДИШЬ',540,250,150,'disp',fill=HI,stroke=10,sfill=(10,8,14),glow=VIOL)
    txt(b,'В 2D',540,420,230,'disp',fill=RED,stroke=12,sfill=(10,8,14),glow=MAG,gr=30)
    plate(b,(150,1560,930,1700),3); txt(b,'А МОЗГ ДОРИСОВЫВАЕТ 3D',540,1632,62,'disp',fill=INK)
    return b
VIG=None
def vign():
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); r=np.sqrt(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.72))**2)
    a=np.clip((r-0.55)*1.3,0,1)*200; z=np.zeros((H,W,4),np.uint8); z[...,3]=a.astype(np.uint8); return Image.fromarray(z,'RGBA')
def stop(base,v):
    if v<=0: return base
    g=ImageOps.grayscale(base.convert('RGB')).convert('RGBA'); b=Image.blend(base.convert('RGBA'),g,0.7*v); comp(b,Image.new('RGBA',(W,H),(6,4,10,int(255*0.4*v))),(0,0)); return b
def flash(base,t,tf,amp=0.8,d=0.14):
    if 0<=t-tf<d: comp(base,Image.new('RGBA',(W,H),(243,226,244,int(255*amp*(1-(t-tf)/d)))),(0,0))
def glitch(im,t,k):
    a=np.asarray(im.convert('RGB')).copy(); rs=random.Random(int(t*30))
    s=int(18*k); a[...,0]=np.roll(a[...,0],s,1); a[...,2]=np.roll(a[...,2],-s,1)
    for _ in range(int(6*k)):
        y=rs.randint(0,H-60); h=rs.randint(10,60); a[y:y+h]=np.roll(a[y:y+h],rs.randint(-80,80),1)
    return Image.fromarray(a).convert('RGBA')
