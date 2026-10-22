from base import *
import base as B
TEAL=(63,206,194); NEU=(150,160,190); ICE=(170,210,255)
def credit(base,s): txt(base,s,540,1850,26,'mono',fill=HI,alpha=0.65)
def glowlayer(base,lay,r=14,k=1):
    g=lay.filter(ImageFilter.GaussianBlur(r))
    for _ in range(k): comp(base,g,(0,0))
    comp(base,lay,(0,0))
def fmt(n): return f'{int(n):,}'.replace(',',' ')
# ---------- motion graphics ----------
def scale_counter(base,t,t0,y=900,dur=1.4,final=1e9,sub='ТОНН'):
    q=eio(P(t,t0,dur)); n=final if q>=1 else 10**(9*q)
    a=P(t,t0,0.2)
    # balance: plate + pan + spoon icon dropping
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    sink=26*eo(P(t,t0+0.15,0.35))
    d.rounded_rectangle((300,y+150+sink,780,y+176+sink),12,fill=HI+(255,))
    d.rectangle((525,y+176+sink,555,y+330),fill=LILAC+(255,)); d.rounded_rectangle((380,y+320,700,y+350),12,fill=LILAC+(255,))
    sy=y-200+(350+sink)*eo(P(t,t0,0.18)) if t<t0+0.18 else y+150+sink-12
    d.ellipse((470,sy-40,590,sy+10),fill=GOLD+(255,)); d.rounded_rectangle((580,sy-30,760,sy-14),8,fill=GOLD+(255,))
    comp(base,lay,(0,0),a)
    plate(base,(90,y-330,990,y-90),11,a)
    s='≈ '+fmt(n); txt(base,s,540,y-235,120 if len(s)<12 else 100,'disp',fill=RED,alpha=a)
    txt(base,sub,540,y-140,50,'disp',fill=INK,alpha=a)
def sphere(base,cx,cy,R,col=ICE,core=HI):
    R=max(2,R); lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.ellipse((cx-R*1.6,cy-R*1.6,cx+R*1.6,cy+R*1.6),fill=col+(70,))
    g=lay.filter(ImageFilter.GaussianBlur(R*0.4+4)); comp(base,g,(0,0))
    d2=ImageDraw.Draw(base); d2.ellipse((cx-R,cy-R,cx+R,cy+R),fill=col+(255,)); d2.ellipse((cx-R*0.55,cy-R*0.6,cx+R*0.25,cy+R*0.2),fill=core+(255,))
def compress(base,t,t0):
    q=eio(P(t,t0,2.4)); R=520*(1-q)+40*q
    sphere(base,540,820,R)
    for i in range(10):
        a=i*math.pi/5+t*0.4; r0=R+120; r1=R+30
        arrow(base,(540+math.cos(a)*(r0+90),820+math.sin(a)*(r0+90)),(540+math.cos(a)*r1,820+math.sin(a)*r1),MAG,6,0.8*P(t,t0,0.3))
    if q>0.7: txt(base,'≈ 25 КМ',540,1150,110,'disp',fill=GOLD,stroke=8,sfill=(10,8,14),alpha=P(t,t0+1.8,0.25))
def arrow(base,p0,p1,col,w=12,alpha=1.0):
    if alpha<=0: return
    line(base,p0,p1,col,w,alpha); a=math.atan2(p1[1]-p0[1],p1[0]-p0[0]); L=w*4
    poly_layer(base,[p1,(p1[0]-L*math.cos(a-0.45),p1[1]-L*math.sin(a-0.45)),(p1[0]-L*math.cos(a+0.45),p1[1]-L*math.sin(a+0.45))],col,alpha)
def city_ring(base,t,t0):
    p=eio(P(t,t0,0.6)); lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.arc((140,560,940,1360),-90,-90+360*p,fill=RED+(255,),width=12); glowlayer(base,lay,12,1)
    if p>0.5: plate(base,(330,900,750,1020),4,P(t,t0+0.3,0.2)); txt(base,'25 КМ',540,960,90,'disp',fill=INK,alpha=P(t,t0+0.3,0.2))
