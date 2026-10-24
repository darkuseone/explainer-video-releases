import sys,os,math,random,json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageOps,ImageEnhance
from lib import *
TEAL=(70,214,196); INK=(20,24,30); WARN=(255,196,64)
TOT=59.67; NF=int(round(TOT*FPS))
SH='/workspace/onc10/b/shots/'; FT='/workspace/onc10/footage/'; AV='/workspace/onc10/av/f/'
LAG=0.023; SEG={'A':(0.0,4.70,0.0),'B':(20.75,26.40,5.0)}
X0,X1=120,780; CX=(X0+X1)//2
# ---- shots: (t0, kind, src, off, z0, z1, cx, cy)
S=[(0.0,'av','A',0),(2.40,'v','5883925',0.0,1.05,1.15),(3.50,'v','5883925',3.0,1.35,1.25),(4.80,'v','8852657',0.0,1.0,1.1),(6.20,'v','8852657',4.0,1.3,1.4),
(7.36,'v','8852695',0.0,1.0,1.08),(8.40,'v','8852695',3.0,1.4,1.3),(9.40,'i','bccell.jpg',0,1.0,1.12),(11.15,'i','bccell.jpg',0,1.6,1.9),
(12.70,'v','5453585',0.0,1.0,1.08),(13.70,'v','5453585',4.0,1.4,1.5),(15.06,'i','tcells.png',0,1.0,1.15),(16.60,'v','8326121',5.0,1.2,1.3),
(17.40,'num','49%',0),(19.10,'v','8670930',0.0,1.0,1.1),(20.85,'v','8670930',4.0,1.25,1.35),(23.00,'v','8852383',0.0,1.0,1.1),(24.34,'v','8852695',6.0,1.2,1.3),
(26.50,'v','8326121',0.0,1.0,1.08),(28.20,'dots','grok_sem.jpg',0),(30.10,'i','grok_sem.jpg',0,1.3,1.5),(32.35,'num','3 ГОДА',0),(33.20,'v','5722113',1.0,1.0,1.1),
(34.65,'v','8852383',5.0,1.3,1.2),(36.35,'i','grok_cart.jpg',0,1.0,1.12),(37.65,'i','grok_cart.jpg',0,1.5,1.7),(39.60,'v','8852657',7.0,1.1,1.2),
(41.05,'i','grok_cart.jpg',0,1.2,1.1),(43.20,'mam','mammogram.jpg',0),(45.15,'num','29%',0),(47.80,'v','6236757',0.0,1.0,1.1),
(49.40,'v','8460389',0.0,1.0,1.1),(51.35,'v','8460389',4.0,1.35,1.45),(52.60,'v','5453585',7.0,1.0,1.1),(54.75,'i','tcells.png',0,1.4,1.25),
(56.40,'v','8670930',7.0,1.0,1.1),(57.45,'v','5883925',6.0,1.1,1.2)]
CIRC=[(2.40,4.70,'A'),(20.85,26.40,'B')]
# transition at shot boundary: type
TR={2.40:'punch',3.50:'cut',4.80:'whip',6.20:'cut',7.36:'flash',8.40:'cut',9.40:'glitch',11.15:'punch',12.70:'whip',13.70:'cut',15.06:'flash',16.60:'cut',17.40:'dip',
19.10:'whip',20.85:'glitch',23.00:'cut',24.34:'punch',26.50:'flash',28.20:'dip',30.10:'punch',32.35:'dip',33.20:'cut',34.65:'glitch',36.35:'flash',37.65:'punch',
39.60:'whip',41.05:'cut',43.20:'glitch',45.15:'dip',47.80:'whip',49.40:'flash',51.35:'punch',52.60:'whip',54.75:'glitch',56.40:'cut',57.45:'flash'}
CAP=[(0.06,'ВАКЦИНА ОТ РАКА',0),(1.30,'УЖЕ ЕСТЬ',1),(2.46,'НО ОНА СДЕЛАНА',0),(3.47,'ДЛЯ ОДНОГО ЧЕЛОВЕКА',1),(4.88,'УЧЁНЫЕ ЧИТАЮТ',0),(5.67,'МУТАЦИИ ОПУХОЛИ',1),
(7.36,'И ЗАПИСЫВАЮТ',0),(8.31,'В мРНК',1),(9.41,'ШПАРГАЛКА',1),(10.11,'ДЛЯ ИММУНИТЕТА',0),(11.19,'ВОТ ВРАГ',1),(11.87,'НАЙДИ ЕГО',0),(12.77,'МЕЛАНОМА',1),
(13.70,'5 ЛЕТ НАБЛЮДЕНИЯ',0),(15.06,'С ВАКЦИНОЙ',0),(15.79,'РИСК РЕЦИДИВА',0),(16.60,'ИЛИ СМЕРТИ',0),(17.40,None,0),(19.10,'ЧЕМ С ОДНОЙ',0),(19.70,'ИММУНОТЕРАПИЕЙ',0),
(20.91,'НО ЭТО ФАЗА 2',1),(22.88,'НЕ ЛЕКАРСТВО В АПТЕКЕ',0),(24.34,'ФАЗА 3',1),(25.13,'ИДЁТ ПРЯМО СЕЙЧАС',0),(26.56,'РАК ПОДЖЕЛУДОЧНОЙ',1),(28.20,None,0),
(30.14,'ВАКЦИНА ВЫРАСТИЛА',0),(31.07,'КЛЕТКИ-ОХОТНИКИ',1),(32.35,None,0),(33.22,'ВСЁ ЕЩЁ В КРОВИ',0),(34.69,'ДАЛЬШЕ',0),(35.24,'ЖИВЫЕ ЛЕКАРСТВА',1),
(36.41,'CAR-T КЛЕТКИ',1),(37.68,'ВПЕРВЫЕ',1),(38.19,'В РАНДОМИЗИРОВАННОМ',0),(38.98,'ИСПЫТАНИИ',0),(39.62,'ДОЛЬШЕ БЕЗ РОСТА',0),(41.09,'ТВЁРДОЙ ОПУХОЛИ',0),
(42.19,'РАК ЖЕЛУДКА',1),(43.24,'ИИ НА МАММОГРАФИИ',0),(45.15,None,0),(47.84,'БЕЗ РОСТА',0),(48.41,'ЛОЖНЫХ ТРЕВОГ',1),(49.46,'КАКОЙ РАК',0),(50.01,'ВЗЛОМАЮТ СЛЕДУЮЩИМ?',1),
(51.39,'ПИШИ В КОММЕНТАРИЯХ',1),(52.64,'ОТПРАВЬ ТОМУ, КТО',0),(53.37,'СЧИТАЕТ ЭТО ФАНТАСТИКОЙ',0),(54.75,'И ПОДПИШИСЬ',1),(55.59,'ЧТОБЫ НЕ ПРОПУСТИТЬ',0),
(56.47,'ФАЗУ 3',1),(57.48,'ПОТОМУ ЧТО',0),(57.96,'ГЛАВНОЕ УЖЕ СЛУЧИЛОСЬ',1)]
TAG=[(4.8,'ИСПЫТАНИЕ KEYNOTE-942 · ФАЗА 2'),(12.7,'JCO 2026 · 157 ПАЦИЕНТОВ'),(26.5,'NATURE 2025 · ФАЗА 1'),(34.65,'LANCET 2025 · ФАЗА 2'),(43.2,'LANCET DIG HEALTH 2025'),(49.4,None)]
CH=[(0,'00'),(4.8,'01 / мРНК-ВАКЦИНА'),(26.5,'02 / ПОДЖЕЛУДОЧНАЯ'),(34.65,'03 / CAR-T'),(43.2,'04 / ИИ'),(49.4,'05 / ДАЛЬШЕ')]
_ic={}
def img(path):
    if path not in _ic: _ic[path]=Image.open(path).convert('RGB')
    return _ic[path]
