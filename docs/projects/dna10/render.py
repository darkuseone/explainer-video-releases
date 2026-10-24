import sys,os,math,random,json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
from lib import *
import lib
G=(57,255,136); GD=(18,120,64); BK=(4,10,7); RD=(255,70,80); AMB=(255,190,60); WH=(225,255,235)
TOT=57.56; NF=int(round(TOT*FPS))
SH='/workspace/dna10/b/shots/'; AV='/workspace/dna10/av/f/'
LAG=0.023; M=json.load(open('/workspace/dna10/av/meta.json')); SEG={k:(v['t0'],v['t1'],v['c0']) for k,v in M.items()}
X0,X1=120,780; CX=(X0+X1)//2
# shots (t0, kind, src, off, z0, z1)
S=[(0.0,'av'),(1.70,'v','34862096',0.0,1.05,1.2),(3.44,'bits','30162924',0,1.1,1.2),(9.38,'mb','6804121',0,1.1,1.2),(13.04,'v','7047796',2.0,1.0,1.12),
(14.91,'grid','30162924',3,1.0,1.1),(19.80,'grid2','30162924',5,1.1,1.15),(21.48,'v','12893579',1.0,1.05,1.18),(22.80,'v','7140928',0.0,1.0,1.15),
(23.77,'v','35460855',0.0,1.1,1.3),(24.85,'v','9837848',2.0,1.0,1.12),(27.40,'pct','34862899',0,1.1,1.2),(30.32,'v','4122942',3.0,1.0,1.1),
(32.26,'diff','4122942',6,1.15,1.2),(35.01,'bug','6804121',4.0,1.2,1.35),(37.12,'warn','30162924',2,1.0,1.05),(38.55,'v','7989667',0.0,1.0,1.12),
(40.53,'v','34862899',2.0,1.0,1.15),(42.90,'b24','30162924',4,1.05,1.1),(44.19,'cells','35460855',2.0,1.0,1.1),(47.11,'v','34862096',3.0,1.15,1.3),
(48.84,'v','12893579',4.0,1.0,1.1),(50.26,'v','4122942',10.0,1.0,1.12),(52.43,'v','31767898',0.0,1.0,1.1),(53.24,'sim','30162924',1,1.0,1.1),(56.23,'loop','34862096',0,1.0,1.3)]
TR={1.70:'scan',3.44:'glitch',9.38:'scan',13.04:'punch',14.91:'glitch',19.80:'flash',21.48:'scan',22.80:'punch',23.77:'glitch',24.85:'scan',27.40:'flash',30.32:'scan',
32.26:'punch',35.01:'glitch',37.12:'flash',38.55:'scan',40.53:'punch',42.90:'glitch',44.19:'scan',47.11:'glitch',48.84:'punch',50.26:'scan',52.43:'punch',53.24:'glitch',56.23:'scan'}
CAP=[(0.02,'ТЫ — ПРОГРАММА',1),(1.63,'И Я ДОКАЖУ',0),(2.51,'ЗА МИНУТУ',1),(3.44,'ТВОЙ КОД',0),(4.39,'ВСЕГО 4 БУКВЫ',1),(5.96,None,0),(9.38,'3 МЛРД БУКВ',0),(10.47,None,0),
(13.04,'МЕНЬШЕ, ЧЕМ',0),(13.67,'ИГРА НА ТЕЛЕФОНЕ',1),(14.91,'КОД ЧИТАЕТСЯ ТРОЙКАМИ',0),(16.51,None,0),(18.09,'У КАЖДОЙ — КОМАНДА',0),(19.80,'«СТАРТ»',1),(20.66,'И ТРИ «СТОП»',1),
(21.48,'КАК В ЛЮБОЙ ПРОГРАММЕ',0),(22.80,'А ПРОЦЕССОР —',0),(23.77,'РИБОСОМА',1),(24.85,'ЧИТАЕТ КОД',0),(25.75,'СОБИРАЕТ БЕЛКИ',1),(27.40,None,0),
(30.32,'С ЛЮБЫМ ЧЕЛОВЕКОМ',0),(31.42,'КОД СОВПАДАЕТ НА',0),(32.26,None,0),(35.01,'ОШИБКИ КОПИРОВАНИЯ',0),(36.15,'— ЭТО БАГИ',1),(37.12,None,0),
(38.55,'НЕТ ПРОГРАММИСТА',1),(40.53,'ЕГО ПИСАЛА',0),(41.28,'ЭВОЛЮЦИЯ',1),(41.96,'МИЛЛИАРДЫ ЛЕТ',0),(42.90,None,0),(44.19,'РАБОТАЕТ',0),(44.90,'В ТРИЛЛИОНАХ КЛЕТОК',1),(46.08,'ОДНОВРЕМЕННО',0),
(47.11,'ТАК ТЫ ПРОГРАММА',0),(48.10,'ИЛИ НЕТ?',1),(48.84,'ПИШИ В КОММЕНТАРИЯХ',1),(50.26,'ОТПРАВЬ ТОМУ, КТО',0),(51.02,'СЧИТАЕТ СЕБЯ УНИКАЛЬНЫМ',0),(52.35,'И ПОДПИШИСЬ',1),
(53.24,'В СЛЕДУЮЩЕМ РОЛИКЕ',0),(54.50,'МЫ ЖИВЁМ В СИМУЛЯЦИИ',1),(56.23,'А ПОКА ЗАПОМНИ:',0)]
CH=[(0,'boot'),(3.44,'01_alphabet'),(9.38,'02_size'),(14.91,'03_codons'),(22.80,'04_cpu'),(27.40,'05_junk'),(30.32,'06_diff'),(35.01,'07_bugs'),(37.12,'08_NOT_CODE'),(47.11,'09_exit')]
_ic={}
def img(path):
    if path not in _ic: _ic[path]=Image.open(path).convert('RGB')
    return _ic[path]