def atom(base,t,t0):
    cx,cy=540,820; q=eio(P(t,t0+0.8,1.6))
    d=ImageDraw.Draw(base)
    for k in range(3):
        r=(330-60*k)*(1-q)+60*q
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(70,60,95,255),width=3)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); dl=ImageDraw.Draw(lay)
    for k in range(6):
        r=((330-60*(k%3))*(1-q)+40*q); a=t*(2.2+0.3*k)+k*1.05
        x,y=cx+math.cos(a)*r,cy+math.sin(a)*r
        if q<0.98: dl.ellipse((x-18,y-18,x+18,y+18),fill=TEAL+(255,))
    glowlayer(base,lay,10,1)
    conv=P(t,t0+1.9,0.6)
    for k,(dx,dy) in enumerate([(-30,-20),(28,-24),(0,26),(-26,22),(30,18),(2,-2)]):
        col=mix(RED,NEU,conv)
        d.ellipse((cx+dx-32,cy+dy-32,cx+dx+32,cy+dy+32),fill=col+(255,),outline=(20,16,26,255),width=3)
    y=1260
    txt(base,'e⁻',360,y,110,'disp',fill=TEAL,alpha=P(t,t0,0.2)); txt(base,'+',450,y,90,'disp',fill=HI,alpha=P(t,t0,0.2))
    txt(base,'p⁺',540,y,110,'disp',fill=RED,alpha=P(t,t0,0.2)); txt(base,'→',640,y,90,'disp',fill=HI,alpha=P(t,t0+1.9,0.2))
    txt(base,'n',740,y,120,'disp',fill=NEU,alpha=P(t,t0+1.9,0.2))
def packed(base,t,t0):
    d=ImageDraw.Draw(base); r=44; k=0
    for j in range(14):
        for i in range(13):
            x=i*88+(44 if j%2 else 0)+10; y=360+j*76
            if y>1500: continue
            p=eob(P(t,t0+0.004*k,0.25),1.2); k+=1
            if p<=0: continue
            rr=r*p; d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=NEU+(255,),outline=(30,26,40,255),width=3)
def burst(base,t,t0):
    q=P(t,t0,1.6); lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); cx,cy=540,780
    R0=60+900*eo(q)
    d.ellipse((cx-R0,cy-R0,cx+R0,cy+R0),outline=GOLD+(int(255*(1-q)),),width=16)
    rs=random.Random(9)
    for i in range(48):
        a=rs.uniform(0,6.283); sp=rs.uniform(0.5,1.0); r=40+850*eo(q)*sp
        x,y=cx+math.cos(a)*r,cy+math.sin(a)*r; s=rs.uniform(8,18)*(1-0.6*q)
        d.ellipse((x-s,y-s,x+s,y+s),fill=(NEU if i%3 else ICE)+(int(255*(1-q*0.8)),))
    if q<0.25:
        R=60*(1+3*eo(q*4)); d.ellipse((cx-R,cy-R,cx+R,cy+R),fill=HI+(int(255*(1-q*4)),))
    glowlayer(base,lay,18,2)
def earth_fall(base,t,t0):
    cx,cy,R=540,900,470; d=ImageDraw.Draw(base)
    for rr,col in [(R,(60,90,160)),(R*0.97,(170,95,60)),(R*0.55,(225,140,60)),(R*0.2,(250,215,120))]:
        d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=col+(255,))
    d.ellipse((cx-R,cy-R,cx+R,cy+R),outline=HI+(255,),width=4)
    txt(base,'КОРА',cx+R*0.62,cy-R*0.86,34,'mono',fill=HI); txt(base,'МАНТИЯ',cx+R*0.62,cy-R*0.25,34,'mono',fill=INK)
    txt(base,'ЯДРО',cx,cy+R*0.37,34,'mono',fill=INK)
    q=eio(P(t,t0+0.2,2.4)); y=cy-R-160+(2*R+320)*q
    if q>0: line(base,(cx,cy-R-160),(cx,y),(255,255,255),3,0.5)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); dl=ImageDraw.Draw(lay)
    dl.ellipse((cx-26,y-20,cx+26,y+20),fill=GOLD+(255,)); dl.rounded_rectangle((cx+18,y-8,cx+120,y+6),6,fill=GOLD+(255,))
    glowlayer(base,lay,10,1)
def pulsar(base,t,t0,cx,cy,R,speed=1.0):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    a=(t-t0)*speed*2*math.pi
    for s in (0,math.pi):
        b=a+s; L=1400
        p1=(cx+math.cos(b-0.08)*L,cy+math.sin(b-0.08)*L*0.55); p2=(cx+math.cos(b+0.08)*L,cy+math.sin(b+0.08)*L*0.55)
        d.polygon([(cx,cy),p1,p2],fill=ICE+(120,))
    glowlayer(base,lay,20,1); sphere(base,cx,cy,R)
