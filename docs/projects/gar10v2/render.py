import sys,os,math,random,json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
from lib import *
import lib
CR=(246,239,226); INK=(34,28,24); OL=(96,116,40); OLL=(176,196,92); PL=(128,40,78); GO=(222,176,72); RD=(200,50,50); WH=(255,252,245)
TOT=57.60; NF=int(round(TOT*FPS))
SH='/workspace/gar10/b/shots/'; AV='/workspace/gar10/av/f/'
LAG=0.023; M=json.load(open('/workspace/gar10/av/meta.json')); SEG={k:(v['t0'],v['t1'],v['c0']) for k,v in M.items()}
X0,X1=120,780; CX=(X0+X1)//2
# (t0, kind, src, off, z0, z1)
S=[(0.0,'av'),(3.05,'intro','10071217',0,1.05,1.15),(4.77,'v','7601421',0,1.0,1.12),(7.12,'chem','7237297',0,1.1,1.2),
(9.61,'v','39137542',0,1.0,1.15),(11.65,'timer','7525923',0,1.0,1.08),(14.27,'bp','6998172',0,1.0,1.1),(18.98,'chol','8530073',0,1.05,1.12),
(23.00,'cold','10071217',3,1.15,1.2),(27.19,'cancer','37138963',0,1.0,1.05),(28.40,'obs','37138963',1.0,1.05,1.15),(33.28,'obs2','7601421',3,1.1,1.15),
(35.72,'rct','8530073',2,1.0,1.1),(40.34,'rct2','8530073',4,1.1,1.15),(44.39,'oil','25745552',0,1.0,1.12),(47.76,'oil2','37223242',0,1.05,1.15),
(50.78,'warn','10431987',0,1.0,1.06),(53.13,'v','37223242',3,1.0,1.1),(55.31,'loop','10071217',0,1.15,1.0)]
TR={3.05:'wipe',4.77:'punch',7.12:'wipe',9.61:'flash',11.65:'wipe',14.27:'punch',18.98:'wipe',23.00:'punch',27.19:'flash',28.40:'wipe',33.28:'punch',
35.72:'wipe',40.34:'punch',44.39:'wipe',47.76:'punch',50.78:'flash',53.13:'wipe',55.31:'punch'}
CAP=[(0.02,'ЧЕСНОК ПРОТИВ РАКА',1),(1.67,'ПРАВДА ИЛИ МИФ?',0),(3.13,'ПО ИССЛЕДОВАНИЯМ',0),(4.77,'ЦЕЛЫЙ ЗУБЧИК',0),(5.65,'ПОЧТИ БЕСПОЛЕЗЕН',1),
(7.12,'РАЗДАВИ ЕГО',0),(8.0,'И ПОЯВИТСЯ АЛЛИЦИН',1),(9.61,'НО ЖАР УБИВАЕТ ФЕРМЕНТ',1),(11.65,'ПОДОЖДИ 10 МИНУТ',1),(12.93,'ПОТОМ НА СКОВОРОДУ',0),
(14.27,'ДАВЛЕНИЕ',0),(15.26,'У ГИПЕРТОНИКОВ',1),(16.23,'ВЕРХНЕЕ ПАДАЛО',0),(17.04,'ПОЧТИ НА 9 ММ',1),(18.98,'ХОЛЕСТЕРИН',0),(20.03,'МИНУС ~10%',1),(21.76,'ЗА ПАРУ МЕСЯЦЕВ',0),
(23.00,'ПРОСТУДА',0),(23.95,'ВСЕГО ОДНО ИСПЫТАНИЕ',1),(26.16,'ЭТОГО МАЛО',0),(27.19,'ТЕПЕРЬ — РАК',1),(28.40,'КТО ЕСТ МНОГО',0),(29.28,'ЧЕСНОКА И ЛУКА',1),
(30.46,'РАК ЖЕЛУДКА',0),(31.59,'ПОЧТИ ВДВОЕ РЕЖЕ',1),(33.28,'НО ЭТО НАБЛЮДЕНИЯ',0),(34.44,'А НЕ ДОКАЗАТЕЛЬСТВО',1),(35.72,'КИТАЙ: 3 ТЫСЯЧИ ЧЕЛОВЕК',0),
(37.62,'7 ЛЕТ',1),(38.19,'ЧЕСНОК ИЛИ ПЛАЦЕБО',0),(40.34,'ЧЕРЕЗ 22 ГОДА',0),(41.60,'СМЕРТНОСТЬ ОТ РАКА',0),(42.94,'НИЖЕ НА ТРЕТЬ',1),
(44.39,'А МАСЛО?',1),(45.31,'ВЕЩЕСТВА ЧЕСНОКА',0),(46.28,'РАСТВОРЯЮТСЯ В ЖИРАХ',1),(47.76,'НО ИСПЫТАНИЙ',0),(48.44,'С ОЛИВКОВЫМ',0),(49.13,'ИЛИ ЛЬНЯНЫМ',0),(49.76,'МАСЛОМ — НЕТ',1),
(50.78,None,0),(53.13,'ОТПРАВЬ ТОМУ,',0),(53.81,'КТО ЛЕЧИТСЯ ЧЕСНОКОМ',1),(55.31,'И ОТВЕТЬ:',0),(56.14,'ПРАВДА ИЛИ МИФ?',1)]
CLAIM=[(14.27,1),(18.98,2),(23.00,3),(28.40,4),(35.72,5),(44.39,6)]
SRC=[(9.61,'Song & Milner, J Nutr 2001 (опыты на крысах)'),(14.27,'Ried, J Nutr 2016: 20 РКИ, 970 чел.'),(18.98,'Ried 2016 (обзор 39 РКИ); эффект при повышенном'),
(23.00,'Cochrane, Lissiman 2014: 1 РКИ, 146 чел.'),(28.40,'Zhou, Gastroenterology 2011: 21 исследование'),(35.72,'Li, BMJ 2019: Shandong Intervention Trial'),
(44.39,'Прямых испытаний сочетания нет'),(50.78,None)]
_ic={}
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
def soft(im,r=6,dk=0.55): return ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(r))).enhance(dk)
CARD_KINDS=('chem','timer','bp','chol','cold','obs','rct','rct2','oil','oil2','warn')
def shot_img(t,k):
    s=S[k]; t0=s[0]; d=nxt(k)-t0; kind=s[1]
    if kind=='av': return kb(avf('A',t),t,t0,d,1.0,1.04,0.5,0.42)
    im=vframe(s[2],int((t-t0+s[3])*FPS))
    if kind in CARD_KINDS: im=soft(im,4,0.62)
    return kb(im,t,t0,d,s[4],s[5])
