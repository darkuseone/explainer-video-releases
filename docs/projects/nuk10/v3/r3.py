from base import *
import json as _j
_TM=_j.load(open('/workspace/nuk10/v3/tmap.json'))['anc']; _O=np.array([x[0] for x in _TM]); _N=np.array([x[1] for x in _TM])
import base as B
ICE=(120,190,255); WARM=(255,214,140); GREY=(120,116,130); SKY=(90,170,255)
FT='/workspace/nuk10/footage/'
def credit(base,s,y=1850): txt(base,s,540,y,24,'mono',fill=HI,alpha=0.9,stroke=4,sfill=(10,8,14))
def zoomc(base,s,cx=540,cy=960):
    if s<=1.0005: return base
    a=1/s; return base.transform((W,H),Image.AFFINE,(a,0,cx*(1-a),0,a,cy*(1-a)),Image.BICUBIC)
_cnt={}
def frm(sid,i):
    d=R+'shots/'+sid+'/'
    if sid not in _cnt: _cnt[sid]=len(os.listdir(d))
    i=min(_cnt[sid],max(1,i)); return Image.open(d+f'f{i:04d}.jpg').convert('RGB')
def S(sid,t,t0,t1,off=0.0,z0=1.0,z1=1.1,cx=.5,cy=.5):
    im=frm(sid,int(round((t-t0+off)*25))+1); z=z0+(z1-z0)*eio(P(t,t0,t1-t0))
    if z!=1:
        a=1/z; im=im.transform((W,H),Image.AFFINE,(a,0,W*cx*(1-a),0,a,H*cy*(1-a)),Image.BICUBIC)
    return im.convert('RGBA')
def dim(base,k,col=(10,8,18)):
    base.alpha_composite(Image.new('RGBA',(W,H),col+(int(255*k),))); return base
def WIN(base,sid,t,t0,off=0.0,y0=560,z0=1.0,z1=1.06,bg=0.62,frame=True):
    im=frm(sid,int(round((t-t0+off)*25))+1)
    b=im.crop((369,0,711,608)).resize((108,192),Image.BILINEAR).resize((W,H),Image.BICUBIC).filter(ImageFilter.GaussianBlur(10))
    base.alpha_composite(b.convert('RGBA')); dim(base,bg)
    z=z0+(z1-z0)*clamp((t-t0)/3.0)
    if z!=1: a=1/z; im=im.transform((W,608),Image.AFFINE,(a,0,W/2*(1-a),0,a,304*(1-a)),Image.BICUBIC)
    base.alpha_composite(im.convert('RGBA'),(0,y0))
    if frame:
        bracket(base,(14,y0+10,W-14,y0+598),RED,50,6)
    return y0
_ob={}
def _blob(r,col):
    k=(int(r),col)
    if k not in _ob:
        s=int(r*8); yy,xx=np.mgrid[0:s,0:s].astype(np.float32); d=np.sqrt((xx-s/2)**2+(yy-s/2)**2)/(r*4)
        a=np.clip(1-d,0,1)**2.6*0.9; arr=np.zeros((s,s,4),np.uint8); arr[...,0]=col[0]; arr[...,1]=col[1]; arr[...,2]=col[2]; arr[...,3]=(a*255).astype(np.uint8)
        _ob[k]=Image.fromarray(arr,'RGBA')
    return _ob[k]
def orb(base,cx,cy,r,col=TEAL,a=1.0,core=HI):
    if a<=0 or r<2: return
    r=r*2.2; b=_blob(r,col); comp(base,b,(cx-b.width/2,cy-b.height/2),a)
    rr=r*0.40; lay=Image.new('RGBA',(int(rr*4),int(rr*4)),(0,0,0,0)); ImageDraw.Draw(lay).ellipse((rr,rr,rr*3,rr*3),fill=core+(255,))
    lay=lay.filter(ImageFilter.GaussianBlur(max(1,rr*0.22))); comp(base,lay,(cx-lay.width/2,cy-lay.height/2),a)
def ringp(base,cx,cy,r,col,w=6,a=1.0):
    if r<4: return
    lay=Image.new('RGBA',(int(r*2+40),int(r*2+40)),(0,0,0,0)); ImageDraw.Draw(lay).ellipse((20,20,r*2+20,r*2+20),outline=col+(255,),width=w)
    g=lay.filter(ImageFilter.GaussianBlur(8)); comp(base,g,(cx-r-20,cy-r-20),a*0.8); comp(base,lay,(cx-r-20,cy-r-20),a)
# ---------- earth / sun ----------
_E=None
def earth(r):
    global _E
    if _E is None:
        im=Image.open(FT+'earth.jpg').convert('RGB').crop((931-890,938-890,931+890,938+890)); _E=im
    D=int(r*2); im=_E.resize((D,D),Image.LANCZOS).convert('RGBA')
    m=Image.new('L',(D*3,D*3),0); ImageDraw.Draw(m).ellipse((D*3*0.014,D*3*0.014,D*3*0.986,D*3*0.986),fill=255); im.putalpha(m.resize((D,D),Image.LANCZOS)); return im
_SUN=None
def sunim(r):
    global _SUN
    if _SUN is None:
        _SUN=Image.open(FT+'sun.jpg').convert('RGB').crop((1920-1800,1850-1800,1920+1800,1850+1800))
    D=int(r*2); im=_SUN.resize((D,D),Image.LANCZOS).convert('RGBA')
    yy,xx=np.mgrid[0:D,0:D].astype(np.float32); d=np.sqrt(((xx-D/2)/(D/2))**2+((yy-D/2)/(D/2))**2)
    a=np.clip((1.0-d)/0.28,0,1); im.putalpha(Image.fromarray((a*255).astype(np.uint8))); return im