def spin_counter(base,t,t0):
    q=eio(P(t,t0+0.9,1.6)); n=int(716*q)
    pulsar(base,t,t0,540,700,70,speed=0.6+2.4*q)
    plate(base,(170,1100,910,1360),12)
    txt(base,str(n),540,1200,170,'disp',fill=RED); txt(base,'ОБОРОТОВ В СЕКУНДУ',540,1310,46,'disp',fill=INK)
    txt(base,'PSR J1748−2446ad',540,1420,34,'mono',fill=HI,alpha=0.85)

GREEN=(120,220,140)
def nucleus(d,cx,cy,r,col_mix=0.0,seed=1,n=14):
    rs=random.Random(seed)
    for i in range(n):
        a=rs.uniform(0,6.283); rr=r*0.55*math.sqrt(rs.random())
        x,y=cx+math.cos(a)*rr,cy+math.sin(a)*rr; c=RED if i%2 else NEU
        d.ellipse((x-r*0.3,y-r*0.3,x+r*0.3,y+r*0.3),fill=c+(255,),outline=(20,16,26,255),width=2)
def neutron_dot(base,x,y,r=16):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(lay).ellipse((x-r,y-r,x+r,y+r),fill=TEAL+(255,)); glowlayer(base,lay,10,1)
def fission(base,t,t0):
    cx,cy=540,820; d=ImageDraw.Draw(base)
    q=P(t,t0,1.0); nx=80+(cx-80-110)*eio(q)
    sp=P(t,t0+1.1,1.6); 
    if sp<=0:
        wob=1+0.06*math.sin((t-t0)*30)*P(t,t0+0.9,0.2)
        nucleus(d,cx,cy,int(150*wob),seed=3,n=18)
        if q<1: neutron_dot(base,nx,cy)
    else:
        o=eo(sp)*330
        nucleus(d,cx-o,cy-o*0.4,110,seed=4,n=10); nucleus(d,cx+o,cy+o*0.4,110,seed=5,n=10)
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); dl=ImageDraw.Draw(lay); R=40+500*eo(sp)
        dl.ellipse((cx-R,cy-R,cx+R,cy+R),outline=GOLD+(int(255*(1-sp)),),width=10); glowlayer(base,lay,14,1)
def fragments(base,t,t0):
    cx,cy=540,820; d=ImageDraw.Draw(base); sp=0.6+0.4*eo(P(t,t0,1.2)); o=330*sp
    nucleus(d,cx-o,cy-o*0.4,110,seed=4,n=10); nucleus(d,cx+o,cy+o*0.4,110,seed=5,n=10)
    q=P(t,t0+0.9,1.2)
    if q>0:
        for a in (-1.2,0.3,1.9):
            r=40+600*eo(q); neutron_dot(base,cx+math.cos(a)*r,cy+math.sin(a)*r)