NFR={}
def vframe(sid,i):
    if sid not in NFR: NFR[sid]=len(os.listdir(SH+sid))
    n=NFR[sid]; i=i%(2*n-2); i=i if i<n else 2*n-2-i   # ping-pong past end
    return Image.open(SH+sid+'/f%04d.jpg'%(i+1)).convert('RGB')
def avf(seg,t):
    t0,t1,c0=SEG[seg]; i=int(round((t-t0+c0+LAG)*FPS)); i=max(0,min(NAV-1,i)); return Image.open(AV+'f%04d.jpg'%(i+1)).convert('RGB')
NAV=len(os.listdir(AV)) if os.path.isdir(AV) else 1
def cur_shot(t):
    k=0
    for j,s in enumerate(S):
        if t>=s[0]: k=j
    return k
def nxt(k): return S[k+1][0] if k+1<len(S) else TOT
def darkblur(im,r=10,dk=0.35): return ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(r))).enhance(dk)
def shot_img(t,k):
    s=S[k]; t0=s[0]; d=nxt(k)-t0; kind=s[1]
    if kind=='av': return kb(avf('A',t),t,t0,d,1.0,1.05,0.5,0.42)
    im=vframe(s[2],int((t-t0+s[3])*FPS))
    if kind=='v': return kb(im,t,t0,d,s[4],s[5])
    return kb(darkblur(im),t,t0,d,s[4],s[5])
def P(t,t0,d): return clamp((t-t0)/d)
lib.P=P
def fit(s,kind,size,maxw):
    while size>30 and tw_of(s,kind,size)>maxw: size-=2
    return size
# --- terminal caption: typed reveal + block cursor
def caption(b,t):
    cur=None
    for a,s,key in CAP:
        if t>=a: cur=(a,s,key)
    if not cur or not cur[1]: return
    a,s,key=cur; n=int(clamp((t-a)/max(0.12,len(s)*0.022))*len(s)); shown=s[:max(1,n)]
    size=fit('> '+s,'dispb',64,640); y=1150
    w=tw_of('> '+s,'dispb',size)
    rrect(b,(X0-6,y-size*0.85,X0+w+size*0.9,y+size*0.75),6,fill=(BK+(215,)) if not key else (G+(240,)))
    fc=BK if key else G
    txt(b,'> '+shown,X0+8,y,size,'dispb',fill=fc,anchor='lm')
    if int(t*3)%2==0 or n<len(s):
        cx=X0+8+tw_of('> '+shown,'dispb',size)+6; rrect(b,(cx,y-size*0.5,cx+size*0.5,y+size*0.5),0,fill=(fc+(255,)))
def hud(b,t):
    d=ImageDraw.Draw(b); lab=[c for a,c in CH if t>=a][-1]
    col=RD if 37.12<=t<47.11 else G
    txt(b,'~/genome $ ./'+lab,X0,288,28,'mono',fill=col,anchor='lm')
    mm=f'{t:05.2f}s'; txt(b,mm,X1,288,28,'mono',fill=WH,anchor='rm')
    d.line([(X0,312),(X1,312)],fill=col+(160,),width=2)
    # read progress bar
    p=t/TOT; nb=22; k=int(p*nb)
    bar='['+'#'*k+'.'*(nb-k)+f'] {int(p*100):3d}%'
    txt(b,'READING '+bar,X0,1236,24,'mono',fill=col,anchor='lm',alpha=0.85)