def P(t,t0,d): return clamp((t-t0)/d)
lib.P=P
def fit(s,kind,size,maxw):
    while size>24 and tw_of(s,kind,size)>maxw: size-=2
    return size
def card(b,box,alpha=1.0,col=CR,r=26):
    x0,y0,x1,y1=box
    sh=Image.new('RGBA',(int(x1-x0)+80,int(y1-y0)+80),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((40,52,x1-x0+40,y1-y0+52),r,fill=(0,0,0,110)); sh=sh.filter(ImageFilter.GaussianBlur(16))
    comp(b,sh,(x0-40,y0-40),alpha); rrect(b,box,r,fill=col+(int(250*alpha),))
def slide(t,t0,d=0.35): return (1-eo(P(t,t0,d)))*120
# ================= TEXT-FIT LAYOUT SYSTEM (gar10v2) =================
SAFE=(120,270,780,1250); PAD=24; MINB=42
REG=[]; TOP=[]; WARN=[]
def reg_text(name,ink,cont,pad=PAD): REG.append((name,ink,cont,pad))
def reg_top(name,box): TOP.append((name,box))
def ink_of(s,kind,size): return font(kind,int(size)).getbbox(s,anchor='ls')
def line_box(kind,size):
    l,t,r,b=font(kind,int(size)).getbbox('ЁЙНрув',anchor='ls'); return t,b
def draw_line(b,s,kind,size,cx,top,col,alpha=1.0,name='',cont=None,pad=PAD,left=None,lh_size=None):
    """draw s so its line box starts at top; centered on cx (or left-aligned at left). returns ink box"""
    f=font(kind,int(size)); l,t,r,bb=f.getbbox(s,anchor='ls'); lt,lb=line_box(kind,lh_size or size)
    base=top-lt; x=(left-l) if left is not None else cx-(l+r)/2
    ink=(x+l,base+t,x+r,base+bb)
    if alpha>0.003:
        lay=Image.new('RGBA',(int(r-l)+8,int(bb-t)+8),(0,0,0,0))
        ImageDraw.Draw(lay).text((4-l,4-t),s,font=f,fill=col+(255,),anchor='ls')
        comp(b,lay,(int(round(x+l-4)),int(round(base+t-4))),alpha)
    if cont is not None: reg_text(name or s,ink,cont,pad)
    return ink
def fit_lines(s,kind,size,minsz,maxw):
    parts=s.split('\n')
    if len(parts)==1:
        sz=size
        while sz>minsz and font(kind,sz).getlength(s)>maxw: sz-=1
        if font(kind,sz).getlength(s)<=maxw: return sz,[s]
    sz=minsz if len(parts)==1 else size
    while True:
        lines=[]
        for p in parts:
            cur=''
            for w in p.split(' '):
                c=(cur+' '+w).strip()
                if font(kind,sz).getlength(c)<=maxw or not cur: cur=c
                else: lines.append(cur); cur=w
            lines.append(cur)
        if all(font(kind,sz).getlength(x)<=maxw for x in lines) or sz<=16: break
        sz-=1
    if sz<minsz: WARN.append(f'{s!r} shrunk to {sz}<{minsz}')
    return sz,lines
class Stack:
    def __init__(s,x0=X0,x1=X1,pad=32,gap=12): s.x0,s.x1,s.pad,s.gap=x0,x1,pad,gap; s.it=[]
    def text(s,txt,kind,size,col,minsz=MINB,alpha=1.0,sc=1.0,name=None):
        sz,lines=fit_lines(txt,kind,size,minsz,s.x1-s.x0-2*s.pad)
        lt,lb=line_box(kind,sz); lh=lb-lt; s.it.append(('t',lines,kind,sz,col,alpha,sc,lh,name)); return s
    def custom(s,h,fn): s.it.append(('c',h,fn)); return s
    def height(s):
        h=0
        for i in s.it: h+=(len(i[1])*i[7]+(len(i[1])-1)*4) if i[0]=='t' else i[1]
        return h+s.gap*(len(s.it)-1)+2*s.pad
    def draw(s,b,top,col=None,alpha=1.0,name='card',r=26):
        col=col or CR; box=(s.x0,top,s.x1,top+s.height())
        if alpha>0.003: card(b,box,alpha=alpha,col=col,r=r)
        reg_top(name,box); y=top+s.pad; cx=(s.x0+s.x1)/2
        for i in s.it:
            if i[0]=='t':
                _,lines,kind,sz,c,a,sc,lh,nm=i
                for ln in lines:
                    if sc<0.999:   # pop-in scale: smaller glyphs centred in same line box
                        ss=sz*sc; lt2,lb2=line_box(kind,sz); lt3,lb3=line_box(kind,ss)
                        draw_line(b,ln,kind,ss,cx,y+(lh-(lb3-lt3))/2,c,a*alpha,name=nm,cont=box)
                    else: draw_line(b,ln,kind,sz,cx,y,c,a*alpha,name=nm,cont=box)
                    y+=lh+4
                y-=4
            else:
                i[2](b,s.x0+s.pad,y,s.x1-s.pad,y+i[1],box,alpha); y+=i[1]
            y+=s.gap
        return box
def pill(b,s,cx,cy,size,col,fc,alpha=1.0,minsz=MINB,maxw=X1-X0,name='pill',r=None,top=True,padx=28,pady=24):
    sz,lines=fit_lines(s,'man',size,minsz,maxw-2*padx); assert len(lines)==1, s
    l,t,rr,bb=ink_of(s,'man',sz); w=rr-l; hh=bb-t
    # vertical: cap height based box
    lt,lb=line_box('man',sz); ch=lb-lt
    box=(cx-w/2-padx,cy-ch/2-pady,cx+w/2+padx,cy+ch/2+pady)
    if alpha>0.003: card(b,box,alpha=alpha,col=col,r=r or 18)
    if top: reg_top(name,box)
    base=cy-ch/2-lt; f=font('man',sz); x=cx-(l+rr)/2
    if alpha>0.003:
        lay=Image.new('RGBA',(int(w)+8,int(hh)+8),(0,0,0,0)); ImageDraw.Draw(lay).text((4-l,4-t),s,font=f,fill=fc+(255,),anchor='ls')
        comp(b,lay,(int(round(x+l-4)),int(round(base+t-4))),alpha)
    reg_text(name+':'+s,(x+l,base+t,x+rr,base+bb),box,24); return box
def stamp_fit(b,s,cx,cy,t,t0,col,rot,maxw,maxh=None,name='stamp',parent=None):
    size=90
    while True:
        tw=tw_of(s,'man',size); w0=tw+120; h0=size*1.35; a=math.radians(abs(rot))
        rw=w0*math.cos(a)+h0*math.sin(a); rh=w0*math.sin(a)+h0*math.cos(a)
        if rw<=maxw and (maxh is None or rh<=maxh): break
        size-=2
    box=(cx-rw/2,cy-rh/2,cx+rw/2,cy+rh/2)
    if parent: reg_text(name,box,parent,PAD)
    else: reg_top(name,box)
    if t>=t0: stamp(b,s,cx,cy,t,t0,col=col,size=size,rot=rot)
    return box
def inside(a,c,p): return a[0]>=c[0]+p-0.5 and a[1]>=c[1]+p-0.5 and a[2]<=c[2]-p+0.5 and a[3]<=c[3]-p+0.5
def ovl(a,b): return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]
def check(f):
    bad=[]
    for n,ink,c,p in REG:
        if not inside(ink,c,p): bad.append(f'TEXT {n!r} ink={tuple(int(v) for v in ink)} cont={tuple(int(v) for v in c)} pad={p}')
        if not inside(ink,SAFE,0): bad.append(f'TEXT {n!r} outside safe zone')
    for i,(n,bx) in enumerate(TOP):
        if not inside(bx,SAFE,0): bad.append(f'BOX {n} {tuple(int(v) for v in bx)} outside safe zone')
        for m,by in TOP[i+1:]:
            if ovl(bx,by): bad.append(f'OVERLAP {n} {tuple(int(v) for v in bx)} x {m} {tuple(int(v) for v in by)}')
    if bad: raise SystemExit(f'TEXT-FIT FAIL frame {f} (t={f/FPS:.2f}):\n  '+'\n  '.join(bad))