def vframe(sid,i,n=250):
    i=max(0,min(n-1,i)); return img(SH+sid+'/f%04d.jpg'%(i+1)) if False else Image.open(SH+sid+'/f%04d.jpg'%(i+1)).convert('RGB')
def avf(seg,t):
    t0,t1,c0=SEG[seg]; i=int(round((t-t0+c0+LAG)*FPS)); i=max(0,min(265,i)); return Image.open(AV+'f%04d.jpg'%(i+1)).convert('RGB')
def cur_shot(t):
    k=0
    for j,s in enumerate(S):
        if t>=s[0]: k=j
    return k
def nxt(k): return S[k+1][0] if k+1<len(S) else TOT
def darkblur(im,r=18,dk=0.45):
    return ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(r))).enhance(dk)
def shot_img(t,k):
    s=S[k]; t0=s[0]; d=nxt(k)-t0; kind=s[1]
    if kind=='av':
        im=avf('A',t); return kb(im,t,t0,d,1.0,1.06,0.5,0.4)
    if kind=='v':
        i=int((t-t0+s[3])*FPS); im=vframe(s[2],i)
        return kb(im,t,t0,d,s[4],s[5],0.5,0.5)
    if kind=='i':
        return kb(img(FT+s[2]),t,t0,d,s[4],s[5],0.5,0.5)
    if kind=='num':
        src={'49%':(FT+'tcells.png',None),'3 ГОДА':(None,'5722113'),'29%':(FT+'mammogram.jpg',None)}[s[2]]
        im=img(src[0]) if src[0] else vframe(src[1],int((t-t0)*FPS))
        return kb(darkblur(im),t,t0,d,1.1,1.2)
    if kind=='dots':
        return kb(darkblur(img(FT+s[2]),8,0.55),t,t0,d,1.0,1.08)
    if kind=='mam':
        return kb(img(FT+s[2]),t,t0,d,1.0,1.15,0.5,0.5)