SCN=None
def scan_overlay():
    z=np.zeros((H,W,4),np.uint8); z[::4,:,3]=38; return Image.fromarray(z)
def vign():
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); r=np.sqrt(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.72))**2)
    a=np.clip((r-0.5)*1.4,0,1)*190; z=np.zeros((H,W,4),np.uint8); z[...,3]=a.astype(np.uint8); return Image.fromarray(z)
def bigtxt(b,s,cy,size,col,t,t0,maxw=640,glow=None):
    size=fit(s,'disp',size,maxw); sc=0.85+0.15*eob(P(t,t0,0.25),1.5)
    txt(b,s,CX,cy,size*sc,'disp',fill=col,glow=glow,gr=26)
def bits(b,t,t0):
    L=[('А','00',5.96),('Т','01',6.42),('Г','10',6.92),('Ц','11',7.34)]
    txt(b,'ALPHABET.SIZE = 4',CX,430,34,'mono',fill=G,alpha=P(t,t0,0.3))
    for j,(c,bit,ta) in enumerate(L):
        if t<ta-0.05: continue
        x=X0+80+j*165; p=eob(P(t,ta-0.05,0.25),1.6)
        rrect(b,(x-70,560,x+70,760),10,outline=G,width=4,alpha=clamp(p))
        txt(b,c,x,650,120*(0.7+0.3*p),'disp',fill=WH)
        if t>7.84: txt(b,bit,x,830,58,'mono',fill=AMB,alpha=P(t,7.84+j*0.08,0.2))
    if t>8.48: txt(b,'1 БУКВА = 2 БИТА',CX,960,52,'dispb',fill=G,alpha=P(t,8.48,0.2))
def mb(b,t,t0):
    n=3_000_000_000*eo(P(t,t0,1.0)); txt(b,f'{int(n):,}'.replace(',',' '),CX,520,64,'mono',fill=WH)
    txt(b,'БУКВ × 2 БИТА =',CX,610,40,'mono',fill=G,alpha=P(t,t0+0.4,0.3))
    if t>10.47:
        v=int(750*eo(P(t,10.47,1.3))); bigtxt(b,f'{v} МБ',800,170,G,t,10.47,glow=GD)
        txt(b,'≈ 3 × 10⁹ × 2 бит / 8',CX,960,34,'mono',fill=WH,alpha=P(t,11.2,0.3))
def phonecmp(b,t,t0):
    for j,(lab,v,col) in enumerate([('ДНК',0.75,G),('ИГРА',2.0,RD)]):
        y=560+j*110; w=int(520*v/2.0*eo(P(t,t0+0.2+j*0.25,0.5)))
        txt(b,lab,X0,y,40,'mono',fill=WH,anchor='lm'); rrect(b,(X0+150,y-28,X0+150+max(w,4),y+28),4,fill=col+(230,))
        txt(b,f'{v:.2f} ГБ'.replace('.',','),X0+160+w,y,32,'mono',fill=WH,anchor='lm',alpha=P(t,t0+0.6,0.2))
    txt(b,'* многие мобильные игры весят 2+ ГБ',X0,800,24,'mono',fill=WH,anchor='lm',alpha=0.7)
COD=None
def grid(b,t,t0,stage2=False):
    global COD
    if COD is None:
        B='TCAG'; COD=[a+bb+c for a in B for bb in B for c in B]
    n=64 if stage2 else int(64*eo(P(t,16.51,1.37)))
    if not stage2: txt(b,'3 БУКВЫ = 1 КОМАНДА',CX,410,40,'mono',fill=G,alpha=P(t,t0,0.3))
    for i in range(64):
        if i>=n: break
        r,c=divmod(i,8); x=X0+40+c*82; y=470+r*68
        col=(40,90,60); fc=G
        if stage2:
            if COD[i]=='ATG' and t>=19.80: col=G; fc=BK
            if COD[i] in('TAA','TAG','TGA') and t>=20.66: col=RD; fc=WH
        rrect(b,(x-36,y-28,x+36,y+28),4,fill=col+(230,))
        txt(b,COD[i],x,y,24,'mono',fill=fc)
    if not stage2 and t>16.9: bigtxt(b,'64',1040,110,AMB,t,16.9)
    if stage2:
        if t>=19.80: txt(b,'ATG = START',X0,1030,40,'mono',fill=G,anchor='lm')
        if t>=20.66: txt(b,'TAA · TAG · TGA = STOP',X0,1080,36,'mono',fill=RD,anchor='lm')