def glowdisc(base,cx,cy,r,col,a=0.8,gr=40):
    lay=Image.new('RGBA',(int(r*2+gr*6),int(r*2+gr*6)),(0,0,0,0)); c=lay.width/2
    ImageDraw.Draw(lay).ellipse((c-r,c-r,c+r,c+r),fill=col+(255,)); lay=lay.filter(ImageFilter.GaussianBlur(gr)); comp(base,lay,(cx-c,cy-c),a)
def atm_ring(base,cx,cy,r,t,a=1.0,w=14):
    lay=Image.new('RGBA',(int(r*2+160),int(r*2+160)),(0,0,0,0)); c=lay.width/2; d=ImageDraw.Draw(lay)
    d.ellipse((c-r-w,c-r-w,c+r+w,c+r+w),outline=SKY+(255,),width=w)
    g=lay.filter(ImageFilter.GaussianBlur(14)); comp(base,g,(cx-c,cy-c),a*0.9); comp(base,lay,(cx-c,cy-c),a*0.8)
def shards(base,t,t0,cx,cy,r,n=7):
    p=t-t0; im=earth(r); D=im.width
    q=eo(p/0.9) if p>0 else 0
    for k in range(n):
        a0=360/n*k+20; a1=360/n*(k+1)+20
        m=Image.new('L',(D,D),0); ImageDraw.Draw(m).pieslice((-2,-2,D+1,D+1),a0-90,a1-90,fill=255)
        sh=im.copy(); al=ImageChops.multiply(sh.getchannel('A'),m); sh.putalpha(al)
        bis=math.radians((a0+a1)/2-90); dist=q*(110+35*((k*5)%3)); rot=q*(30*(1 if k%2 else -1))
        sh=sh.rotate(rot,resample=Image.BICUBIC,expand=False)
        comp(base,sh,(cx-D/2+math.cos(bis)*dist,cy-D/2+math.sin(bis)*dist),max(0,1-max(0,p-1.0)/0.5))
    # crack glow
    if p<0.25:
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
        for k in range(n):
            ang=math.radians(360/n*k+20-90); d.line([(cx,cy),(cx+math.cos(ang)*r*1.1,cy+math.sin(ang)*r*1.1)],fill=(255,240,200,255),width=10)
        comp(base,lay.filter(ImageFilter.GaussianBlur(6)),(0,0),1-p/0.25)
def arrows_in(base,cx,cy,r,t,t0,col=GOLD):
    q=((t-t0)*1.4)%1
    for k in range(12):
        ang=2*math.pi*k/12; r0=r*(2.0-1.0*q)+10; r1=r0+90
        line(base,(cx+math.cos(ang)*r1,cy+math.sin(ang)*r1),(cx+math.cos(ang)*(r0),cy+math.sin(ang)*(r0)),col,10,0.9*(1-q*0.4))
        pa=ang+math.pi; ax,ay=cx+math.cos(ang)*r0,cy+math.sin(ang)*r0
        for s in (-1,1):
            line(base,(ax,ay),(ax+math.cos(pa+s*0.5)*30,ay+math.sin(pa+s*0.5)*30),col,10,0.9)
def dpad(n,w=0): return ' '.join([n[max(0,i-3):i] for i in range(len(n),0,-3)][::-1])
def roll(t,t0,s,spd=0.05,seed=3):
    # digits lock left-to-right; unlocked digits random
    rs=random.Random(int(t*20)+seed); out=''
    for i,ch in enumerate(s):
        out+=ch if (t-t0)>=spd*i or not ch.isdigit() else str(rs.randint(0,9))
    return out
def fmt_int(s): return ' '.join([s[max(0,i-3):i] for i in range(len(s),0,-3)][::-1])
# ---------- scenes ----------
def sc_s2(base,t,t0):
    base.alpha_composite(S('__h',t,t0,4.58,0,1.0,1.1)) if False else None
    im=still('hiroshima.jpg',None,0.7); base.alpha_composite(kb(im,t,t0,2.2,1.05,1.2,.5,.42)); dim(base,0.72)
    p=eob(P(t,t0,0.25),1.5); txt(base,'3,6',540,700,430*(0.7+0.3*p),'disp',fill=HI,stroke=10,sfill=(10,8,14),glow=MAG,gr=36,alpha=min(1,p*2))
    if t>=3.36:
        q=eob(P(t,3.36,0.2),1.4); txt(base,'КВИНТИЛЛИОНА',540,970,132*(0.75+0.25*q),'disp',fill=HI,stroke=8,sfill=(10,8,14),glow=VIOL,alpha=min(1,q*2))
    if t>=4.04:
        q=eob(P(t,4.04,0.2),1.4); dx,dy=shake(t,4.04,10,0.25); txt(base,'ХИРОСИМ',540+dx,1130+dy,180*(0.75+0.25*q),'disp',fill=GOLD,stroke=9,sfill=(10,8,14),glow=MAG,alpha=min(1,q*2))
    s=roll(t,t0,fmt_int('3600000000000000000'),0.06); txt(base,s,540,1280,38,'mono',fill=LILAC,alpha=0.95)