# ================= captions / HUD / meter =================
CAPY=1158
def caption(b,t):
    cur=None
    for a,s,key in CAP:
        if t>=a: cur=(a,s,key)
    if not cur or not cur[1]: return
    a,s,key=cur; p=eob(P(t,a,0.22),1.4)
    pill(b,s,CX,CAPY,54,OL if key else CR,WH if key else INK,alpha=clamp(p*1.4),name='caption')
def hud(b,t):
    n=0
    for a,k in CLAIM:
        if t>=a: n=k
    chip=pill(b,f'ФАКТ {n}/6' if n else 'ФАКТ —/6',0,0,26,OL,WH,alpha=0,minsz=26,name='_m',top=False); REG.pop()
    w=chip[2]-chip[0]; h=chip[3]-chip[1]
    pill(b,f'ФАКТ {n}/6' if n else 'ФАКТ —/6',X1-w/2,270+h/2,26,OL,WH,minsz=26,name='chip',r=int(h/2))
    lt,lb=line_box('man',28); draw_line(b,'ЧЕСНОК · ПРОВЕРКА ФАКТОВ','man',28,0,270+h/2-(lb-lt)/2,WH,left=X0,name='hud',cont=SAFE,pad=0)
    reg_top('hudtitle',REG[-1][1])
    src=None
    for a,s in SRC:
        if t>=a: src=s
    if src:
        sz,_=fit_lines(src,'manr',24,20,X1-X0); lt,lb=line_box('manr',sz)
        ink=draw_line(b,src,'manr',sz,0,1249-(lb-lt),WH,0.92,left=X0,name='src',cont=SAFE,pad=0); reg_top('source',ink)