def pct(b,t,t0):
    v=1.5*eo(P(t,28.9,0.9)); bigtxt(b,f'{v:.1f}%'.replace('.',','),640,190,G,t,t0,glow=GD)
    # 200-cell genome bar, 3 lit
    for i in range(200):
        r,c=divmod(i,20); x=X0+20+c*31; y=800+r*26
        lit=i<3 and t>28.9
        rrect(b,(x,y,x+24,y+18),2,fill=((G+(255,)) if lit else (60,80,70,200)))
    txt(b,'КОДИРУЕТ БЕЛКИ',CX,1100,44,'dispb',fill=WH,alpha=P(t,t0+0.4,0.3))
def diff(b,t,t0):
    v=99.9*eo(P(t,t0,0.9)); bigtxt(b,f'{v:.1f}%'.replace('.',','),620,170,G,t,t0,glow=GD)
    lines=[('  ATGCCGTTAGCA',WH),('- ATGCCGTTAGCA',RD),('+ ATGCCATTAGCA',G)]
    for j,(s,c) in enumerate(lines):
        if t>t0+0.6+j*0.25: txt(b,s,X0+20,820+j*62,42,'mono',fill=c,anchor='lm')
    if t>t0+1.4: txt(b,'git diff: 0,1%',X0+20,1030,40,'mono',fill=AMB,anchor='lm')
def bug(b,t,t0):
    if t>t0+0.1: stamp(b,'BUG',CX,620,t,t0+0.1,col=RD,size=150,rot=-7)
    if t>36.15: txt(b,'segfault @ copy()',CX,880,38,'mono',fill=RD,alpha=P(t,36.15,0.2))
def warn(b,t,t0):
    d=ImageDraw.Draw(b); d.rectangle((0,0,W,H),fill=(60,0,8,110))
    bigtxt(b,'WARNING',600,120,RD,t,t0)
    txt(b,'А ТЕПЕРЬ ОТЛИЧИЯ',CX,760,50,'dispb',fill=WH,alpha=P(t,t0+0.3,0.2))
def b24(b,t,t0):
    txt(b,'0101 1100',CX,560,70,'mono',fill=(120,140,130))
    if t>43.2: line(b,(X0+60,560),(X1-60,560),RD,10)
    bigtxt(b,'ATGC',780,150,G,t,t0+0.3,glow=GD)
    txt(b,'НЕ ДВОИЧНЫЙ',CX,960,54,'dispb',fill=WH,alpha=P(t,t0+0.2,0.2))
def cells(b,t,t0):
    n=int(clamp((t-t0)/2.0)*5)+1
    for r in range(n):
        for c in range(n):
            s=(X1-X0-40)/n; x=X0+20+c*s; y=430+r*s
            rrect(b,(x+3,y+3,x+s-3,y+s-3),3,outline=G,width=2,alpha=0.8)
            txt(b,'run()',x+s/2,y+s/2,max(12,int(s/5)),'mono',fill=G,alpha=0.8)
def sim(b,t,t0):
    txt(b,'NEXT >> sim10.exe',CX,520,52,'mono',fill=AMB,alpha=P(t,t0,0.2))
    p=eo(P(t,t0+0.2,2.5)); rrect(b,(X0+40,600,X1-40,640),4,outline=AMB,width=3)
    rrect(b,(X0+46,606,X0+46+(X1-X0-92)*p,634),2,fill=AMB+(255,))
    if t>54.50: bigtxt(b,'СИМУЛЯЦИЯ',820,110,G,t,54.50,glow=GD)
def avwin(b,t,seg,t0,t1):
    a=clamp(min((t-t0)/0.15,(t1-t)/0.15)); sz=300
    im=avf(seg,t).crop((170,280,1030,1140)).resize((sz,sz),Image.LANCZOS)
    im=ImageEnhance.Color(im).enhance(0.7).convert('RGBA')
    s=0.8+0.2*eob(P(t,t0,0.25),1.4); 
    if s!=1: im=im.resize((int(sz*s),int(sz*s)),Image.BICUBIC)
    x0,y0=780-im.width//2,1400-im.height//2
    rrect(b,(x0-8,y0-44,x0+im.width+8,y0+im.height+8),6,fill=(BK+(235,)),alpha=a)
    txt(b,'● REC operator.cam',x0+4,y0-22,22,'mono',fill=RD if int(t*2)%2 else G,anchor='lm',alpha=a)
    comp(b,im,(x0,y0),a); rrect(b,(x0-8,y0-44,x0+im.width+8,y0+im.height+8),6,outline=G,width=3,alpha=a)
