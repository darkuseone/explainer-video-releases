import sys,os,math,random,json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
from lib import *
import lib
CR=(236,226,206); INK=(28,22,18); RED=(200,30,36); YEL=(255,214,70); CYAN=(120,200,255); DESK=(38,28,22)
TOT=59.75; NF=int(round(TOT*FPS))
SH='/workspace/sim10/b/shots/'; AV='/workspace/sim10/av/f/'
LAG=0.023; M=json.load(open('/workspace/sim10/av/meta.json')); SEG={k:(v['t0'],v['t1'],v['c0']) for k,v in M.items()}
X0,X1=120,780; CX=(X0+X1)//2
# (t0, kind, src, off, z0, z1)  kinds: av full, v full-bleed, pol = polaroid on desk, scene types
S=[(0.0,'av'),(2.00,'v','30054113',0.0,1.05,1.2),(5.29,'v','11384843',0.0,1.0,1.1),(6.55,'dos','11384843',3,1.0,1.05),(9.44,'tri','30054113',4,1.1,1.15),
(17.25,'v','14904105',0.0,1.0,1.1),(18.55,'pix','20349219',0.0,1.0,1.0),(20.77,'planck','33549816',0,1.1,1.2),(23.95,'v','33549816',2.0,1.0,1.15),
(25.18,'speed','36216099',0,1.0,1.1),(29.26,'v','7140931',0.0,1.0,1.15),(31.08,'v','7299411',0.0,1.0,1.12),(32.37,'cloud','30163656',0,1.0,1.1),
(35.88,'v','8128417',0.0,1.0,1.12),(37.21,'v','7236940',1.0,1.0,1.12),(39.13,'def','14904105',3,1.0,1.05),(40.41,'dos2','38594546',0,1.0,1.05),
(44.01,'v','38594546',2.0,1.0,1.15),(46.03,'v','20349219',2.0,1.15,1.3),(48.18,'verd','11384843',5,1.0,1.05),(51.46,'v','30054113',8.0,1.0,1.1),
(52.64,'yn','30163656',3,1.0,1.05),(54.26,'v','36216099',3.0,1.0,1.12),(56.86,'v','7236940',5.0,1.0,1.1),(57.84,'end','8478578',0,1.0,1.2)]
TR={2.00:'shutter',5.29:'whip',6.55:'shutter',9.44:'whip',17.25:'shutter',18.55:'punch',20.77:'whip',23.95:'shutter',25.18:'punch',29.26:'whip',31.08:'shutter',
32.37:'punch',35.88:'whip',37.21:'punch',39.13:'flash',40.41:'shutter',44.01:'whip',46.03:'punch',48.18:'shutter',51.46:'whip',52.64:'punch',54.26:'whip',56.86:'punch',57.84:'glitch'}
CAP=[(0.05,'ТЫ — КОД',1),(1.32,'Я ЭТО УЖЕ ДОКАЗАЛ',0),(3.05,'ВОПРОС:',0),(3.74,'КТО ЕГО ЗАПУСТИЛ?',1),(5.29,None,0),(9.44,'ВЕРНО ОДНО ИЗ ТРЁХ',0),(10.95,None,0),
(17.25,None,0),(18.55,'У ПРОСТРАНСТВА',0),(19.27,'ВОЗМОЖНО, ЕСТЬ ПИКСЕЛЬ',1),(20.77,None,0),(23.95,None,0),(25.18,None,0),(27.97,'И БЫСТРЕЕ НЕЛЬЗЯ',1),
(29.26,'ПОХОЖЕ НА',0),(29.86,'ЛИМИТ ПРОЦЕССОРА',1),(31.08,None,0),(32.37,'ЧАСТИЦА НЕ ИМЕЕТ',0),(33.42,'ТОЧНОГО ПОЛОЖЕНИЯ',0),(34.41,'ПОКА ЕЁ НЕ ИЗМЕРЯТ',1),
(35.88,'КАК ИГРА,',0),(36.48,'КОТОРАЯ РИСУЕТ ТОЛЬКО',0),(37.84,'ТО, НА ЧТО ТЫ СМОТРИШЬ',1),(39.13,None,0),(40.41,None,0),(44.01,'ЧТОБЫ СИМУЛИРОВАТЬ',0),
(44.81,'ДАЖЕ ОДНУ ЗЕМЛЮ',1),(46.03,'НУЖНА АСТРОНОМИЧЕСКАЯ',0),(47.24,'ЭНЕРГИЯ',1),(48.18,None,0),(51.46,'МЫ В СИМУЛЯЦИИ?',1),(52.64,None,0),
(54.26,'ОТПРАВЬ ТОМУ, КТО',0),(55.13,'УВЕРЕН, ЧТО ВСЁ РЕАЛЬНО',1),(56.86,'И ПОДПИШИСЬ',1),(57.84,'ПОТОМУ ЧТО',0),(58.61,'ЕСЛИ ЭТО ПРАВДА:',1)]
EVI=[(0,'0/4'),(5.29,'1/4'),(17.25,'2/4'),(23.95,'3/4'),(31.08,'4/4'),(39.13,'ЗАЩИТА'),(48.18,'ВЕРДИКТ')]
SRC=[(6.55,'Bostrom, Philosophical Quarterly, 2003'),(17.25,'планковская длина ≈ 1,6×10^−35 м'),(23.95,'c = 299 792 км/с'),(31.08,'Квантовая механика: аналогия'),
(40.41,'Vazza, Frontiers in Physics, 2025'),(48.18,None)]
_ic={}
def img(path):
    if path not in _ic: _ic[path]=Image.open(path).convert('RGB')
    return _ic[path]