def clove(b,cx,cy,col,a):
    pts=[]
    for k in range(24):
        ang=2*math.pi*k/24; r=22*(1+0.25*max(0,-math.sin(ang)))
        pts.append((cx+0.72*r*math.cos(ang),cy+r*math.sin(ang)*(1 if math.sin(ang)>0 else 1.15)))
    poly_layer(b,pts,col,alpha=a)
def meter(b,t,t0,lvl,label,top,note=None):
    a=clamp(P(t,t0,0.3)); lc=(OLL if lvl>=3 else GO if lvl==2 else (240,110,100))
    lx=X0+32+4*58+10; lw=X1-32-lx
    sz,lines=fit_lines(label,'man',42,36,lw); lt,lb=line_box('man',sz); lh=lb-lt
    rowh=max(64,len(lines)*lh+(len(lines)-1)*4)
    st=Stack(pad=30)
    def row(bb,x0,y0,x1,y1,box,al):
        for i in range(4):
            on=i<lvl and t>t0+0.35+i*0.12
            clove(bb,x0+26+i*58,(y0+y1)/2+4,(lc if lvl else RD) if on else (90,84,76),a*al)
        yy=(y0+y1)/2-(len(lines)*lh+(len(lines)-1)*4)/2
        for ln in lines: draw_line(bb,ln,'man',sz,0,yy,lc,a*al,left=lx,name='meter:'+ln,cont=box); yy+=lh+4
    st.custom(rowh,row)
    if note: st.text(note,'manr',42,CR,alpha=1.0)
    return st.draw(b,top,col=INK,alpha=a,name='meter',r=20)