CIRC=[(1.70,SEG['A'][1],'A'),(47.11,SEG['B'][1],'B')]
def trans(im,t):
    for t0,ty in TR.items():
        dt=t-t0
        if -0.001<=dt<0.16:
            k=1-dt/0.16
            if ty=='flash': im=Image.blend(im,Image.new('RGBA',(W,H),G+(255,)),0.55*k)
            elif ty=='glitch': im=glitch(im,t,k)
            elif ty=='scan':
                a=np.asarray(im.convert('RGB')).copy(); y=int((1-k)*H); a[max(0,y-40):y]=np.array(G)*0.8; a[y:]=(a[y:]*0.35).astype(np.uint8); im=Image.fromarray(a).convert('RGBA')
            elif ty=='punch':
                z=1+0.08*k; c=im.resize((int(W*z),int(H*z)),Image.BICUBIC); im=c.crop(((c.width-W)//2,(c.height-H)//2,(c.width-W)//2+W,(c.height-H)//2+H))
    return im
def glitch(im,t,k):
    a=np.asarray(im.convert('RGB')).copy(); rs=random.Random(int(t*30)); s=int(20*k)
    a[...,0]=np.roll(a[...,0],s,1); a[...,2]=np.roll(a[...,2],-s,1)
    for _ in range(int(7*k)):
        y=rs.randint(0,H-60); h=rs.randint(10,60); a[y:y+h]=np.roll(a[y:y+h],rs.randint(-90,90),1)
    return Image.fromarray(a).convert('RGBA')
def cover():
    b=avf('A',0.0).convert('RGBA'); b=Image.blend(b,Image.new('RGBA',(W,H),BK+(255,)),0.5)
    comp(b,scan_overlay(),(0,0))
    txt(b,'ТВОЯ ДНК',CX,560,fit('ТВОЯ ДНК','disp',140,660),'disp',fill=WH)
    txt(b,'— ЭТО КОД',CX,740,fit('— ЭТО КОД','disp',140,660),'disp',fill=G,glow=GD,gr=30)
    txt(b,'> докажу за минуту_',CX,920,44,'dispb',fill=G)
    return b
VG=None;SC=None
def frame(f):
    global VG,SC
    t=f/FPS
    if f<2: return cover().convert('RGB')
    if VG is None: VG=vign(); SC=scan_overlay()
    k=cur_shot(t); b=shot_img(t,k).convert('RGBA'); kind=S[k][1]; t0=S[k][0]
    comp(b,VG,(0,0)); comp(b,SC,(0,0))
    if kind=='bits': bits(b,t,t0)
    elif kind=='mb': mb(b,t,t0)
    elif kind in('grid','grid2'): grid(b,t,t0,kind=='grid2')
    elif kind=='pct': pct(b,t,t0)
    elif kind=='diff': diff(b,t,t0)
    elif kind=='bug': bug(b,t,t0)
    elif kind=='warn': warn(b,t,t0)
    elif kind=='b24': b24(b,t,t0)
    elif kind=='cells': cells(b,t,t0)
    elif kind=='sim': sim(b,t,t0)
    if 13.04<=t<14.91: phonecmp(b,t,13.04)
    if 23.77<=t<24.85: bracket(b,(300,620,620,940),G,50,6)
    if 38.55<=t<40.53 and t>39.33: stamp(b,'AUTHOR: NULL',CX,700,t,39.33,col=RD,size=80,rot=-5)
    if kind=='loop':
        p=P(t,t0,TOT-t0); txt(b,'ТЫ — ПРОГРАММА',CX,700,fit('ТЫ — ПРОГРАММА','disp',96,660)*(0.9+0.1*p),'disp',fill=WH,alpha=clamp(p*1.5))
    if kind!='av' or t>1.0: hud(b,t)
    caption(b,t)
    for a0,a1,sg in CIRC:
        if a0<=t<a1: avwin(b,t,sg,a0,a1)
    b=trans(b,t)
    return b.convert('RGB')
if __name__=='__main__':
    a,bb=int(sys.argv[1]),int(sys.argv[2]); out=sys.argv[3]
    if out.endswith('.jpg'): frame(a).save(out,quality=88); sys.exit()
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','25','-i','-','-c:v','ffv1','-level','3','-pix_fmt','yuv444p',out],stdin=subprocess.PIPE)
    for f in range(a,min(bb,NF)): p.stdin.write(frame(f).tobytes())
    p.stdin.close(); p.wait()
