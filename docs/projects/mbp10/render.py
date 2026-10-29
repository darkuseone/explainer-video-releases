import sys,os,math,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from lib import W,H,FPS,clamp,eo,eio,eob,comp,kb,line
from shots import S,TOT
from caps_manual import CAP
FD='/usr/share/fonts/truetype/sand-box/google/'
# ---- mbp10 look: "OLED night" : true black, cold white glow, electric violet, tiny mint ----
BLK=(2,2,4); WHT=(242,245,255); VIO=(124,92,255); MINT=(92,255,200); GREY=(120,124,134)
NF=int(round(TOT*FPS)); X0,X1=120,780; CX=450; SAFE=(120,270,780,1250)
_fc={}
def font(k,s):
    s=int(s); key=(k,s)
    if key in _fc: return _fc[key]
    if k=='unb': f=ImageFont.truetype(FD+'Unbounded/Unbounded-VariableFont_wght.ttf',s); f.set_variation_by_axes([800])
    elif k=='ons': f=ImageFont.truetype(FD+'Onest/'+[x for x in os.listdir(FD+'Onest') if x.endswith('.ttf')][0],s); f.set_variation_by_axes([750])
    else: f=ImageFont.truetype(FD+'JetBrains Mono/JetBrainsMono-VariableFont_wght.ttf',s); f.set_variation_by_axes([600])
    _fc[key]=f; return f
def P(t,a,d): return clamp((t-a)/d)
GEN=lambda src: src.startswith('g_')
NFR={}
def vframe(k,i):
    d='shots/%02d_%s/'%(k,S[k][1])
    if d not in NFR: NFR[d]=len(os.listdir(d))
    n=NFR[d]; i=i%(2*n-2); i=i if i<n else 2*n-2-i
    return Image.open(d+'f%04d.jpg'%(i+1)).convert('RGB')
def cur(t):
    k=0
    for j,s in enumerate(S):
        if t>=s[0]: k=j
    return k
def nxt(k): return S[k+1][0] if k+1<len(S) else TOT
def shot(t,k):
    t0,src,ss,z0,z1=S[k]; return kb(vframe(k,int((t-t0)*FPS)),t,t0,nxt(k)-t0,z0,z1)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
VIG=np.clip((np.sqrt(((xx-W/2)/(W*0.8))**2+((yy-H/2)/(H*0.72))**2)-0.48)*1.3,0,0.8)[...,None]
def grade(im,t):
    a=np.asarray(im.convert('RGB')).astype(np.float32)/255
    lum=a.mean(2,keepdims=True)
    a=np.clip((a-0.04)/0.96,0,1)**1.12          # OLED: crush to true black
    a=a*(0.9+0.1*np.array([0.95,0.97,1.08],np.float32))  # cool highlights
    a=a+np.array(VIO,np.float32)/255*0.06*lum*(1-lum)*4   # violet in the mids
    # twist: dim + desaturate 28.55-35.40, snap back on reveal
    dk=eio(P(t,28.55,0.8))*(1-P(t,35.40,0.05))
    if dk>0:
        g=a.mean(2,keepdims=True); a=a*(1-0.75*dk)+g*0.75*dk; a=a*(1-0.35*dk)
    a=a*(1-VIG)
    return Image.fromarray((a.clip(0,1)*255).astype(np.uint8)).convert('RGBA')