def big_item(st,s,size,col,t,t0,kind='disp'):
    sc=0.8+0.2*eob(P(t,t0,0.3),1.6); return st.text(s,kind,size,col,minsz=60,alpha=clamp(P(t,t0,0.15)),sc=sc)
TOPY=360
def gap_meter(box): return box[3]+16
# ================= scenes =================
def intro(b,t,t0):
    st=Stack().text('6 УТВЕРЖДЕНИЙ','disp',80,INK,minsz=60).text('1 ШКАЛА ДОКАЗАТЕЛЬСТВ','man',46,OL).text('мета-анализы · испытания · наблюдения','manr',42,INK,alpha=0.8)
    st.draw(b,TOPY+40+slide(t,t0),alpha=P(t,t0,0.2))
def chem(b,t,t0):
    st=Stack().text('АЛЛИИН','disp',80,INK,minsz=60).text('+ фермент аллииназа','manr',44,OL,alpha=P(t,t0+0.3,0.2)).text('↓','man',56,PL,alpha=P(t,8.0,0.2))
    big_item(st,'АЛЛИЦИН',96,PL,t,8.62); st.draw(b,TOPY+40,alpha=P(t,t0,0.2))
def heat(b,t,t0):
    stamp_fit(b,'ФЕРМЕНТ ВЫКЛ',CX,620,t,10.2,RD,-6,X1-X0,name='heatstamp')
def timer(b,t,t0):
    R=180; p=eio(P(t,12.07,1.6)); m=10*(1-p)
    def ring(bb,x0,y0,x1,y1,box,al):
        cx,cy=(x0+x1)/2,(y0+y1)/2
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); dd=ImageDraw.Draw(lay)
        dd.arc((cx-R,cy-R,cx+R,cy+R),0,360,fill=(220,210,192,255),width=24)
        dd.arc((cx-R,cy-R,cx+R,cy+R),-90,-90+360*(1-p) if p<1 else -89.9,fill=OL+(255,),width=24); comp(bb,lay,(0,0),al)
        ri=R-24; hs=ri/math.sqrt(2); sq=(cx-hs,cy-hs,cx+hs,cy+hs)
        s=f'{int(math.ceil(m-1e-6)):02d}:00' if p<1 else '00:00'
        sz,_=fit_lines('00:00','disp',110,40,2*hs-2*PAD); lt,lb=line_box('disp',sz)
        l,tt,r,bt=ink_of('00:00','disp',sz)
        draw_line(bb,s,'disp',sz,cx,cy-(bt+tt)/2+lt,INK,al,name='timer digits',cont=sq)
    st=Stack().custom(2*R+8,ring).text('МИНУТ ПОСЛЕ ИЗМЕЛЬЧЕНИЯ','man',42,OL).text('→ НА СКОВОРОДУ','man',46,PL,alpha=P(t,12.93,0.2))
    st.draw(b,TOPY+10,alpha=P(t,t0,0.2))
def numcard(b,t,t0,head,num,numt0,sub):
    st=Stack().text(head,'man',42,OL); big_item(st,num,140,PL,t,numt0); st.text(sub,'manr',42,INK)
    return st.draw(b,TOPY+slide(t,t0),alpha=P(t,t0,0.2))
def bp(b,t,t0):
    v=8.6*eo(P(t,16.6,1.2)); bx=numcard(b,t,t0,'ВЕРХНЕЕ ДАВЛЕНИЕ',f'−{v:.1f}'.replace('.',','),16.23,'мм рт. ст. · у гипертоников')
    meter(b,t,15.3,3,'УМЕРЕННО',gap_meter(bx),note='при нормальном давлении — без эффекта')
def chol(b,t,t0):
    v=10*eo(P(t,20.0,1.0)); bx=numcard(b,t,t0,'«ПЛОХОЙ» ХОЛЕСТЕРИН',f'≈ −{int(round(v))}%',20.0,'курс добавок от 2 месяцев')
    meter(b,t,20.6,2,'СЛАБО–\nУМЕРЕННО',gap_meter(bx),note='мета-анализы расходятся')
def cold(b,t,t0):
    st=Stack(); big_item(st,'1',180,PL,t,23.95); st.text('испытание · 146 человек','man',42,INK,alpha=P(t,24.2,0.2))
    bx=st.draw(b,TOPY+slide(t,t0),alpha=P(t,t0,0.2))
    meter(b,t,24.8,1,'МАЛО ДАННЫХ',gap_meter(bx),note='Cochrane: «доказательств недостаточно»')