def P(t,t0,d): return clamp((t-t0)/d)
import lib; lib.P=P
def fit_txt(b,s,cy,maxw,size,kind,**kw):
    while size>40 and tw_of(s,kind,size)>maxw: size-=4
    txt(b,s,CX,cy,size,kind,**kw); return size
def caption(b,t):
    cur=None
    for a,s,key in CAP:
        if t>=a: cur=(a,s,key)
    if not cur or not cur[1]: return
    a,s,key=cur; p=eob(P(t,a,0.16),1.5); sc=0.88+0.12*p
    kind='disp'; size=96
    while size>54 and tw_of(s,kind,size)>600: size-=4
    lines=[s]
    if tw_of(s,kind,size)>600:
        w=s.split(); h=len(w)//2 or 1; lines=[' '.join(w[:h]),' '.join(w[h:])]; size=86
        while size>50 and max(tw_of(l,kind,size) for l in lines)>600: size-=4
    y0=1110-(len(lines)-1)*size*0.55
    for j,l in enumerate(lines):
        yy=y0+j*size*1.08; w=tw_of(l,kind,size*sc)
        if key: rrect(b,(CX-w/2-22,yy-size*sc*0.58,CX+w/2+22,yy+size*sc*0.55),12,fill=TEAL+(235,))
        txt(b,l,CX,yy,size*sc,kind,fill=(INK if key else HI),stroke=(0 if key else 8),sfill=(8,10,14))
def hud(b,t):
    d=ImageDraw.Draw(b)
    lab=[c for a,c in CH if t>=a][-1]
    d.line([(X0,300),(X1,300)],fill=TEAL+(150,),width=2)
    txt(b,'ONC · '+lab,X0,276,30,'mono',fill=TEAL,anchor='lm')
    mm=f'{int(t)//60:02d}:{int(t)%60:02d}.{int((t%1)*100):02d}'
    txt(b,mm,X1,276,30,'mono',fill=HI,anchor='rm')
    # ecg strip
    pts=[]
    for i in range(80):
        x=X0+i*(X1-X0)/79; ph=(i/79*3+t*1.2)%1
        y=318+(-22 if 0.48<ph<0.5 else 14 if 0.5<ph<0.52 else -5*math.sin(ph*6.28) if ph<0.3 else 0)
        pts.append((x,y))
    d.line(pts,fill=TEAL+(200,),width=3)
    tg=[(a,s) for a,s in TAG if t>=a]
    if tg and tg[-1][1]:
        a,s=tg[-1]; al=clamp((t-a)/0.3)
        txt(b,s,X0,1236,26,'mono',fill=WARN,anchor='lm',alpha=al)