NFR={}
def vframe(sid,i):
    if sid not in NFR: NFR[sid]=len(os.listdir(SH+sid))
    n=NFR[sid]; i=i%(2*n-2); i=i if i<n else 2*n-2-i
    return Image.open(SH+sid+'/f%04d.jpg'%(i+1)).convert('RGB')
NAV=len(os.listdir(AV)) if os.path.isdir(AV) else 1
def avf(seg,t):
    t0,t1,c0=SEG[seg]; i=int(round((t-t0+c0+LAG)*FPS)); i=max(0,min(NAV-1,i)); return Image.open(AV+'f%04d.jpg'%(i+1)).convert('RGB')
def cur_shot(t):
    k=0
    for j,s in enumerate(S):
        if t>=s[0]: k=j
    return k
def nxt(k): return S[k+1][0] if k+1<len(S) else TOT
def P(t,t0,d): return clamp((t-t0)/d)
lib.P=P
DK=None
def desk():
    global DK
    if DK is None:
        rs=np.random.RandomState(3); n=rs.rand(H//8+1,W//8+1).astype(np.float32)
        n=np.asarray(Image.fromarray((n*255).astype(np.uint8)).resize((W,H),Image.BICUBIC)).astype(np.float32)/255
        g=np.asarray(Image.fromarray((rs.rand(H,W)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))).astype(np.float32)/255
        a=np.array(DESK,np.float32)*(0.8+0.3*n[...,None])+(g[...,None]-0.5)*18
        DK=Image.fromarray(a.clip(0,255).astype(np.uint8))
    return DK.copy().convert('RGBA')
def darkblur(im,r=12,dk=0.32): return ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(r))).enhance(dk)
def shot_img(t,k):
    s=S[k]; t0=s[0]; d=nxt(k)-t0; kind=s[1]
    if kind=='av': return kb(avf('A',t),t,t0,d,1.0,1.05,0.5,0.42)
    if kind in('dos','dos2','tri','verd','def'):
        b=desk(); bg=kb(darkblur(vframe(s[2],int((t-t0+s[3])*FPS)),14,0.45),t,t0,d,1.0,1.05)
        return Image.blend(b,bg,0.35)
    if kind=='pix':
        im=vframe(s[2],int((t-t0)*FPS)); q=eio(P(t,19.6,1.1)); bs=int(1+q*44)
        if bs>1: im=im.resize((W//bs,H//bs),Image.BILINEAR).resize((W,H),Image.NEAREST)
        return kb(im,t,t0,d,1.0,1.15)
    im=vframe(s[2],int((t-t0+s[3])*FPS))
    if kind=='v': return kb(im,t,t0,d,s[4],s[5])
    return kb(darkblur(im),t,t0,d,s[4],s[5])
def fit(s,kind,size,maxw):
    while size>28 and tw_of(s,kind,size)>maxw: size-=2
    return size
# --- caption: paper label strip, slab serif, red highlighter for key
def caption(b,t):
    cur=None
    for a,s,key in CAP:
        if t>=a: cur=(a,s,key)
    if not cur or not cur[1]: return
    a,s,key=cur; p=eob(P(t,a,0.18),1.4)
    size=fit(s,'dispb',66,600); w=tw_of(s,'dispb',size); y=1130
    rot=-1.5 if (int(a*10)%2) else 1.2
    lay=Image.new('RGBA',(int(w+80),int(size*1.7)),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rectangle((0,0,lay.width,lay.height),fill=(RED if key else CR)+(245,))
    d.text((lay.width/2,lay.height/2),s,font=font('dispb',size),fill=(CR if key else INK)+(255,),anchor='mm')
    lay=lay.rotate(rot,resample=Image.BICUBIC,expand=True)
    sc=0.9+0.1*p; lay=lay.resize((int(lay.width*sc),int(lay.height*sc)),Image.BICUBIC)
    comp(b,lay,(CX-lay.width/2,y-lay.height/2+(1-clamp(p))*30),clamp(P(t,a,0.08)))
def hud(b,t):
    d=ImageDraw.Draw(b); ev=[c for a,c in EVI if t>=a][-1]
    col=CYAN if 39.13<=t<48.18 else CR
    txt(b,'ДЕЛО № 010 · СИМУЛЯЦИЯ',X0,288,28,'dispb',fill=col,anchor='lm')
    txt(b,'УЛИКИ '+ev if '/' in ev else ev,X1,288,28,'dispb',fill=YEL if '/' in ev else (CYAN if ev=='ЗАЩИТА' else RED),anchor='rm')
    for x in range(X0,X1,24): d.line([(x,312),(x+12,312)],fill=col+(170,),width=3)
    sr=[(a,s) for a,s in SRC if t>=a]
    if sr and sr[-1][1]:
        a,s=sr[-1]; txt(b,'ИСТ.: '+s,X0,1236,24,'mono',fill=CR,anchor='lm',alpha=0.85*P(t,a,0.3))
def grain(t):
    rs=np.random.RandomState(int(t*25)%16); z=np.zeros((H//2,W//2,4),np.uint8); z[...,:3]=128; z[...,3]=(rs.rand(H//2,W//2)*26).astype(np.uint8)
    return Image.fromarray(z).resize((W,H),Image.NEAREST)
GR=[None]*16
def vign():
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); r=np.sqrt(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.72))**2)
    a=np.clip((r-0.45)*1.5,0,1)*200; z=np.zeros((H,W,4),np.uint8); z[...,:3]=(20,10,4); z[...,3]=a.astype(np.uint8); return Image.fromarray(z)
def evstamp(b,t,t0,n):
    if t0<=t<t0+1.25: stamp(b,f'УЛИКА №{n}',CX,640,t,t0,col=RED,size=130,rot=-7)
def card(b,box,t,t0,seed=2,rot=0):
    p=eob(P(t,t0,0.3),1.3); x0,y0,x1,y1=box; dy=(1-p)*90
    plate(b,(x0,y0+dy,x1,y1+dy),seed,alpha=clamp(p)); return dy,clamp(p)
def dossier(b,t,t0,rows,title):
    dy,a=card(b,(150,420,750,1000),t,t0,4)
    txt(b,title,CX,490+dy,52,'disp',fill=INK,alpha=a)
    line(b,(190,535+dy),(710,535+dy),INK,3,a)
    for j,(k,v,tv) in enumerate(rows):
        if t<tv: continue
        yy=600+dy+j*90; txt(b,k,190,yy,26,'mono',fill=(110,90,70),anchor='lm',alpha=a)
        sz=fit(v,'dispb',40,520); txt(b,v,190,yy+38,sz,'dispb',fill=INK,anchor='lm',alpha=a*P(t,tv,0.15))
def tri(b,t,t0):
    items=[('1','ЦИВИЛИЗАЦИИ ГИБНУТ','РАНЬШЕ',10.95),('2','НЕ ХОТЯТ','СИМУЛИРОВАТЬ',12.79),('3','МЫ ПОЧТИ НАВЕРНЯКА','В СИМУЛЯЦИИ',14.75)]
    for j,(n,a1,a2,ta) in enumerate(items):
        if t<ta: continue
        y0=420+j*215; dy,a=card(b,(150,y0,750,y0+185),t,ta,7+j)
        txt(b,n,215,y0+92+dy,110,'disp',fill=RED,alpha=a)
        txt(b,a1,290,y0+70+dy,fit(a1,'dispb',40,430),'dispb',fill=INK,anchor='lm',alpha=a)
        txt(b,a2,290,y0+120+dy,fit(a2,'dispb',40,430),'dispb',fill=INK,anchor='lm',alpha=a)
    if t>=15.64:
        p=eo(P(t,15.64,0.4)); y0=420+2*215
        pts=[(CX+330*math.cos(a_)*1.02,y0+92+120*math.sin(a_)) for a_ in np.linspace(0,2*math.pi*p,60)]
        if len(pts)>1: ImageDraw.Draw(b).line(pts,fill=RED+(255,),width=8)
    if t>=9.44: txt(b,'ТРИЛЕММА БОСТРОМА',CX,370,40,'disp',fill=CR,alpha=P(t,9.44,0.3))
def planck(b,t,t0):
    sc=0.85+0.15*eob(P(t,t0,0.3),1.5)
    txt(b,'10',CX-120,680,220*sc,'disp',fill=YEL,glow=(120,80,0),gr=24); txt(b,'−35',CX+30,565,110*sc,'disp',fill=YEL); txt(b,'м',CX+200,690,150*sc,'disp',fill=YEL)
    txt(b,'ПЛАНКОВСКАЯ ДЛИНА',CX,850,50,'dispb',fill=CR,alpha=P(t,t0+0.2,0.3))
    txt(b,'* дискретность пространства не доказана',CX,950,26,'mono',fill=CR,alpha=P(t,t0+0.8,0.3)*0.85)
def speed(b,t,t0):
    v=int(300000*eo(P(t,26.08,0.9))); s=f'{v:,}'.replace(',',' ')
    txt(b,s,CX,620,fit('300 000','disp',200,640),'disp',fill=CR,glow=(80,60,30))
    txt(b,'КМ/С',CX,800,70,'disp',fill=YEL,alpha=P(t,26.8,0.2))
    # gauge
    cx,cy,r=CX,1010,150; d=ImageDraw.Draw(b); d.arc((cx-r,cy-r,cx+r,cy+r),180,360,fill=CR+(200,),width=6)
    a_=math.pi*(1-eo(P(t,26.08,1.0))*0.98); d.line([(cx,cy),(cx+r*0.9*math.cos(a_),cy-r*0.9*math.sin(a_))],fill=RED+(255,),width=8)
    if t>27.97: txt(b,'MAX',cx+r+10,cy-20,30,'disp',fill=RED,anchor='lm')
def cloud(b,t,t0):
    rs=np.random.RandomState(5); col=(t>=35.04); d=ImageDraw.Draw(b)
    k=eo(P(t,35.04,0.25))
    for i in range(160):
        x=CX+rs.randn()*130*(1-k); y=700+rs.randn()*130*(1-k); r_=6
        d.ellipse((x-r_,y-r_,x+r_,y+r_),fill=CYAN+(int(180*(1-k))+40,))
    if col: d.ellipse((CX-22,678,CX+22,722),fill=YEL+(255,)); txt(b,'ИЗМЕРЕНО',CX,790,40,'dispb',fill=YEL,alpha=P(t,35.04,0.2))
    else: txt(b,'ГДЕ ОНА?',CX,460,44,'dispb',fill=CR)
def cone(b,t,t0):
    d=ImageDraw.Draw(b); a=P(t,37.84,0.3)
    if a>0:
        ov=Image.new('RGBA',(W,H),(0,0,0,int(170*a))); m=Image.new('L',(W,H),255); ImageDraw.Draw(m).polygon([(CX,1180),(X0-60,380),(X1+60,380)],fill=0)
        ov.putalpha(Image.fromarray((np.asarray(m,np.float32)/255*170*a).astype(np.uint8))); comp(b,ov,(0,0))
        txt(b,'RENDER: ВКЛ',CX,420,36,'mono',fill=YEL,alpha=a)
def defense(b,t,t0):
    ov=Image.new('RGBA',(W,H),(10,30,60,120)); comp(b,ov,(0,0))
    stamp(b,'ЗАЩИТА',CX,660,t,t0,col=CYAN,size=150,rot=5)
def verdict(b,t,t0):
    txt(b,'ВЕРДИКТ',CX,430,90,'disp',fill=CR,alpha=P(t,t0,0.2))
    if t>=49.05: stamp(b,'НЕ ДОКАЗАНО',CX,610,t,49.05,col=RED,size=110,rot=-6)
    if t>=50.09: stamp(b,'НЕ ОПРОВЕРГНУТО',CX,820,t,50.09,col=CYAN,size=90,rot=4)
def yn(b,t,t0):
    txt(b,'ПИШИ В КОММЕНТАРИЯХ',CX,450,44,'dispb',fill=CR)
    for j,(s,ta) in enumerate([('ДА',53.02),('НЕТ',53.68)]):
        x=X0+120+j*300; p=eob(P(t,ta-0.1,0.25),1.5)
        rrect(b,(x-110,580,x+110,800),8,outline=CR,width=6,alpha=clamp(p))
        txt(b,s,x,690,110*(0.6+0.4*p),'disp',fill=YEL if j==0 else RED,alpha=clamp(p))
def endsc(b,t,t0):
    p=P(t,58.9,TOT-58.9)
    if p>0: txt(b,'ТЫ — КОД',CX,700,fit('ТЫ — КОД','disp',170,640)*(0.9+0.1*p),'disp',fill=CR,alpha=clamp(p*1.6))
def polaroid(b,t,seg,t0,t1,label='СЛЕДОВАТЕЛЬ'):
    a=clamp(min((t-t0)/0.15,(t1-t)/0.15)); sz=290
    im=avf(seg,t).crop((170,280,1030,1140)).resize((sz,sz),Image.LANCZOS)
    im=ImageEnhance.Color(im).enhance(0.55)
    fr=Image.new('RGBA',(sz+36,sz+96),CR+(255,)); fr.paste(im,(18,18))
    ImageDraw.Draw(fr).text((fr.width/2,sz+56),label,font=font('dispb',30),fill=INK+(255,),anchor='mm')
    s=0.8+0.2*eob(P(t,t0,0.25),1.4); fr=fr.resize((int(fr.width*s),int(fr.height*s)),Image.BICUBIC).rotate(-4,resample=Image.BICUBIC,expand=True)
    sh=Image.new('RGBA',(fr.width+40,fr.height+40),(0,0,0,0)); ImageDraw.Draw(sh).rectangle((20,28,fr.width+20,fr.height+28),fill=(0,0,0,130)); sh=sh.filter(ImageFilter.GaussianBlur(10))
    cx,cy=790,1440; comp(b,sh,(cx-sh.width/2,cy-sh.height/2),a); comp(b,fr,(cx-fr.width/2,cy-fr.height/2),a)
    # red pin
    ImageDraw.Draw(b).ellipse((cx-14,cy-fr.height/2-6,cx+14,cy-fr.height/2+22),fill=RED+(int(255*a),))
CIRC=[(2.00,SEG['A'][1],'A'),(48.18,SEG['B'][1],'B')]
def trans(im,t):
    for t0,ty in TR.items():
        dt=t-t0
        if -0.001<=dt<0.16:
            k=1-dt/0.16
            if ty=='flash': im=Image.blend(im,Image.new('RGBA',(W,H),(255,255,255,255)),0.6*k)
            elif ty=='shutter':
                a=np.asarray(im.convert('RGB')).copy(); hgt=int(k*H/2); a[:hgt]=0; a[H-hgt:]=0; im=Image.fromarray(a).convert('RGBA')
            elif ty=='glitch':
                a=np.asarray(im.convert('RGB')).copy(); rs=random.Random(int(t*30)); s=int(22*k); a[...,0]=np.roll(a[...,0],s,1); a[...,2]=np.roll(a[...,2],-s,1)
                for _ in range(int(7*k)):
                    y=rs.randint(0,H-60); h=rs.randint(10,60); a[y:y+h]=np.roll(a[y:y+h],rs.randint(-90,90),1)
                im=Image.fromarray(a).convert('RGBA')
            elif ty=='whip':
                a=np.asarray(im.convert('RGB')).astype(np.float32); o=np.zeros_like(a)
                for s in range(6): o+=np.roll(a,int(s*30*k),1)
                im=Image.fromarray((o/6).astype(np.uint8)).convert('RGBA')
            elif ty=='punch':
                z=1+0.08*k; c=im.resize((int(W*z),int(H*z)),Image.BICUBIC); im=c.crop(((c.width-W)//2,(c.height-H)//2,(c.width-W)//2+W,(c.height-H)//2+H))
    return im
def cover():
    b=avf('A',0.0).convert('RGBA'); b=Image.blend(b,Image.new('RGBA',(W,H),(20,12,6,255)),0.5)
    s1,s2='МЫ ЖИВЁМ','В СИМУЛЯЦИИ?'
    txt(b,'ДЕЛО № 010',CX,430,44,'dispb',fill=CR)
    txt(b,s1,CX,580,fit(s1,'disp',170,660),'disp',fill=CR,stroke=8,sfill=(10,6,4))
    txt(b,s2,CX,770,fit(s2,'disp',170,660),'disp',fill=YEL,stroke=8,sfill=(10,6,4))
    stamp(b,'4 УЛИКИ',CX,990,1,0,col=RED,size=90,rot=-6)
    return b
VG=None
def frame(f):
    global VG
    t=f/FPS
    if f<2: return cover().convert('RGB')
    if VG is None: VG=vign()
    k=cur_shot(t); b=shot_img(t,k).convert('RGBA'); kind=S[k][1]; t0=S[k][0]
    comp(b,VG,(0,0))
    if kind=='dos': dossier(b,t,t0,[('ИМЯ','Ник Бостром, философ',6.55),('ГОД','2003',7.95),('ДОКУМЕНТ','«Живём ли мы в симуляции?»',8.4)],'ДОСЬЕ')
    elif kind=='dos2': dossier(b,t,t0,[('ИМЯ','Франко Вацца, астрофизик',41.66),('ГОД','2025',40.48),('ВЫВОД','Не хватит энергии',43.1)],'ЗАЩИТА')
    elif kind=='tri': tri(b,t,t0)
    elif kind=='planck': planck(b,t,t0)
    elif kind=='speed': speed(b,t,t0)
    elif kind=='cloud': cloud(b,t,t0)
    elif kind=='def': defense(b,t,t0)
    elif kind=='verd': verdict(b,t,t0)
    elif kind=='yn': yn(b,t,t0)
    elif kind=='end': endsc(b,t,t0)
    if 37.21<=t<39.13: cone(b,t,37.21)
    for t0_,n in [(5.29,1),(17.25,2),(23.95,3),(31.08,4)]: evstamp(b,t,t0_,n)
    if 1.32<=t<2.0: txt(b,'ПРЕДЫДУЩЕЕ ДЕЛО: ДНК',CX,430,34,'mono',fill=YEL,alpha=P(t,1.32,0.2))
    if 29.26<=t<31.08: bracket(b,(260,560,640,940),YEL,50,6)
    if kind!='av' or t>1.3: hud(b,t)
    caption(b,t)
    for a0,a1,sg in CIRC:
        if a0<=t<a1: polaroid(b,t,sg,a0,a1)
    gi=f%16
    if GR[gi] is None: GR[gi]=grain(gi/25)
    comp(b,GR[gi],(0,0))
    b=trans(b,t)
    return b.convert('RGB')
if __name__=='__main__':
    a,bb=int(sys.argv[1]),int(sys.argv[2]); out=sys.argv[3]
    if out.endswith('.jpg'): frame(a).save(out,quality=88); sys.exit()
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','25','-i','-','-c:v','ffv1','-level','3','-pix_fmt','yuv444p',out],stdin=subprocess.PIPE)
    for f in range(a,min(bb,NF)): p.stdin.write(frame(f).tobytes())
    p.stdin.close(); p.wait()