def sc_s3(base,t,t0):
    base.alpha_composite(bg_void(t))
    p=eio(P(t,t0,0.5)); txt(base,'НУЖНО',100,640,40,'mono',fill=LILAC,anchor='lm')
    rrect(base,(90,690,90+int(900*p),790),12,fill=PURP+(255,)); 
    if p>0.3: txt(base,fmt_int('3600000000000000000'),540,740,48,'mono',fill=HI,alpha=min(1,(p-0.3)*2))
    txt(base,'ЕСТЬ',100,920,40,'mono',fill=LILAC,anchor='lm')
    q=P(t,t0+0.5,0.2)
    if q>0:
        glowrect(base,(88,970,94,1070),RED,14,0.9,2,3); rrect(base,(90,972,93,1068),1,fill=RED+(255,))
        line(base,(140,1020),(250,1020),RED,4,q)
        txt(base,'ВОТ ОН, ТОНЕНЬКИЙ ШТРИХ',275,1020,34,'mono',fill=RED,anchor='lm',alpha=q)
    if t>=5.66:
        v=int(round(135000*eo(P(t,5.66,0.55)))); txt(base,fmt_int(str(v)),540,1260,230,'disp',fill=GOLD,stroke=9,sfill=(10,8,14),glow=MAG,gr=30)
        txt(base,'ХИРОСИМ НА ВСЁ ЧЕЛОВЕЧЕСТВО',540,1400,40,'mono',fill=HI,alpha=P(t,5.9,0.3))
def sc_s4(base,t,t0):
    im=still('hiroshima.jpg',None,0.8); base.alpha_composite(kb(im,t,t0,1.7,1.0,1.15,.5,.45)); dim(base,0.38)
    txt(base,'6 АВГУСТА 1945',540,760,56,'mono',fill=PINK,alpha=eo(P(t,t0+0.15,0.2)))
    if t>=7.44:
        stamp(base,'15 КТ',540,1090,t,7.44,RED,250,-6,'ТРОТИЛОВЫЙ ЭКВИВАЛЕНТ')
    credit(base,'Фото: George R. Caron, USAAF / NARA. Общественное достояние',1760)
def sc_s5a(base,t,t0):
    base.alpha_composite(bg_void(t))
    p=eob(P(t,t0,0.3),1.3); plate(base,(110,700,970,1100),4,1.0,True)
    txt(base,'ЕДИНИЦА ИЗМЕРЕНИЯ',540,770,50,'mono',fill=LILAC,alpha=p)
    txt(base,'1 ХИРОСИМА',540,900,190*(0.8+0.2*p),'disp',fill=GOLD,stroke=8,sfill=(10,8,14),glow=MAG)
    txt(base,'= 63 ТРИЛЛИОНА ДЖОУЛЕЙ',540,1030,54,'tek',fill=HI,alpha=P(t,t0+0.35,0.2))
def sc_s5b(base,t,t0):
    base.alpha_composite(bg_dark(t) if False else Image.new('RGBA',(W,H),VOID+(255,)))
    cx,cy,r=540,860,300
    if t<11.42:
        pu=1+0.02*math.sin((t-t0)*16); im=earth(r*pu); comp(base,im,(cx-im.width/2,cy-im.height/2)); atm_ring(base,cx,cy,r*pu,t,0.5,6)
        arrows_in(base,cx,cy,r,t,t0)
        txt(base,'ГРАВИТАЦИЯ',540,1330,120,'disp',fill=GOLD,stroke=8,sfill=(10,8,14),glow=MAG,alpha=eo(P(t,t0+0.3,0.2)))
    else:
        shards(base,t,11.42,cx,cy,r)
        if t>=11.9: stamp(base,'РАСКОЛ',540,1330,t,11.9,RED,170,-5)
def sc_s6(base,t,t0):
    seq=[(12.9,'ivym'),(14.1,'brb'),(15.3,'brd')]
    sid,s0=[(s,a) for a,s in seq if t>=a][-1]
    WIN(base,sid,t,s0,0,560)
    p=eob(P(t,t0,0.25),1.3)
    txt(base,'ЦАРЬ-БОМБА · 50 МТ',540,470,70,'disp',fill=HI,stroke=6,sfill=(10,8,14),glow=VIOL)
    txt(base,'× 1 000 000 000 000 000',540,1290,84,'disp',fill=GOLD,stroke=8,sfill=(10,8,14),glow=MAG,alpha=p)
    txt(base,'КВАДРИЛЛИОН ЦАРЬ-БОМБ',540,1390,44,'mono',fill=HI,alpha=P(t,t0+0.3,0.2))
    credit(base,'Кадры других испытаний: Ivy Mike, Castle Bravo. US DOE, PD',1760)
def sc_s7(base,t,t0):
    sid='brp'
    WIN(base,sid,t,t0,0,560)
    txt(base,'СУММА ВСЕХ ЯДЕРНЫХ ЗАРЯДОВ',540,480,40,'mono',fill=HI,alpha=0.9)
    if t>=17.56:
        q=eob(P(t,17.56,0.22),1.4); dx,dy=shake(t,17.56,10,0.25)
        txt(base,'≈ 2 ГИГАТОННЫ',540+dx,1280+dy,150*(0.8+0.2*q),'disp',fill=GOLD,stroke=9,sfill=(10,8,14),glow=MAG,alpha=min(1,q*2))
        txt(base,'= 2 000 000 000 ТОНН ТНТ',540,1400,44,'mono',fill=HI,alpha=P(t,17.7,0.25))
    credit(base,'Кадры: испытание Castle Bravo, US DOE. Общественное достояние',1760)