def cancer(b,t,t0):
    d=ImageDraw.Draw(b); d.rectangle((0,0,W,H),fill=PL+(150,))
    sc=0.8+0.2*eob(P(t,t0,0.3),1.6)
    draw_line(b,'ТЕПЕРЬ','disp',90*sc,CX,470,CR,clamp(P(t,t0,0.15)),name='теперь',cont=SAFE,pad=0)
    sz,_=fit_lines('РАК','disp',220,100,X1-X0); sc2=0.8+0.2*eob(P(t,t0+0.2,0.3),1.6)
    draw_line(b,'РАК','disp',sz*sc2,CX,600,WH,clamp(P(t,t0+0.2,0.15)),name='рак',cont=SAFE,pad=0)
def bars(t,t0):
    def fn(bb,x0,y0,x1,y1,box,al):
        lw=max(font('man',42).getlength(s) for s in ('МАЛО','МНОГО'))+20
        for j,(lab,v,col) in enumerate([('МАЛО',1.0,(150,140,128)),('МНОГО',0.54,PL)]):
            yy=y0+j*80; w=int((x1-x0-lw)*v*eo(P(t,t0+0.3+j*0.3+(1.3 if j else 0),0.6)))
            lt,lb=line_box('man',42); draw_line(bb,lab,'man',42,0,yy+(64-(lb-lt))/2,INK,al,left=x0,name='bar:'+lab,cont=box)
            if al>0.003: rrect(bb,(x0+lw,yy+6,x0+lw+max(w,4),yy+58),10,fill=col+(int(255*al),))
    return fn
def obs(b,t,t0):
    st=Stack().text('РАК ЖЕЛУДКА','man',46,OL).text('лук и чеснок: мало vs много','manr',42,INK).custom(144,bars(t,t0)).text('ОШ 0,54 · почти вдвое реже','man',42,PL,alpha=P(t,31.6,0.2))
    st.draw(b,TOPY+slide(t,t0),alpha=P(t,t0,0.2))
def obs2(b,t,t0):
    def slot(bb,x0,y0,x1,y1,box,al): stamp_fit(bb,'НАБЛЮДЕНИЯ',(x0+x1)/2,(y0+y1)/2,t,33.5,RD,-5,x1-x0+48-2*PAD,maxh=y1-y0+0,name='obsstamp',parent=box)
    st=Stack().text('РАК ЖЕЛУДКА','man',46,OL).text('ОШ 0,54 · почти вдвое реже','man',42,PL).custom(150,slot)
    bx=st.draw(b,TOPY)
    meter(b,t,34.5,2,'СЛАБО–\nУМЕРЕННО',gap_meter(bx),note='связь ≠ причина')
def timeline(t,stage2):
    def fn(bb,x0,y0,x1,y1,box,al):
        xa,xc=x0+10,x1-10; xb=xa+(xc-xa)*7.3/22.3; ly=y0+70
        lt,lb=line_box('man',42)
        draw_line(bb,'7,3 года','man',42,max(x0+font('man',42).getlength('7,3 года')/2,(xa+xb)/2),y0,OL,al*P(t,37.6,0.2),name='7,3',cont=box)
        p=eo(P(t,36.4,1.2)); rrect(bb,(xa,ly-12,xa+(xb-xa)*p,ly+12),12,fill=OL+(int(255*al),))
        if stage2:
            q=eo(P(t,40.34,1.0)); rrect(bb,(xb,ly-5,xb+(xc-xb)*q,ly+5),5,fill=(150,140,128,int(255*al)))
            draw_line(bb,'2017','manr',42,0,ly+22,INK,al,left=x1-font('manr',42).getlength('2017')-2,name='2017',cont=box)
        draw_line(bb,'1995','manr',42,0,ly+22,INK,al,left=x0,name='1995',cont=box)
    return fn
def rct(b,t,t0,stage2=False):
    st=Stack()
    if not stage2: st.text('РКИ В ШАНЬДУНЕ, КИТАЙ','man',42,OL)
    st.custom(150,timeline(t,stage2))
    if not stage2:
        big_item(st,'3365',130,INK,t,36.38); st.text('человек · чеснок или плацебо','manr',42,INK,alpha=P(t,38.2,0.2))
        st.draw(b,TOPY,alpha=P(t,t0,0.2))
    else:
        big_item(st,'−34%',120,PL,t,42.94); st.text('смертность от рака желудка · 1 РКИ','man',42,INK)
        st.text('заболеваемость: значимой разницы нет','manr',42,INK,alpha=0.85)
        bx=st.draw(b,TOPY); meter(b,t,43.3,2,'УМЕРЕННО',gap_meter(bx))