def chain(base,t,t0,levels_t,cx=540,y0=420,dy=150):
    d=ImageDraw.Draw(base); nodes=[[(cx,y0)]]
    for L in range(1,7):
        prev=nodes[-1]; span=880/(2**L); nodes.append([ (x+s*span/2*1.0, y0+L*dy) for x,_ in prev for s in (-1,1)])
    shown=0
    for L,lt in enumerate(levels_t):
        p=eo(P(t,lt,0.3))
        if p<=0: break
        shown=L
        for j,(x,y) in enumerate(nodes[L]):
            if L>0:
                px,py=nodes[L-1][j//2]; ex,ey=px+(x-px)*p,py+(y-py)*p
                d.line([(px,py),(ex,ey)],fill=LILAC+(255,),width=max(2,6-L))
            r=max(5,26-3*L)*p; d.ellipse((x-r,y-r,x+r,y+r),fill=(GOLD if L%2 else RED)+(255,))
    return 2**shown
def density(base,t,t0):
    d=ImageDraw.Draw(base); rs=random.Random(2)
    for side,(x0,n,ok) in enumerate([(60,7,False),(560,40,True)]):
        rrect(base,(x0,560,x0+460,1180),24,outline=LILAC,width=4)
        pts=[(x0+40+rs.random()*380,600+rs.random()*540) for _ in range(n)]
        for (x,y) in pts: d.ellipse((x-18,y-18,x+18,y+18),fill=RED+(255,))
        q=P(t,t0+0.4,1.4)
        for k in range(3 if not ok else 9):
            a=k*2.1+side; r=q*(500 if not ok else 200)
            neutron_dot(base,x0+230+math.cos(a)*r,870+math.sin(a)*r,12)
        txt(base,'МАЛО ЯДЕР' if not ok else 'ДОСТАТОЧНО',x0+230,1260,58,'disp',fill=(HI if not ok else GOLD))
        txt(base,'реакция гаснет' if not ok else 'реакция растёт',x0+230,1340,36,'mono',fill=HI,alpha=0.85)
def bars(base,t,t0):
    p=eio(P(t,t0+0.3,1.6)); plate(base,(90,520,990,1420),12)
    rrect(base,(160,1300,300,1310),3,fill=RED+(255,)); txt(base,'ХИРОСИМА',230,1360,40,'disp',fill=INK)
    h=int(720*p); rrect(base,(560,1310-h,860,1310),8,fill=MAG+(255,))
    txt(base,'ЦАРЬ-БОМБА',710,1360,40,'disp',fill=INK)
    txt(base,'×'+fmt(3000*p) if p<1 else '× 3 000',710,1250-h,70,'disp',fill=RED)
    txt(base,'1961',300,620,90,'disp',fill=INK)
def merge(base,t,t0):
    q=eio(P(t,t0,1.0)); d=ImageDraw.Draw(base); cx,cy=540,820
    if q<1:
        for s in (-1,1): nucleus(d,cx+s*260*(1-q),cy,60,seed=7+s,n=4)
    else:
        nucleus(d,cx,cy,80,seed=9,n=6); lay=Image.new('RGBA',(W,H),(0,0,0,0)); R=60+400*eo(P(t,t0+1,0.8))
        ImageDraw.Draw(lay).ellipse((cx-R,cy-R,cx+R,cy+R),outline=GOLD+(int(255*(1-P(t,t0+1,0.8))),),width=10); glowlayer(base,lay,14,1)
CAP=[(0.0,'ТРИ ЧИСЛА'),(1.3,'И ТЫ ПОНИМАЕШЬ'),(2.02,'ЯДЕРНУЮ БОМБУ'),(3.32,'ЧИСЛО ПЕРВОЕ'),(4.26,'ОДИН НЕЙТРОН'),(5.42,'ВЛЕТАЕТ В ЯДРО'),(7.36,'ЯДРО РАСКАЛЫВАЕТСЯ'),(9.06,'ОСКОЛКИ РАЗЛЕТАЮТСЯ'),(11.38,'НОВЫЕ НЕЙТРОНЫ'),
(12.84,'ЧИСЛО ВТОРОЕ'),(13.76,'2'),(14.02,'4'),(14.64,'8'),(15.1,'КАЖДЫЙ РАСКАЛЫВАЕТ'),(16.26,'СЛЕДУЮЩЕЕ ЯДРО'),(17.3,'ЦЕПНАЯ РЕАКЦИЯ'),(18.5,'ИДЁТ, ТОЛЬКО ЕСЛИ'),(19.52,'ЯДЕР РЯДОМ ДОСТАТОЧНО'),(21.0,'КРИТИЧЕСКАЯ МАССА'),
(22.3,'ЧИСЛО ТРЕТЬЕ'),(23.1,'И ЭТО ПОВОРОТ'),(24.4,'МЕНЬШЕ ГРАММА'),(25.36,'СТОЛЬКО МАССЫ'),(26.08,'СТАЛО ЭНЕРГИЕЙ'),(27.02,'НАД ХИРОСИМОЙ'),(27.86,'МЕНЬШЕ СКРЕПКИ'),(29.2,'ФОРМУЛА ЭЙНШТЕЙНА'),(31.7,'СКОРОСТЬ СВЕТА В КВАДРАТЕ'),
(32.94,'ГИГАНТСКИЙ МНОЖИТЕЛЬ'),(34.06,'ДЕЛЕНИЕ КАК СПИЧКА'),(36.08,'ДЛЯ СЛИЯНИЯ ЯДЕР'),(37.04,'КАК В СОЛНЦЕ'),(37.7,'ЦАРЬ-БОМБА, 1961'),(39.28,'В 3000 РАЗ СИЛЬНЕЕ'),(41.72,'В ХИРОСИМЕ ПОГИБЛИ'),(42.7,'ДЕСЯТКИ ТЫСЯЧ ЛЮДЕЙ'),
(44.04,'ЭТИ ЧИСЛА СТОИТ ЗНАТЬ'),(45.34,'ЧЕСТНО'),(45.84,'БОЛЬШЕ ПОЛЬЗЫ'),(48.32,'ИЛИ ВРЕДА?'),(48.96,'ЖДУ АРГУМЕНТЫ'),(49.66,'ПОДПИШИСЬ')]
B.CAP=CAP; B.KEYW={'ЧИСЛО ПЕРВОЕ','ЧИСЛО ВТОРОЕ','ЧИСЛО ТРЕТЬЕ','И ЭТО ПОВОРОТ','МЕНЬШЕ ГРАММА','ПОДПИШИСЬ','КРИТИЧЕСКАЯ МАССА','ЖДУ АРГУМЕНТЫ'}
def cover():
    b=kb(still('trinity.jpg'),0,0,1,1.0,1.0,.5,.5); b=Image.blend(b,Image.new('RGBA',(W,H),VOID+(255,)),0.35)
    m=Image.open('/workspace/ref_markus.png').convert('RGBA')
    gl=Image.new('RGBA',m.size,MAG+(255,)); gl.putalpha(m.getchannel('A').filter(ImageFilter.GaussianBlur(40)).point(lambda v:int(v*0.6)))
    comp(b,gl,(0,260)); comp(b,m,(0,260))
    txt(b,'КАК РАБОТАЕТ',540,250,140,'disp',fill=HI,stroke=10,sfill=(10,8,14),glow=VIOL)
    txt(b,'ЯДЕРНАЯ БОМБА',540,410,130,'disp',fill=RED,stroke=12,sfill=(10,8,14),glow=MAG,gr=30)
    plate(b,(170,1560,910,1700),3); txt(b,'ТРИ ЧИСЛА',540,1632,70,'disp',fill=INK)
    return b
COV=None; VIG=None
def frame(f):
    global COV,VIG
    t=f/25
    if COV is None: COV=cover(); VIG=vign()
    if f<3: base=COV.copy(); comp(base,VIG,(0,0),0.6); return base.convert('RGB').tobytes()
    capy=1560
    if t<2.02:
        base=av_full(t,1.0).convert('RGBA')
    elif t<3.32:
        base=kb(still('trinity.jpg'),t,2.02,1.3,1.0,1.06,.5,.5)
        plate(base,(250,1180,830,1300),4); txt(base,'TRINITY · 16.07.1945',540,1240,56,'disp',fill=INK)
        circle(base,t,f,820,1600,280,2.02); capy=330
        credit(base,'фото: US DOE / Los Alamos, общественное достояние')
    elif t<5.42:
        base=bg_void(t); plate(base,(240,520,840,1000),9,P(t,3.35,0.15)); txt(base,'1',540,740,330,'disp',fill=RED,alpha=P(t,3.35,0.15))
        if t>=4.5: neutron_dot(base,540,1120,26); txt(base,'НЕЙТРОН',540,1200,56,'disp',fill=TEAL)
        circle(base,t,f,540,1560,340,3.32); capy=330
    elif t<9.06:
        base=bg_void(t); fission(base,t,5.42); circle(base,t,f,850,1650,260); capy=330
    elif t<10.7:
        base=foot('bill',t,9.06,1.0,1.04); circle(base,t,f,850,1650,260); capy=330
        credit(base,'видео: Tima Miroshnichenko / Pexels')
    elif t<12.84:
        base=bg_void(t); fragments(base,t,10.7); capy=1500
    elif t<17.3:
        base=bg_void(t); n=chain(base,t,12.84,[12.9,13.76,14.02,14.64,15.4,16.0,16.6]); capy=230
        plate(base,(300,1520,780,1660),5); txt(base,fmt(n)+' ДЕЛЕНИЙ' if n>1 else '1 ДЕЛЕНИЕ',540,1590,64,'disp',fill=INK)
    elif t<18.5:
        base=bg_void(t); chain(base,t,0,[0,0,0,0,0,0,0]); stamp(base,'ЦЕПНАЯ РЕАКЦИЯ',540,1650,t,17.4,RED,100,-5); capy=230
    elif t<20.76:
        base=bg_void(t); density(base,t,18.5); capy=330
    elif t<22.3:
        base=bg_void(t); plate(base,(150,520,930,820),9); txt(base,'КРИТИЧЕСКАЯ',540,620,96,'disp',fill=INK); txt(base,'МАССА',540,730,96,'disp',fill=RED)
        circle(base,t,f,540,1250,560,20.76); capy=1700
    elif t<24.4:
        base=av_full(t,1.0).convert('RGBA'); flash(base,t,22.3,0.5,0.14)
    elif t<25.36:
        base=bg_void(t); plate(base,(190,560,890,980),9); txt(base,'< 1 Г',540,730,220,'disp',fill=RED); txt(base,'МАССЫ',540,900,70,'disp',fill=INK)
        circle(base,t,f,540,1450,380,24.4); capy=330
    elif t<27.86:
        base=kb(still('dome.jpg'),t,25.36,2.5,1.0,1.06,.5,.45)
        plate(base,(200,1200,880,1320),4); txt(base,'ХИРОСИМА · 6.08.1945',540,1260,56,'disp',fill=INK)
        credit(base,'Купол Гэмбаку · фото: DXR, CC BY-SA 4.0'); capy=330
    elif t<29.2:
        base=foot('clips',t,27.86,1.0,1.04); base=Image.blend(base,bg_void(t),0.25)
        plate(base,(160,500,920,760),7); txt(base,'≈ 0,7 Г  <  СКРЕПКА',540,630,80,'disp',fill=INK)
        circle(base,t,f,820,1500,320,27.86); capy=1750
        credit(base,'видео: Katrin Bolovtsova / Pexels')
    elif t<31.56:
        base=kb(still('einstein.jpg',(0,300,3250,4333)),t,29.2,2.4,1.0,1.06,.5,.4); base=Image.blend(base,bg_void(t),0.3)
        if t>=30.1: plate(base,(170,1130,910,1350),8,P(t,30.1,0.15)); txt(base,'E = mc²',540,1240,150,'disp',fill=RED,alpha=P(t,30.1,0.15))
        circle(base,t,f,840,520,300,29.2); capy=1600
        credit(base,'фото: Orren Jack Turner, 1947, общественное достояние')
    elif t<34.06:
        base=bg_void(t); q=eio(P(t,31.7,1.4)); n=9e16*q
        plate(base,(80,640,1000,1060),11)
        txt(base,'c² ≈',540,740,90,'disp',fill=INK); txt(base,fmt(n),540,880,76,'disp',fill=RED)
        txt(base,'м²/с²',540,990,44,'mono',fill=INK); capy=330
    elif t<35.7:
        base=foot('match',t,34.06,1.0,1.04); capy=1560
        credit(base,'видео: Solo World / Pexels')
    elif t<37.7:
        base=kb(still('sun.jpg'),t,35.7,2.0,1.0,1.06,.5,.5); base=Image.blend(base,bg_void(t),0.45); merge(base,t,36.1)
        txt(base,'СЛИЯНИЕ ЯДЕР',540,1250,70,'disp',fill=GOLD,stroke=7,sfill=(10,8,14),alpha=P(t,36.1,0.2))
        credit(base,'Солнце: NASA/SDO (AIA)'); capy=330
    elif t<41.72:
        base=bg_void(t); bars(base,t,38.9); capy=330
    elif t<45.34:
        base=kb(still('dome.jpg',(600,0,3240,2743)),t,41.72,3.6,1.12,1.04,.5,.4); base=Image.blend(base,bg_void(t),0.2)
        credit(base,'Мемориал мира в Хиросиме · фото: DXR, CC BY-SA 4.0'); capy=1560
    elif t<49.6:
        base=bg_void(t)
        plate(base,(110,360,970,760),9,P(t,45.4,0.15))
        txt(base,'ОТКРЫТИЕ ДЕЛЕНИЯ ЯДРА:',540,450,62,'disp',fill=INK,alpha=P(t,45.4,0.15))
        txt(base,'БОЛЬШЕ ПОЛЬЗЫ',540,560,80,'disp',fill=TEAL,alpha=P(t,45.9,0.15)); txt(base,'ИЛИ ВРЕДА?',540,660,80,'disp',fill=RED,alpha=P(t,48.3,0.15))
        txt(base,'аргументы в комментарии',540,820,40,'mono',fill=HI,alpha=P(t,49.0,0.2))
        circle(base,t,f,540,1260,560,45.34); capy=1720
    else:
        base=av_full(t,1.0).convert('RGBA')
        if t>=49.7:
            p=eob(P(t,49.7,0.3),1.5); rrect(base,(540-330*p,1290,540+330*p,1430),70,fill=RED+(255,))
            if p>0.6: txt(base,'ПОДПИСАТЬСЯ',540,1360,70,'disp',fill=HI)
        capy=330
    caption(base,t,capy)
    comp(base,VIG,(0,0),0.85)
    return base.convert('RGB').tobytes()
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