def sc_s8(base,t,t0):
    base.alpha_composite(bg_void(t)); 
    ex,ey,sx,sy=150,820,880,820
    if t<21.98:
        txt(base,'ТАК ВЫГЛЯДИТ МАСШТАБ',540,640,44,'mono',fill=LILAC,alpha=eo(P(t,t0,0.2)))
        e=earth(70); comp(base,e,(ex-70,ey-70)); atm_ring(base,ex,ey,70,t,0.5,4)
        glowdisc(base,sx,sy,170,(255,140,40),0.7,50); s=sunim(150); comp(base,s,(sx-150,sy-150))
        pr=eio(P(t,t0+0.3,2.0)); xx=ex+90+(sx-170-ex-90)*pr
        line(base,(ex+90,ey),(xx,ey),GOLD,6,1.0)
        for k in range(0,11):
            x=ex+90+(sx-170-ex-90)*k/10
            if x<=xx: line(base,(x,ey-16),(x,ey+16),GOLD,4,0.9)
        orb(base,xx,ey,18,GOLD,1.0)
        km=int(round(150000000*pr)); txt(base,fmt_int(str(km))+' КМ',540,1040,104,'disp',fill=HI,stroke=6,sfill=(10,8,14),glow=MAG)
    else:
        q=eob(P(t,21.98,0.25),1.3)
        txt(base,'ВЕСЬ АРСЕНАЛ НА ТОЙ ЖЕ ДОРОГЕ:',540,720,36,'mono',fill=LILAC,alpha=P(t,21.98,0.2))
        # ruler 40 mm = 880 px (22 px per mm)
        y=900; x0=100
        rrect(base,(x0-34,y-60,x0+914,y+60),10,fill=(214,196,140,255))
        for k in range(0,41):
            L=44 if k%10==0 else (30 if k%5==0 else 18); line(base,(x0+k*22,y-60),(x0+k*22,y-60+L),(40,30,20),2 if k%5 else 4,1.0)
            if k%10==0: txt(base,str(k//10)+' СМ' if k else '0',x0+k*22,y+20,28,'mono',fill=(40,30,20))
        w=125.4*eio(P(t,22.3,0.35)); 
        if w>1: rrect(base,(x0,y-20,x0+w,y+40),4,fill=RED+(255,)); glowrect(base,(x0,y-20,x0+w,y+40),RED,16,0.8,4,3)
        if t>=22.65:
            txt(base,'5,7 ММ',540,y+210,220,'disp',fill=RED,stroke=7,sfill=(10,8,14),glow=MAG,alpha=eo(P(t,22.65,0.2)))
        txt(base,'ОДИН ШАГ ИЗ 150 МЛН КМ',540,1280,40,'mono',fill=HI,alpha=P(t,23.2,0.2))
def sc_rice(base,t,t0):
    base.alpha_composite(S('rice',t,t0,24.92,0,1.0,1.12)); dim(base,0.18)
    txt(base,'≈ 6 ММ',540,1300,200,'disp',fill=HI,stroke=10,sfill=(10,8,14),glow=MAG,alpha=eo(P(t,t0+0.1,0.2)))
    credit(base,'Видео: Artem Podrez, Pexels',1760)
def sc_atm(base,t,t0):
    base.alpha_composite(Image.new('RGBA',(W,H),VOID+(255,)))
    cx,cy,r=540,940,300
    im=earth(r); comp(base,im,(cx-r,cy-r))
    peel=P(t,27.74,1.6)
    atm_ring(base,cx,cy,r+6,t,max(0.15,1-peel*0.8),16 if peel<1 else 6)
    if peel>0:
        rs=random.Random(11)
        for k in range(160):
            ang=rs.uniform(0,2*math.pi); sp=rs.uniform(0.6,1.4); ph=rs.uniform(0,0.4); q=clamp(peel*1.2-ph)
            if q<=0: continue
            rr=r+16+q*sp*520; x=cx+math.cos(ang)*rr; y=cy+math.sin(ang)*rr*0.95; a=1-q
            ImageDraw.Draw(base).ellipse((x-4,y-4,x+4,y+4),fill=SKY+(int(220*a),))
    txt(base,'АТМОСФЕРА',540,1380,130,'disp',fill=SKY,stroke=8,sfill=(10,8,14),glow=(40,90,200),alpha=eo(P(t,t0,0.2)))
    if t>=28.62:
        q=eob(P(t,28.62,0.22),1.4); dx,dy=shake(t,28.62,10,0.25)
        txt(base,'5 000 000 000 000',540+dx,1500+dy,100*(0.8+0.2*q),'disp',fill=GOLD,stroke=7,sfill=(10,8,14),glow=MAG,alpha=min(1,q*2))
        txt(base,'ХИРОСИМ',540,1600,60,'mono',fill=HI,alpha=P(t,28.8,0.2))
ROWS=[('ХИРОСИМА',6.28e13,PINK),('ЦАРЬ-БОМБА',2.09e17,HI),('ВЕСЬ АРСЕНАЛ',8.49e18,GOLD),('АТМОСФЕРА',3.22e26,SKY),('ЗЕМЛЯ ЦЕЛИКОМ',2.24e32,RED)]
def bw(E): return int((math.log10(E)-12.5)/20.0*800)
def sc_logbars(base,t,t0):
    base.alpha_composite(bg_void(t))
    txt(base,'ЭНЕРГИЯ, ДЖ · ЛОГАРИФМИЧЕСКАЯ ШКАЛА',540,560,34,'mono',fill=LILAC,alpha=eo(P(t,t0,0.2)))
    txt(base,'КАЖДАЯ ЧЕРТА = ×10',540,610,30,'mono',fill=LILAC,alpha=eo(P(t,t0,0.2))*0.8)
    x0=140; y0=730; dy=170
    for i,(nm,E,col) in enumerate(ROWS):
        ts=t0+0.1+i*0.28; p=eio(P(t,ts,0.45)); y=y0+i*dy
        txt(base,nm,x0,y-52,46,'disp',fill=col,anchor='lm',alpha=min(1,p*3))
        w=int(bw(E)*p)
        if w>2:
            rrect(base,(x0,y-24,x0+w,y+34),6,fill=col+(255,)); glowrect(base,(x0,y-24,x0+w,y+34),col,14,0.5,6,3)
        for k in range(0,21,2): line(base,(x0+k*40,y+46),(x0+k*40,y+54),(90,80,100),2,0.7*min(1,p*3))
        if p>0.95: txt(base,'%.1e'%E,x0+bw(E)+16,y+5,36,'mono',fill=HI,anchor='lm') if E<1e30 else None
    if t>=31.3:
        q=eob(P(t,31.3,0.25),1.3); xa=x0+bw(ROWS[2][1]); xb=x0+bw(ROWS[3][1]); ym=y0+2*dy+80
        line(base,(xa,ym),(xb,ym),RED,6,q); line(base,(xa,ym-14),(xa,ym+14),RED,6,q); line(base,(xb,ym-14),(xb,ym+14),RED,6,q)
        txt(base,'НЕ ХВАТАЕТ В 38 000 000 РАЗ',540,1560,52,'disp',fill=RED,stroke=6,sfill=(10,8,14),glow=MAG,alpha=min(1,q*2))
def sc_sun(base,t,t0):
    base.alpha_composite(Image.new('RGBA',(W,H),VOID+(255,)))
    cx,cy,r=540,840,400
    pu=1+0.015*math.sin((t-t0)*12); glowdisc(base,cx,cy,r*pu,(255,120,30),0.8,70); s=sunim(r*pu); comp(base,s,(cx-s.width/2,cy-s.height/2))
    v=min(0.84,(t-t0)*0.84/1.1) if t>=t0 else 0
    done=v>=0.84
    txt(base,'СОЛНЦЕ ОТДАЁТ СТОЛЬКО ЗА',540,1320,46,'mono',fill=HI,alpha=eo(P(t,t0+0.1,0.2)))
    txt(base,('%.2f'%v).replace('.',',')+' С',540,1450,210,'disp',fill=(RED if done else HI),stroke=10,sfill=(10,8,14),glow=MAG,gr=30)
def sc_chx(base,t,t0):
    base.alpha_composite(kb(still('gen_chicxulub.jpg',None,1.0),t,t0,3.9,1.0,1.18,.5,.5)); dim(base,0.12)
    txt(base,'ЧИКСУЛУБ',540,1130,150,'disp',fill=HI,stroke=9,sfill=(10,8,14),glow=MAG,alpha=eo(P(t,t0,0.2)))
    txt(base,'66 МЛН ЛЕТ НАЗАД',540,1230,42,'mono',fill=PINK,alpha=eo(P(t,t0+0.2,0.2)))
    if t>=37.22:
        q=eob(P(t,37.22,0.25),1.3); txt(base,'× 12 000',540,1360,190*(0.8+0.2*q),'disp',fill=GOLD,stroke=10,sfill=(10,8,14),glow=MAG,alpha=min(1,q*2))
        txt(base,'МОЩНЕЕ ВСЕГО АРСЕНАЛА',540,1480,44,'mono',fill=HI,alpha=P(t,37.4,0.2))
    credit(base,'Иллюстрация: Grok (ИИ). Энергия удара ≈ 10^23 Дж',1790)
def sc_alive(base,t,t0):
    base.alpha_composite(Image.new('RGBA',(W,H),VOID+(255,)))
    cx,cy,r=540,880,310; im=earth(r); comp(base,im,(cx-r,cy-r)); atm_ring(base,cx,cy,r+6,t,0.9,12)
    ringp(base,cx,cy,r+40,TEAL,6,0.9*eo(P(t,t0,0.3)))
    if t>=40.34: stamp(base,'ЦЕЛА',540,1330,t,40.34,TEAL,200,-5,'ЗЕМЛЯ НЕ ТРЕСНУЛА')
def sc_planet(base,t,t0):
    base.alpha_composite(S('gloom',t,t0,44.04,0,1.0,1.12)); dim(base,0.45)
    if t>=41.02: txt(base,'ПЛАНЕТЕ — НИЧЕГО',540,700,110,'disp',fill=TEAL,stroke=8,sfill=(10,8,14),glow=(20,90,80),alpha=eo(P(t,41.02,0.2)))
    if t>=42.34:
        q=eob(P(t,42.34,0.2),1.4); dx,dy=shake(t,42.34,12,0.3); txt(base,'А НАМ?',540+dx,880+dy,230*(0.8+0.2*q),'disp',fill=RED,stroke=11,sfill=(10,8,14),glow=MAG,alpha=min(1,q*2),rot=-4)
def sc_winter(base,t,t0):
    base.alpha_composite(S('etna',t,t0,47.5,0,1.0,1.12)); dim(base,0.55)
    txt(base,'ЛЮДЕЙ НА ЗЕМЛЕ: ≈ 8 МЛРД',540,650,44,'mono',fill=HI,alpha=eo(P(t,t0,0.2)))
    n=int(clamp((t-44.78)/2.35)*62); 
    for i in range(100):
        r_,c_=divmod(i,10); cx=140+c_*90; cy=760+r_*66
        if i<int(clamp((t-t0)/0.5)*100):
            col=RED if i<n else (170,150,175); rr=22
            ImageDraw.Draw(base).ellipse((cx-rr,cy-rr+4,cx+rr,cy+rr-4),fill=col+(255,))
    if t>=46.1:
        q=eob(P(t,46.1,0.22),1.4); txt(base,'> 5 МЛРД',540,1500-0,150*(0.8+0.2*q),'disp',fill=RED,stroke=9,sfill=(10,8,14),glow=MAG,alpha=min(1,q*2))
    credit(base,'Оценка голода: Xia et al., Nature Food, 2022',1790)
def sc_bait(base,t,t0):
    base.alpha_composite(S('shelf',t,t0,50.76,0,1.0,1.08)); dim(base,0.6)
    txt(base,'ТВОЙ КОММЕНТАРИЙ ↓',540,610,54,'mono',fill=HI,alpha=eo(P(t,t0,0.2)))
    p=eob(P(t,t0+0.1,0.25),1.2); plate(base,(80,680,1000,1180),6,p)
    full='ЭТО В 26 ТРИЛЛИОНОВ РАЗ МЕНЬШЕ, ЧЕМ…'
    n=int(clamp((t-48.52)/1.9)*len(full)); s=full[:n]
    words=s.split(' '); lines=['','','']; 
    # wrap manually
    cur=0
    for w in words:
        if len((lines[cur]+' '+w).strip())>16: cur=min(2,cur+1)
        lines[cur]=(lines[cur]+' '+w).strip()
    for i,l in enumerate(lines):
        if l: txt(base,l,110,780+i*115,100,'disp',fill=INK,anchor='lm')
    if int(t*3)%2==0:
        li=max(0,max([i for i,l in enumerate(lines) if l] or [0])); tw=tw_of(lines[li],'disp',100) if lines[li] else 0
        rrect(base,(120+tw,740+li*115,132+tw,820+li*115),3,fill=MAG+(255,))
def sc_end(base,t,t0):
    base.alpha_composite(S('etna',t,t0,53.72,2.5,1.0,1.1)); dim(base,0.6,(10,8,22))
    e=earth(150); comp(base,e,(330-150,1000-150)); atm_ring(base,330,1000,150,t,0.9,8)
def subbtn(base,t):
    if t>=51.82:
        p=eob(P(t,51.82,0.2),1.3); rrect(base,(540-260*p,640,540+260*p,735),48,fill=RED+(255,))
        if p>0.6: txt(base,'ПОДПИСАТЬСЯ',540,688,56,'disp',fill=HI)
Q='ХВАТИТ ЛИ БОМБ НА КОНЕЦ СВЕТА?'
HV=[(0,'НУЖНО: 3,6 КВИНТ.'),(4.58,'ЕСТЬ: 135 000'),(6.86,'1 ХИР. = 15 КТ'),(9.98,'ЗЕМЛЯ: ЦЕЛА?'),(11.42,'ЗЕМЛЯ: РАСКОЛ'),(12.9,'ЦАРЬ-БОМБА 50 МТ'),(16.6,'АРСЕНАЛ: 2 ГТ'),(19.1,'ДО СОЛНЦА 150 МЛН КМ'),(22.0,'АРСЕНАЛ: 5,7 ММ'),(24.92,'НЕ ХВАТАЕТ ×26 ТРЛН'),(27.08,'АТМОСФЕРА: 5 ТРЛН'),(30.0,'НЕ ХВАТАЕТ ×38 МЛН'),(33.08,'СОЛНЦЕ: 0,84 С'),(35.8,'ЧИКСУЛУБ: ×12 000'),(39.66,'ЗЕМЛЯ: ЦЕЛА'),(41.02,'ЛЮДИ: ПОД УДАРОМ'),(44.78,'ГОЛОД: > 5 МЛРД'),(47.5,'ТВОЙ ХОД'),(51.8,'ПОДПИШИСЬ')]
REDV={'ЗЕМЛЯ: РАСКОЛ','НЕ ХВАТАЕТ ×26 ТРЛН','НЕ ХВАТАЕТ ×38 МЛН','ГОЛОД: > 5 МЛРД','ЛЮДИ: ПОД УДАРОМ'}
def hud(base,t):
    a=eo(P(t,0.3,0.4))
    if a<=0: return
    rrect(base,(60,226,112,278),8,outline=RED,width=3,alpha=a); txt(base,'MB',86,253,28,'disp',fill=HI,alpha=a)
    n=int(clamp((t-0.5)/0.7)*len(Q)); txt(base,Q[:n],126,252,26,'dispb',fill=HI,anchor='lm',alpha=0.55*a) if n else None
    v=[s for tt,s in HV if t>=tt][-1]
    rrect(base,(640,230,1020,276),10,fill=(14,15,18,170),alpha=a)
    if int(t*2)%2==0: ImageDraw.Draw(base).ellipse((654,246,668,260),fill=RED+(int(255*a),))
    txt(base,v,1010,253,26,'tek',fill=(RED if v in REDV else HI),anchor='rm',alpha=a)
CAP=[(0.0,'ЧТОБЫ РАСКОЛОТЬ ЗЕМЛЮ'),(1.5,'НУЖНО 3,6'),(3.36,'КВИНТИЛЛИОНА ХИРОСИМ'),(4.58,'У ЧЕЛОВЕЧЕСТВА ИХ'),(5.66,'135 ТЫСЯЧ'),(6.86,'ХИРОСИМА'),(7.44,'15 КИЛОТОНН'),(8.58,'ТЯЖЁЛАЯ МЕРА'),(9.52,'ДРУГОЙ НЕТ'),(9.98,'ЗЕМЛЮ ДЕРЖИТ'),(10.62,'ГРАВИТАЦИЯ'),(11.42,'РАЗОБРАТЬ НА КУСКИ'),
(12.9,'КВАДРИЛЛИОН'),(13.68,'ЦАРЬ-БОМБ'),(14.24,'САМЫХ МОЩНЫХ ВЗРЫВОВ'),(15.6,'ЗА ВСЮ ИСТОРИЮ'),(16.6,'ВЕСЬ АРСЕНАЛ МИРА'),(17.56,'ОКОЛО 2 ГИГАТОНН'),(19.1,'ЭНЕРГИЯ РАСКОЛА ЗЕМЛИ'),(20.98,'ДОРОГА ДО СОЛНЦА'),(21.98,'АРСЕНАЛ'),(22.5,'ПОЧТИ 6 ММ'),(23.88,'РИСОВОЕ ЗЁРНЫШКО'),
(24.76,'НЕ ХВАТАЕТ'),(25.36,'В 26 ТРИЛЛИОНОВ РАЗ'),(27.08,'АТМОСФЕРУ'),(27.74,'СОРВАТЬ ПРОЩЕ'),(28.62,'5 ТРИЛЛИОНОВ ХИРОСИМ'),(29.98,'И ВСЁ РАВНО'),(30.7,'НЕ ХВАТАЕТ'),(31.3,'В 38 МИЛЛИОНОВ РАЗ'),(33.08,'СОЛНЦЕ СТОЛЬКО ОТДАЁТ'),(34.5,'МЕНЬШЕ ЧЕМ ЗА СЕКУНДУ'),
(35.8,'АСТЕРОИД ЧИКСУЛУБ'),(36.76,'В 12 000 РАЗ'),(38.2,'МОЩНЕЕ АРСЕНАЛА'),(39.38,'А ЗЕМЛЯ'),(40.06,'ДАЖЕ НЕ ТРЕСНУЛА'),(41.02,'ПЛАНЕТЕ НИЧЕГО'),(41.9,'НЕ БУДЕТ'),(42.6,'А НАМ БУДЕТ'),(43.0,'ЯДЕРНАЯ ЗИМА'),(43.98,'В ПЛОХОМ СЦЕНАРИИ'),(44.78,'БЕЗ ЕДЫ ОСТАНЕТСЯ'),(45.68,'БОЛЬШЕ 5 МИЛЛИАРДОВ'),(47.12,'ЧЕЛОВЕК'),
(47.5,'ДОПИШИ'),(48.1,'В КОММЕНТАРИЯХ'),(48.52,'ЭТО В 26 ТРИЛЛИОНОВ'),(50.16,'РАЗ МЕНЬШЕ, ЧЕМ…'),(51.5,'И ПОДПИШИСЬ'),(52.34,'ПОКА У НАС'),(52.88,'ЕСТЬ АТМОСФЕРА')]
KEYW={'ЧТОБЫ РАСКОЛОТЬ ЗЕМЛЮ','КВИНТИЛЛИОНА ХИРОСИМ','135 ТЫСЯЧ','15 КИЛОТОНН','РАЗОБРАТЬ НА КУСКИ','КВАДРИЛЛИОН','ОКОЛО 2 ГИГАТОНН','ПОЧТИ 6 ММ','РИСОВОЕ ЗЁРНЫШКО','В 26 ТРИЛЛИОНОВ РАЗ','НЕ ХВАТАЕТ','В 38 МИЛЛИОНОВ РАЗ','МЕНЬШЕ ЧЕМ ЗА СЕКУНДУ','В 12 000 РАЗ','ДАЖЕ НЕ ТРЕСНУЛА','А НАМ БУДЕТ','ЯДЕРНАЯ ЗИМА','БОЛЬШЕ 5 МИЛЛИАРДОВ','ДОПИШИ','И ПОДПИШИСЬ','ЕСТЬ АТМОСФЕРА','5 ТРИЛЛИОНОВ ХИРОСИМ'}
B.CAP=CAP; B.KEYW=KEYW
COVQ=('ХВАТИТ ЛИ БОМБ','РАСКОЛОТЬ ЗЕМЛЮ?')
def cover():
    b=Image.new('RGBA',(W,H),VOID+(255,)); e=earth(520); comp(b,e,(20,200)); dim(b,0.35)
    m=Image.open('/workspace/ref_markus.png').convert('RGBA')
    gl=Image.new('RGBA',m.size,MAG+(255,)); gl.putalpha(m.getchannel('A').filter(ImageFilter.GaussianBlur(40)).point(lambda v:int(v*0.6)))
    comp(b,gl,(0,300)); comp(b,m,(0,300))
    txt(b,'ХВАТИТ ЛИ БОМБ',540,300,140,'disp',fill=HI,stroke=10,sfill=(10,8,14),glow=VIOL)
    txt(b,'РАСКОЛОТЬ ЗЕМЛЮ?',540,460,150,'disp',fill=RED,stroke=12,sfill=(10,8,14),glow=MAG,gr=30)
    plate(b,(150,1560,930,1700),3); txt(b,'СЧИТАЕМ В ХИРОСИМАХ',540,1632,62,'disp',fill=INK)
    return b
TR={2.46:'punch',4.58:'glitch',6.86:'flash',8.58:'slice',9.98:'punch',11.42:'flash',12.9:'rgb',16.6:'whip',19.1:'dip',21.98:'punch',23.88:'whip',24.918:'rgb',27.08:'flash',29.98:'slice',33.08:'flash',35.8:'rgb',39.66:'dip',41.013:'glitch',44.04:'slice',47.5:'whip',50.758:'punch'}
def trans(base,t):
    for tb,ty in TR.items():
        d=t-tb
        if d<0 or d>0.3: continue
        p=clamp(d/0.24)
        if ty=='punch': return zoomc(base,1+0.22*(1-eo(p)))
        if ty=='glitch' and d<0.2: return glitch(base,t,1-p)
        if ty=='flash': flash(base,t,tb,0.85,0.16); return base
        if ty=='rgb' and p<1:
            a=np.asarray(base.convert('RGB')).copy(); s=int(26*(1-p)); a[...,0]=np.roll(a[...,0],s,1); a[...,2]=np.roll(a[...,2],-s,1); return Image.fromarray(a).convert('RGBA')
        if ty=='whip' and p<1:
            amp=int(200*(1-p)); a=np.asarray(base.convert('RGB')).astype(np.float32); acc=np.zeros_like(a)
            for k in range(7): acc+=np.roll(a,int(amp*k/6),1)
            return Image.fromarray((acc/7).astype(np.uint8)).convert('RGBA')
        if ty=='slice' and p<1:
            a=np.asarray(base.convert('RGB')).copy()
            for i,y in enumerate(range(0,H,120)): a[y:y+120]=np.roll(a[y:y+120],int(220*(1-p)*(1 if i%2 else -1)),1)
            return Image.fromarray(a).convert('RGBA')
        if ty=='dip' and d<0.16: comp(base,Image.new('RGBA',(W,H),(0,0,0,int(255*(1-d/0.16)))),(0,0)); return base
    return base
CIRC=(780,1400,300)
END=53.72
COV=None; VIG=None
def frame(f):
    global COV,VIG
    t=float(np.interp(f/25,_N,_O))
    if COV is None: COV=cover(); VIG=vign()
    if t>=END: return Image.new('RGB',(W,H),(0,0,0)).tobytes()
    if f<2: base=COV.copy(); hud(base,0.8); comp(base,VIG,(0,0),0.6); return base.convert('RGB').tobytes()
    capy=340; circ=None; full=False
    if t<2.458: base=av_full(t,1.0+0.06*eio(P(t,0,2.4))).convert('RGBA'); full=True
    elif t<4.58: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_s2(base,t,2.46)
    elif t<6.86: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_s3(base,t,4.58)
    elif t<8.58: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_s4(base,t,6.86)
    elif t<9.98: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_s5a(base,t,8.58)
    elif t<12.9: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_s5b(base,t,9.98)
    elif t<16.6: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_s6(base,t,12.9)
    elif t<19.1: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_s7(base,t,16.6)
    elif t<23.88: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_s8(base,t,19.1)
    elif t<24.918: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_rice(base,t,23.88)
    elif t<27.08:
        base=av_full(t,1.0+0.07*eio(P(t,24.918,2.1))).convert('RGBA'); full=True
        stamp(base,'НЕ ХВАТАЕТ',540,490,t,25.0,RED,160,-5)
    elif t<29.98: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_atm(base,t,27.08)
    elif t<33.08: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_logbars(base,t,29.98)
    elif t<35.8: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_sun(base,t,33.08)
    elif t<39.66: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_chx(base,t,35.8)
    elif t<41.013: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_alive(base,t,39.66)
    elif t<44.04: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_planet(base,t,41.013); circ=(CIRC,41.013)
    elif t<47.5: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_winter(base,t,44.04)
    elif t<50.758: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_bait(base,t,47.5)
    else: base=Image.new('RGBA',(W,H),VOID+(255,)); sc_end(base,t,50.758); subbtn(base,t); circ=(CIRC,50.758)
    base=trans(base,t)
    if circ: circle(base,t,f,*circ[0],t0=circ[1])
    cap(base,t,capy if not full else 1380)
    comp(base,VIG,(0,0),0.6 if full else 0.85)
    hud(base,t)
    return base.convert('RGB').tobytes()
def cap(base,t,y):
    s=[s for a,s in CAP if t>=a]
    if s and s[-1]: caption(base,t,y)
if __name__=='__main__':
    out=sys.argv[1]
    if out.endswith('.png'):
        for f in [int(x) for x in sys.argv[2].split(',')]:
            Image.frombytes('RGB',(W,H),frame(f)).save(out.replace('.png',f'_{f:04d}.png'))
        sys.exit()
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','25','-i','-','-c:v','ffv1','-level','3','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    with Pool(8) as pool:
        for i,fr in enumerate(pool.imap(frame,range(NF),chunksize=4)):
            ff.stdin.write(fr)
            if i%250==0: print(i,'/',NF,flush=True)
    ff.stdin.close(); ff.wait(); print('done',NF)