def oilboxes(t):
    def fn(bb,x0,y0,x1,y1,box,al):
        bw=(x1-x0-24)/2; sz=min(fit_lines(s,'man',42,30,bw-2*PAD)[0] for s in ('ОЛИВКОВОЕ','ЛЬНЯНОЕ'))
        for j,lab in enumerate(['ОЛИВКОВОЕ','ЛЬНЯНОЕ']):
            bx0=x0+j*(bw+24); sb=(bx0,y0,bx0+bw,y0+96)
            if al>0.003: rrect(bb,sb,14,outline=INK,width=4,alpha=al)
            lt,lb=line_box('man',sz); draw_line(bb,lab,'man',sz,bx0+bw/2,y0+48-(lb-lt)/2,INK,al,name='oil:'+lab,cont=sb)
            lt,lb=line_box('disp',80); draw_line(bb,'0','disp',80,bx0+bw/2,y0+108,PL,al*P(t,50.0,0.2),name='zero',cont=box)
    return fn
def oil(b,t,t0,stage2=False):
    if not stage2:
        st=Stack(); big_item(st,'А МАСЛО?',90,INK,t,t0)
        st.text('аллицин → сульфиды, аджоен','man',42,OL,alpha=P(t,45.3,0.2)).text('ЖИРОРАСТВОРИМЫ','man',54,PL,alpha=P(t,46.3,0.2))
        st.draw(b,TOPY+40,alpha=P(t,t0,0.2))
    else:
        lt,lb=line_box('disp',80)
        st=Stack().text('ИСПЫТАНИЙ НА ЛЮДЯХ','man',42,OL).custom(108+(lb-lt)+4,oilboxes(t)).text('средиземноморская диета полезна — но целиком','manr',42,INK)
        bx=st.draw(b,TOPY); meter(b,t,50.2,0,'НЕТ ДАННЫХ',gap_meter(bx))
def warn(b,t,t0):
    d=ImageDraw.Draw(b); d.rectangle((0,0,W,H),fill=(20,12,10,120))
    st=Stack(gap=6).text('ЧЕСНОК','man',50,WH).text('НЕ ЗАМЕНЯЕТ','disp',84,WH,minsz=56).text('ЛЕЧЕНИЕ','disp',84,WH,minsz=56).text('при болезни — к врачу','man',42,WH,alpha=P(t,52.5,0.2))
    st.draw(b,TOPY,col=RD,alpha=P(t,t0,0.2),name='warncard')
def loopc(b,t,t0,yc=640):
    for j,(lab,col) in enumerate([('ПРАВДА',OL),('МИФ',PL)]):
        x=CX-155+j*310; p=eob(P(t,t0+0.8+j*0.25,0.3),1.5)
        box=(x-145,yc-60,x+145,yc+60); reg_top('btn'+lab,box)
        sz,_=fit_lines('ПРАВДА','man',48,36,290-2*PAD); lt,lb=ink_of('НД','man',sz)[1],ink_of('НД','man',sz)[3]
        if p>0:
            card(b,box,alpha=clamp(p),col=col,r=60)
        draw_line(b,lab,'man',sz,x,yc-(lb-lt)/2-(lt-line_box('man',sz)[0]),WH,clamp(p) if p>0 else 0,name='btn:'+lab,cont=box)