def grainf(i):
    rs=np.random.RandomState(i); n=rs.randint(0,255,(H//2,W//2)).astype(np.uint8); z=np.zeros((H//2,W//2,4),np.uint8); z[...,0]=n;z[...,1]=n;z[...,2]=n;z[...,3]=10
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
def text(b,s,k,size,cx,cy,col,alpha=1.0,maxw=X1-X0,glow=None,name=None,cont=None,pad=0,minsz=24,left=None,outline=False):
    size=int(size)
    while size>minsz and font(k,size).getlength(s)>maxw: size-=2
    if font(k,size).getlength(s)>maxw: WARN.append(f'{s} too wide')
    f=font(k,size); anc='mm' if left is None else 'lm'; l,tp,r,bt=f.getbbox(s,anchor=anc)
    x=cx if left is None else left; ink=(x+l,cy+tp,x+r,cy+bt)
    if alpha>0.003:
        g=30 if glow else 6
        lay=Image.new('RGBA',(int(r-l)+2*g+8,int(bt-tp)+2*g+8),(0,0,0,0)); ox,oy=g+4-l,g+4-tp
        if glow:
            gl=Image.new('RGBA',lay.size,(0,0,0,0)); ImageDraw.Draw(gl).text((ox,oy),s,font=f,fill=glow+(255,),anchor=anc,stroke_width=4)
            lay=Image.alpha_composite(lay,gl.filter(ImageFilter.GaussianBlur(18)))
        d=ImageDraw.Draw(lay)
        if outline: d.text((ox,oy),s,font=f,fill=(0,0,0,0),anchor=anc,stroke_width=3,stroke_fill=col+(255,))
        else: d.text((ox,oy),s,font=f,fill=col+(255,),anchor=anc)
        comp(b,lay,(x-ox,cy-oy),alpha)
    REG.append((name or s,ink,cont or SAFE,pad)); return ink,size
def panel(b,box,alpha,fill=BLK,fa=0.8,edge=None,r=14,ew=2):
    if alpha<=0.003: return
    x0,y0,x1,y1=[int(round(v)) for v in box]; lay=Image.new('RGBA',(x1-x0,y1-y0),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((0,0,x1-x0-1,y1-y0-1),r,fill=fill+(int(255*fa),),outline=(edge+(220,)) if edge else None,width=ew)
    comp(b,lay,(x0,y0),alpha)
# ---------- HUD ----------
CHAP=[(0,'01 · КРЫШКА'),(5.45,'02 · ЭКРАН'),(16.25,'03 · OLED'),(24.70,'04 · СЛОИ'),(28.55,'05 · ПОВОРОТ'),(42.30,'06 · ЦЕНА'),(47.90,'07 · ЗАГАДКА'),(52.50,'01 · КРЫШКА')]
def hud(b,t,k):
    ch=[s for a,s in CHAP if t>=a][-1]
    ink,_=text(b,'MACBOOK PRO · 2026','mono',24,0,300,WHT,0.8,left=X0,name='hudl'); TOP.append(('hudl',ink))
    f=font('mono',22); w=f.getlength(ch)+32; box=(X1-w,281,X1,319)
    panel(b,box,1,fa=0.65,edge=VIO,r=19); text(b,ch,'mono',22,(box[0]+box[2])/2,300,WHT,name='chip',cont=box,pad=5); TOP.append(('chip',box))
    if GEN(S[k][1]):
        s='КОНЦЕПТ · ИИ-КАДР'; f=font('mono',20); w=f.getlength(s)+28; box=(X0,336,X0+w,368)
        panel(b,box,0.9,fa=0.55,edge=GREY,r=16); text(b,s,'mono',20,(box[0]+box[2])/2,352,(200,204,214),0.9,name='gen',cont=box,pad=4); TOP.append(('gen',box))
    for (px,py,dx,dy) in [(X0-50,255,1,1),(X1+50,255,-1,1),(X0-50,1265,1,-1),(X1+50,1265,-1,-1)]:
        line(b,(px,py),(px+dx*30,py),WHT,2,0.45); line(b,(px,py),(px,py+dy*30),WHT,2,0.45)
    # progress "pixel row": 24 dots light up with time (motif)
    n=24; y=1238
    for i in range(n):
        x=X0+12+i*(X1-X0-24)/(n-1); on=i/(n-1)<=t/TOT
        c=WHT if on else (60,62,70); r=4 if on else 3
        lay=Image.new('RGBA',(14,14),(0,0,0,0)); ImageDraw.Draw(lay).ellipse((7-r,7-r,7+r,7+r),fill=c+(230,)); comp(b,lay,(x-7,y-7))
    TOP.append(('dots',(X0,1228,X1,1248)))
CAPY=1140
def caption(b,t):
    c=[x for x in CAP if t>=x[0]]
    if not c: return
    a0,s,key=c[-1]; p=eob(P(t,a0,0.22),1.2) if a0>0 else 1
    sz=50; f=font('ons',sz)
    while f.getlength(s)>X1-X0-70: sz-=2; f=font('ons',sz)
    l,tp,r,bt=f.getbbox(s,anchor='mm'); hw=(r-l)/2+30
    hh=44*(0.9+0.1*p); box=(CX-hw,CAPY-hh,CX+hw,CAPY+hh)
    panel(b,box,1,fill=BLK,fa=0.9,r=44)
    a=clamp(P(t,a0,0.12)*1.0) if a0>0 else 1
    if key and key in s:
        # draw word by word, key word in violet
        x=CX-(r-l)/2; parts=s.split(' ')
        for i,wd in enumerate(parts):
            ww=f.getlength(wd); col=VIO if key in wd else WHT
            text(b,wd,'ons',sz,x+ww/2,CAPY,col,a,name='cap',cont=box,pad=8,maxw=9999)
            x+=ww+f.getlength(' ')
    else: text(b,s,'ons',sz,CX,CAPY,WHT,a,name='cap',cont=box,pad=8)
    TOP.append(('caption',box))
def title(b,t,s,t0,cy,size,col=WHT,glow=VIO,name='title',outline=False,t1=None,instant=False):
    a=1 if instant else clamp(P(t,t0,0.12))
    if t1: a*=1-P(t,t1-0.2,0.2)
    sc=1 if instant else 0.86+0.14*eob(P(t,t0,0.3),1.4)
    ink,sz=text(b,s,'unb',size*sc,CX,cy,col,a,glow=glow,name=name,outline=outline,minsz=36)
    TOP.append((name,ink)); return ink
def counter(b,t,t0,d,v0,v1,fmt,cy,lab,t_end):
    a=clamp(P(t,t0-0.1,0.12))*(1-P(t,t_end-0.2,0.2))
    if a<=0: return
    p=eio(P(t,t0,d)); v=v0+(v1-v0)*p; iv=int(round(v)) if p<1 else v1
    frac=(v%1) if p<1 else 0
    s=fmt(iv); ink,_=text(b,s,'unb',150,CX,cy-frac*18,WHT,a,glow=VIO,name='count'); TOP.append(('count',(X0+20,cy-100,X1-20,cy+100)))
    line(b,(X0+60,cy-108),(X1-60,cy-108),VIO,3,a*0.8); line(b,(X0+60,cy+106),(X1-60,cy+106),VIO,3,a*0.8)
    ink2,_=text(b,lab,'mono',30,CX,cy+150,MINT,a,name='countlab'); TOP.append(('countlab',ink2))
def swatch(b,t):   # 14.4-16.2  "black" on LCD vs OLED
    a=clamp(P(t,14.56,0.2))*(1-P(t,16.05,0.2))
    if a<=0: return
    for i,(lab,c) in enumerate([('ЭКРАН С ЛАМПОЙ',(46,48,54)),('OLED',(0,0,0))]):
        x0=X0+40+i*300; y0=470; box=(x0,y0,x0+240,y0+240)
        p=eob(P(t,14.56+i*0.5,0.3),1.3)
        if p<=0: continue
        panel(b,box,a*clamp(p),fill=c,fa=1.0,edge=WHT if i==0 else VIO,r=18,ew=3)
        text(b,lab,'mono',22,(box[0]+box[2])/2,y0+275,WHT,a*clamp(p),name='sw%d'%i,maxw=280); TOP.append(('sw%d'%i,(x0-20,y0,x0+260,y0+295)))
def pixgrid(b,t):  # 19.0-21.3 dots switch off
    a=clamp(P(t,19.0,0.2))*(1-P(t,21.1,0.2))
    if a<=0: return
    cols,rows=7,5; sp=88; x0=CX-(cols-1)*sp/2; y0=470
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    rs=np.random.RandomState(3); order=rs.permutation(cols*rows)
    for j in range(cols*rows):
        x=x0+(j%cols)*sp; y=y0+(j//cols)*sp
        off=order[j]<int(cols*rows*0.6*eio(P(t,20.04,0.7)))
        c=[(255,70,90),(80,255,140),(90,120,255)][j%3]
        if off: d.ellipse((x-26,y-26,x+26,y+26),outline=(70,72,80,255),width=2)
        else: d.ellipse((x-26,y-26,x+26,y+26),fill=c+(255,))
    comp(b,lay.filter(ImageFilter.GaussianBlur(10)),(0,0),a*0.7); comp(b,lay,(0,0),a)
    TOP.append(('grid',(x0-30,y0-30,x0+(cols-1)*sp+30,y0+(rows-1)*sp+30)))
def slider(b,t):   # 38.5-42.1 brightness slider: logo brightness follows screen
    a=clamp(P(t,38.6,0.2))*(1-P(t,42.0,0.2))
    if a<=0: return
    v=0.25+0.7*eio(P(t,38.9,0.9)) - 0.95*eio(P(t,40.9,0.6)); v=max(0,min(1,v))
    for i,(lab,y) in enumerate([('ЭКРАН',520),('ЯБЛОКО',660)]):
        xa,xb=X0+60,X1-60
        panel(b,(xa-10,y-14,xb+10,y+14),a,fill=(30,32,40),fa=0.9,r=14)
        if v>0.01: panel(b,(xa-10,y-14,xa+(xb-xa)*v+10,y+14),a,fill=WHT if i==0 else VIO,fa=1.0,r=14)
        text(b,lab,'mono',24,0,y-46,WHT,a,left=xa-10,name='sl%d'%i)
        TOP.append(('sl%d'%i,(xa-12,y-62,xb+12,y+16)))
    s='ВЫКЛ' if v<0.02 else '%d%%'%round(v*100)
    ink,_=text(b,s,'unb',64,CX,800,MINT if v<0.02 else WHT,a,name='slv'); TOP.append(('slv',ink))
def scene(b,t):
    if t<3.20: title(b,t,'СНОВА',0,480,150,instant=True,name='h1'); title(b,t,'СВЕТИТСЯ?',0,640,110,col=WHT,glow=VIO,instant=True,name='h2')
    elif t<5.45: counter(b,t,4.0,0.75,2016,2026,str,560,'ЛОГОТИП НЕ СВЕТИЛСЯ',5.4)
    elif 9.12<=t<10.15: title(b,t,'OLED',9.40,560,190,name='oled')
    elif 13.05<=t<16.25: swatch(b,t)
    elif 16.86<=t<18.95: title(b,t,'СВЕТИТСЯ САМА',17.82,540,84,glow=VIO,name='sama')
    elif 18.95<=t<21.30: pixgrid(b,t)
    elif 25.28<=t<28.55:
        title(b,t,'2',25.62,520,260,col=WHT,glow=VIO,name='two'); 
        if t>=26.34: title(b,t,'СЛОЯ СВЕТА',26.34,720,70,glow=None,name='twol')
    elif 28.76<=t<29.75: title(b,t,'ПОВОРОТ',28.94,560,110,col=MINT,glow=None,name='pov')
    elif 29.75<=t<33.10:
        if t>=31.50: title(b,t,'ДО 2016',31.50,520,120,glow=None,outline=True,name='old')
    elif 33.10<=t<35.40:
        if t>=33.88: title(b,t,'ПОДСВЕТКИ',33.88,500,92,glow=None,name='nb1'); title(b,t,'НЕТ',34.66,640,170,col=MINT,glow=None,name='nb2')
    elif 35.40<=t<38.50:
        if t>=37.08: title(b,t,'СВОЙ СВЕТ',37.20,540,110,glow=VIO,name='own')
    elif 38.50<=t<42.30: slider(b,t)
    elif 42.30<=t<45.15: counter(b,t,43.32,0.8,0,2899,lambda v:'$'+f'{v:,}'.replace(',',' '),560,'НАЧАЛЬНАЯ ЦЕНА В США',45.1)
    elif 45.15<=t<47.90:
        if t>=46.5: title(b,t,'КОШЕЛЁК',46.5,500,100,glow=None,name='w1'); title(b,t,'ГАСНЕТ',46.9,640,110,col=MINT,glow=None,name='w2')
    elif 48.0<=t<51.20: title(b,t,'?',48.3,560,260,col=VIO,glow=VIO,name='q')
    elif t>=53.5: title(b,t,'СНОВА',53.84,480,150,name='e1'); title(b,t,'СВЕТИТСЯ?',54.48,640,110,glow=VIO,name='e2')
CUTS=[s[0] for s in S[1:]]
def trans(im,t):
    for t0 in CUTS:
        dt=t-t0
        if -0.001<=dt<0.16:
            k=1-dt/0.16
            if abs(t0-35.40)<0.01: im=Image.blend(im,Image.new('RGBA',(W,H),(235,235,255,255)),0.85*k); continue
            z=1+0.07*k; c=im.resize((int(W*z),int(H*z)),Image.BICUBIC); im=c.crop(((c.width-W)//2,(c.height-H)//2,(c.width-W)//2+W,(c.height-H)//2+H))
            a=np.asarray(im).copy(); a[...,0]=np.roll(a[...,0],int(10*k),axis=1); a[...,2]=np.roll(a[...,2],-int(10*k),axis=1); im=Image.fromarray(a)
    return im
def frame(f):
    REG.clear(); TOP.clear(); t=f/FPS
    k=cur(t); b=grade(shot(t,k),t); comp(b,GR[f%6],(0,0))
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