def numscene(b,t,k):
    s=S[k]; t0=s[0]; v=s[2]; p=t-t0
    if v=='49%':
        n=int(round(49*eo(p/0.7))); txt(b,'−%d%%'%n,CX,700,300*(0.9+0.1*eob(P(t,t0,0.3))),'disp',fill=WARN,glow=MAG,gr=30)
        txt(b,'РИСК РЕЦИДИВА',CX,920,62,'dispb',fill=HI,alpha=P(t,t0+0.3,0.3)); txt(b,'ИЛИ СМЕРТИ',CX,990,62,'dispb',fill=HI,alpha=P(t,t0+0.45,0.3))
    elif v=='29%':
        n=int(round(29*eo(p/0.7))); txt(b,'+%d%%'%n,CX,700,300*(0.9+0.1*eob(P(t,t0,0.3))),'disp',fill=TEAL,glow=TEAL,gr=30)
        txt(b,'НАЙДЕННЫХ РАКОВ',CX,920,62,'dispb',fill=HI,alpha=P(t,t0+0.3,0.3)); txt(b,'105 934 ЖЕНЩИНЫ · ШВЕЦИЯ',CX,1000,34,'mono',fill=HI,alpha=P(t,t0+0.6,0.3))
    else:
        txt(b,'3',CX,640,320*(0.9+0.1*eob(P(t,t0,0.3))),'disp',fill=WARN,glow=MAG,gr=30)
        txt(b,'ГОДА СПУСТЯ',CX,880,72,'dispb',fill=HI,alpha=P(t,t0+0.2,0.3))
def dotscene(b,t,t0):
    d=ImageDraw.Draw(b); n=int(clamp((t-t0)/0.6)*16)
    for i in range(16):
        r_,c_=divmod(i,4); x=CX-180+c_*120; y=540+r_*120
        if i>=n: continue
        lit=i<8 and t>t0+0.8; col=TEAL if lit else (110,110,120); rr=44 if lit else 38
        d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=col+(255,))
    if t>t0+0.8: txt(b,'8 ИЗ 16',CX,1060,120,'disp',fill=TEAL,glow=TEAL,gr=20,alpha=P(t,t0+0.8,0.2))
    txt(b,'ПАЦИЕНТОВ',CX,440,50,'dispb',fill=HI)
def mamscene(b,t,t0):
    y=420+700*((t-t0)/2.0%1)
    line(b,(X0,y),(X1,y),TEAL,4,0.9)
    for i,(bx,by) in enumerate([(300,640),(560,880)]):
        if t>t0+0.6+i*0.6: bracket(b,(bx-70,by-70,bx+70,by+70),WARN,30,5); txt(b,'ИИ: ПРОВЕРИТЬ',bx,by-100,26,'mono',fill=WARN)
def card(b,t,t0):
    p=eob(P(t,t0,0.3),1.3); x0,y0,x1,y1=150,430,750,900
    plate(b,(x0,y0+(1-p)*80,x1,y1+(1-p)*80),5,alpha=clamp(p))
    txt(b,'ШПАРГАЛКА',CX,y0+70,70,'disp',fill=INK,alpha=clamp(p))
    for j in range(5):
        if t>t0+0.35+j*0.22:
            yy=y0+160+j*62; txt(b,'ЦЕЛЬ %02d'%(j+1),x0+40,yy,34,'mono',fill=INK,anchor='lm'); line(b,(x0+250,yy),(x0+250+250*((j*37)%5+3)/7,yy),MAG,10)
def avcircle(b,t,seg,t0,t1):
    a=clamp(min((t-t0)/0.15,(t1-t)/0.15)); im=avf(seg,t).crop((170,280,1030,1140)).resize((300,300),Image.LANCZOS).convert('RGBA')
    m=Image.new('L',(300,300),0); ImageDraw.Draw(m).ellipse((0,0,299,299),fill=255); im.putalpha(m)
    s=1+0.25*(1-eob(P(t,t0,0.25),1.4))
    d=ImageDraw.Draw(b); r=150*s+6; d.ellipse((780-r,1400-r,780+r,1400+r),outline=TEAL+(255,),width=6)
    if s!=1: im=im.resize((int(300*s),int(300*s)),Image.BICUBIC)
    comp(b,im,(780-im.width/2,1400-im.height/2),a)