def avbadge(b,t,seg,t0,t1):
    a=clamp(min((t-t0)/0.15,(t1-t)/0.15)); sz=250
    im=avf(seg,t).crop((200,300,1000,1100)).resize((sz,sz),Image.LANCZOS).convert('RGBA')
    m=Image.new('L',(sz,sz),0); ImageDraw.Draw(m).ellipse((0,0,sz-1,sz-1),fill=255); im.putalpha(m)
    s=0.8+0.2*eob(P(t,t0,0.25),1.4)
    if s!=1: im=im.resize((int(sz*s),int(sz*s)),Image.BICUBIC)
    cx,cy=CX,905; r=im.width//2
    lay=Image.new('RGBA',(im.width+24,im.height+24),(0,0,0,0)); ImageDraw.Draw(lay).ellipse((0,0,im.width+23,im.height+23),fill=CR+(255,))
    comp(b,lay,(cx-r-12,cy-r-12),a); comp(b,im,(cx-r,cy-r),a)
    reg_top('badge',(cx-sz//2-12,cy-sz//2-12,cx+sz//2+12,cy+sz//2+12+60))
    pill(b,'ВЕДУЩИЙ',cx,cy+sz//2+30,28,OL,WH,alpha=a,minsz=28,name='badgelabel',top=False)
def trans(im,t):
    for t0,ty in TR.items():
        dt=t-t0
        if -0.001<=dt<0.18:
            k=1-dt/0.18
            if ty=='flash': im=Image.blend(im,Image.new('RGBA',(W,H),CR+(255,)),0.6*k)
            elif ty=='wipe':
                a=np.asarray(im.convert('RGB')).copy(); x=int((1-k)*W); a[:,x:min(W,x+60)]=np.array(OL); a[:,min(W,x+60):]=np.array(CR); im=Image.fromarray(a).convert('RGBA')
            elif ty=='punch':
                z=1+0.07*k; c=im.resize((int(W*z),int(H*z)),Image.BICUBIC); im=c.crop(((c.width-W)//2,(c.height-H)//2,(c.width-W)//2+W,(c.height-H)//2+H))
    return im
def grain(t):
    rs=np.random.RandomState(int(t*25)%17); z=np.zeros((H//2,W//2,4),np.uint8); n=rs.randint(0,255,(H//2,W//2)).astype(np.uint8); z[...,0]=n;z[...,1]=n;z[...,2]=n;z[...,3]=10
    return Image.fromarray(z).resize((W,H))
GR=[grain(i/25) for i in range(6)]
def vign():
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); r=np.sqrt(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.72))**2)
    a=np.clip((r-0.45)*1.3,0,1)*170; z=np.zeros((H,W,4),np.uint8); z[...,:3]=(30,18,10); z[...,3]=a.astype(np.uint8); return Image.fromarray(z)
VG=None
def cover():
    b=vframe('10071217',40); b=kb(b,0,0,1,1.1,1.1).convert('RGBA'); comp(b,vign(),(0,0))
    st=Stack(pad=40).text('ЧЕСНОК','disp',150,INK,minsz=80).text('ПРОТИВ РАКА','disp',110,PL,minsz=60)
    def pl(bb,x0,y0,x1,y1,box,al): pill(bb,'ПРАВДА ИЛИ МИФ?',(x0+x1)/2,(y0+y1)/2,44,OL,WH,name='coverpill',top=False,maxw=x1-x0)
    st.custom(100,pl); st.draw(b,440,name='covercard')
    return b
def frame(f):
    global VG
    REG.clear(); TOP.clear()
    t=f/FPS
    if f<2:
        b=cover().convert('RGB'); check(f); return b
    if VG is None: VG=vign()
    k=cur_shot(t); b=shot_img(t,k).convert('RGBA'); kind=S[k][1]; t0=S[k][0]
    comp(b,VG,(0,0)); comp(b,GR[f%6],(0,0))
    if kind=='intro': intro(b,t,t0)
    elif kind=='chem': chem(b,t,t0)
    elif kind=='timer': timer(b,t,t0)
    elif kind=='bp': bp(b,t,t0)
    elif kind=='chol': chol(b,t,t0)
    elif kind=='cold': cold(b,t,t0)
    elif kind=='cancer': cancer(b,t,t0)
    elif kind=='obs': obs(b,t,t0)
    elif kind=='obs2': obs2(b,t,t0)
    elif kind=='rct': rct(b,t,t0)
    elif kind=='rct2': rct(b,t,35.72,True)
    elif kind=='oil': oil(b,t,t0)
    elif kind=='oil2': oil(b,t,44.39,True)
    elif kind=='warn': warn(b,t,t0)
    elif kind=='loop': loopc(b,t,t0)
    if 9.61<=t<11.65: heat(b,t,9.61)
    if kind=='av' and t<3.05: loopc(b,t,-0.6,1010)
    if kind!='av' or t>1.0: hud(b,t)
    caption(b,t)
    if SEG['B'][0]<=t<SEG['B'][1]: avbadge(b,t,'B',SEG['B'][0],SEG['B'][1])
    check(f)
    b=trans(b,t)
    return b.convert('RGB')
if __name__=='__main__':
    a,bb=int(sys.argv[1]),int(sys.argv[2]); out=sys.argv[3]
    if out=='check':
        for f in range(a,min(bb,NF)): frame(f)
        print('ok',a,bb,'warn',sorted(set(WARN))); sys.exit()
    if out.endswith('.jpg') or out.endswith('.png'): frame(a).save(out); sys.exit()
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','25','-i','-','-c:v','ffv1','-level','3','-pix_fmt','yuv444p',out],stdin=subprocess.PIPE)
    try:
        for f in range(a,min(bb,NF)): p.stdin.write(frame(f).tobytes())
    finally:
        p.stdin.close(); p.wait()
    if WARN: print('warn',sorted(set(WARN)))