def stampx(b,t):
    for t0,s in [(21.43,'ФАЗА 2'),(24.34,'ФАЗА 3: ИДЁТ'),(37.68,'ВПЕРВЫЕ')]:
        if t0<=t<t0+1.6: stamp(b,s,CX,640,t,t0,col=WARN,size=110,rot=-6)
def cover():
    b=avf('A',0.0).convert('RGBA'); b=Image.blend(b,Image.new('RGBA',(W,H),(0,0,0,255)),0.45)
    txt(b,'ВАКЦИНА',CX,560,190,'disp',fill=HI,stroke=10,sfill=(8,10,14))
    txt(b,'ОТ РАКА',CX,760,190,'disp',fill=WARN,stroke=10,sfill=(8,10,14),glow=MAG)
    rrect(b,(CX-300,880,CX+300,1030),16,fill=TEAL+(255,)); txt(b,'УЖЕ ЕСТЬ',CX,955,120,'disp',fill=INK)
    return b
def trans(im,t):
    for tb,ty in TR.items():
        p=t-tb
        if 0<=p<0.16:
            k=1-p/0.16
            if ty=='flash': comp(im,Image.new('RGBA',(W,H),(240,250,250,int(200*k))),(0,0))
            elif ty=='glitch': im=glitch(im,t,k)
            elif ty=='dip': comp(im,Image.new('RGBA',(W,H),(0,0,0,int(230*k))),(0,0))
            elif ty=='whip':
                a=np.asarray(im.convert('RGB')).astype(np.float32); o=a.copy()
                for s in range(1,6): o+=np.roll(a,int(s*28*k),1)
                im=Image.fromarray((o/6).astype(np.uint8)).convert('RGBA')
            elif ty=='punch':
                z=1+0.08*k; c=im.resize((int(W*z),int(H*z)),Image.BICUBIC); im=c.crop(((c.width-W)//2,(c.height-H)//2,(c.width-W)//2+W,(c.height-H)//2+H))
    return im
import random

def vign():
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); r=np.sqrt(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.72))**2)
    a=np.clip((r-0.55)*1.3,0,1)*170; z=np.zeros((H,W,4),np.uint8); z[...,3]=a.astype(np.uint8); return Image.fromarray(z)
def glitch(im,t,k):
    a=np.asarray(im.convert('RGB')).copy(); rs=random.Random(int(t*30))
    s=int(18*k); a[...,0]=np.roll(a[...,0],s,1); a[...,2]=np.roll(a[...,2],-s,1)
    for _ in range(int(6*k)):
        y=rs.randint(0,H-60); h=rs.randint(10,60); a[y:y+h]=np.roll(a[y:y+h],rs.randint(-80,80),1)
    return Image.fromarray(a).convert('RGBA')
VG=None
def frame(f):
    global VG
    t=f/FPS
    if f<2: return cover().convert('RGB')
    if VG is None: VG=vign()
    k=cur_shot(t); b=shot_img(t,k).convert('RGBA'); kind=S[k][1]
    comp(b,VG,(0,0))
    if kind=='num': numscene(b,t,k)
    if kind=='dots': dotscene(b,t,S[k][0])
    if kind=='mam': mamscene(b,t,S[k][0])
    if 9.40<=t<11.15: card(b,t,9.40)
    if 11.15<=t<12.70 and t>11.4: bracket(b,(260,620,640,1000),WARN,60,7)
    if kind!='av': hud(b,t)
    stampx(b,t); caption(b,t)
    for t0,t1,sg in CIRC:
        if t0<=t<t1: avcircle(b,t,sg,t0,t1)
    b=trans(b,t)
    return b.convert('RGB')
if __name__=='__main__':
    a,bb=int(sys.argv[1]),int(sys.argv[2]); out=sys.argv[3]
    if out.endswith('.jpg'):
        frame(a).save(out,quality=90); sys.exit()
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','25','-i','-','-c:v','ffv1','-level','3','-pix_fmt','yuv444p',out],stdin=subprocess.PIPE)
    for f in range(a,min(bb,NF)): p.stdin.write(frame(f).tobytes())
    p.stdin.close(); p.wait()
