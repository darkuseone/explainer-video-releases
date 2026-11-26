# l2m02 renderer: «Lineage 2 из нулевых — на айфоне». Pillow, 25 fps, 1080x1920.
# usage: python3 r.py png out.png t1,t2,...   |   python3 r.py <f0> <f1> out.mkv
import sys, os, json, math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from lib import *
ROOT=os.path.dirname(os.path.abspath(__file__)); P=lambda *a: os.path.join(ROOT,*a)
TL=json.load(open(P('timeline.json'))); PH=TL['phrases']; WD=TL['words']; TOT=TL['tot']
AVM=json.load(open(P('..','v','av_meta.json'))); AVN=len(os.listdir(P('av'))); LAG=0.02
SHN=json.load(open(P('shots','meta.json')))
COVER=3; NF=COVER+int(round(TOT*FPS))
GOLD=(228,179,90); YEL=(255,211,77); RED=(230,57,70); TEAL=(63,206,194); DEEP=(10,12,22); HI=(243,236,224)
def wt(word,k=0,end=False,ph=None):
    n=0
    for w in WD:
        if (ph is None or w[3]==ph) and w[2].lower().strip('.,!?…—:«»').startswith(word.lower()):
            if n==k: return w[1] if end else w[0]
            n+=1
    raise KeyError(word)
def pt(i,k=0): return PH[i][k]
# ---------------- footage ----------------
_fc={}
def shot(name,lt):
    n=SHN[name]; i=int(lt*FPS)
    i=i%(2*n-2) if n>1 else 0
    if i>=n: i=2*n-2-i          # ping-pong instead of freezing
    fn=P('shots',name,f'f{i+1:04d}.jpg')
    if fn in _fc: return _fc[fn]
    im=Image.open(fn).convert('RGBA')
    if len(_fc)>60: _fc.clear()
    _fc[fn]=im; return im
def kb(im,z,cx=0.5,cy=0.5,outw=W,outh=H):
    """subpixel Ken Burns: crop window of size out/z around (cx,cy) of im, resampled to out"""
    w,h=im.size; s=max(outw/w,outh/h)*z
    cw,ch=outw/s,outh/s; x0=cx*w-cw/2; y0=cy*h-ch/2
    x0=min(max(x0,0),w-cw); y0=min(max(y0,0),h-ch)
    return im.transform((outw,outh),Image.AFFINE,(1/s,0,x0,0,1/s,y0),resample=Image.BICUBIC)
def vfill(name,t,t0,z0=1.0,z1=1.07,cx=0.5,cy=0.5,dur=4.0):
    p=eio((t-t0)/dur); return kb(shot(name,t-t0),lerp(z0,z1,p),cx,cy)
_blur={}
def hwin(base,name,t,t0,y=860,z0=1.0,z1=1.06,border=GOLD,dim=0.62,w=1000,dur=4.0,ar=1.3):
    im=shot(name,t-t0)
    key=(name,int((t-t0)*FPS)//3)
    if key not in _blur:
        b=im.resize((im.width//8,im.height//8),Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
        b=kb(b,1.0); b=ImageEnhance.Color(ImageEnhance.Brightness(b).enhance(dim)).enhance(1.2)
        if len(_blur)>8: _blur.clear()
        _blur[key]=b
    base.alpha_composite(_blur[key])
    nat=w*im.height/im.width; h=int(min(max(nat,w/ar),840))
    fr=kb(im,lerp(z0,z1,eio((t-t0)/dur)),outw=w,outh=h)
    m=rrect_mask(w,h,26); card=Image.new('RGBA',(w,h),(0,0,0,0)); card.paste(fr,(0,0),m)
    g=Image.new('RGBA',(w+120,h+120),(0,0,0,0)); ImageDraw.Draw(g).rounded_rectangle((60,60,60+w,60+h),30,fill=(0,0,0,200))
    comp(base,g.filter(ImageFilter.GaussianBlur(22)),(540-w/2-60,y-h/2-50))
    ImageDraw.Draw(card).rounded_rectangle((1,1,w-2,h-2),26,outline=border+(255,),width=4)
    comp(base,card,(540-w/2,y-h/2))
    return (540-w/2,y-h/2,w,h)
def darken(base,a):
    if a>0: base.alpha_composite(Image.new('RGBA',(W,H),(6,7,14,int(255*a))))
# ---------------- avatar ----------------
_avc={}
def av_frame(t):
    for s in AVM:
        if s['t0']-0.6<=t<=s['t1']+0.6:
            i=int(math.floor((t-s['t0']+s['src0']+LAG)*FPS+1e-6))+1; i=max(1,min(AVN,i)); fn=P('av',f'f{i:04d}.jpg')
            if fn not in _avc:
                if len(_avc)>30: _avc.clear()
                _avc[fn]=Image.open(fn).convert('RGBA')
            return _avc[fn]
    return None
ACROP=(200,250,980,1030)
_mask={}
def circ_mask(d):
    if d not in _mask:
        m=Image.new('L',(d*3,d*3),0); ImageDraw.Draw(m).ellipse((0,0,d*3-1,d*3-1),fill=255); _mask[d]=m.resize((d,d),Image.LANCZOS)
    return _mask[d]
def avatar(base,t,cx,cy,D,alpha=1.0,ring=GOLD):
    fr=av_frame(t)
    if fr is None or D<8: return
    D=int(D); c=fr.crop(ACROP).resize((D,D),Image.BICUBIC)
    out=Image.new('RGBA',(D,D),(0,0,0,0)); out.paste(c,(0,0),circ_mask(D))
    pad=int(D*0.22); L=Image.new('RGBA',(D+2*pad,D+2*pad),(0,0,0,0)); d=ImageDraw.Draw(L)
    bw=max(4,int(14*D/640)); d.ellipse((pad-bw,pad-bw,pad+D+bw,pad+D+bw),outline=ring+(255,),width=bw*2)
    gl=L.filter(ImageFilter.GaussianBlur(max(6,int(20*D/640)))); L=Image.alpha_composite(gl,L); L=Image.alpha_composite(L,gl)
    d=ImageDraw.Draw(L)
    for (rk,sp,ln,wd,col) in ((1.12,60,110,6,YEL),(1.18,-45,70,4,HI)):
        r=D/2*rk; c0=pad+D/2; a0=(t*sp)%360
        d.arc((c0-r,c0-r,c0+r,c0+r),a0,a0+ln,fill=col+(230,),width=max(2,int(wd*D/640)+1))
    L.alpha_composite(out,(pad,pad))
    d.ellipse((pad,pad,pad+D-1,pad+D-1),outline=(255,240,214,255),width=max(2,int(3*D/640)))
    comp(base,L,(cx-L.width/2,cy-L.height/2),alpha)
# ---------------- text widgets ----------------
def fit_text(s,size,kind,maxw):
    while font(kind,size).getlength(s)>maxw and size>30: size-=2
    return size
def chip(base,s,cx,cy,col=GOLD,size=46,alpha=1.0,fill=(10,12,22,230),tc=None,scale=1.0):
    size=fit_text(s,size,'disp',620); f=font('disp',size); tw=f.getlength(s)
    asc,desc=f.getmetrics(); h=asc+desc+40; w=int(tw+64)
    L=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle((1,1,w-2,h-2),h//2,fill=fill,outline=col+(255,),width=4)
    d.text((w/2,h/2),s,font=f,fill=(tc or col)+(255,),anchor='mm')
    if scale!=1: L=L.resize((max(1,int(w*scale)),max(1,int(h*scale))),Image.BICUBIC)
    comp(base,L,(cx-L.width/2,cy-L.height/2),alpha)
def stamp(base,s,cx,cy,col=RED,size=92,alpha=1.0,rot=-7,scale=1.0):
    f=font('disp',size); tw=f.getlength(s); asc,desc=f.getmetrics(); w=int(tw+70); h=asc+desc+40
    L=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle((4,4,w-5,h-5),14,outline=col+(255,),width=10); d.rounded_rectangle((16,16,w-17,h-17),8,outline=col+(255,),width=3)
    d.text((w/2,h/2),s,font=f,fill=col+(255,),anchor='mm')
    a=np.array(L); rng=np.random.default_rng(7); msk=rng.random(a.shape[:2])<0.06; a[msk,3]=(a[msk,3]*0.25).astype(np.uint8); L=Image.fromarray(a)
    if scale!=1: L=L.resize((max(1,int(w*scale)),max(1,int(h*scale))),Image.BICUBIC)
    L=L.rotate(rot,resample=Image.BICUBIC,expand=True)
    comp(base,L,(cx-L.width/2,cy-L.height/2),alpha)
def bigtxt(base,s,cx,cy,size,col=YEL,alpha=1.0,scale=1.0,stroke=10):
    size=fit_text(s,size,'disp',880)
    txt(base,s,cx,cy,size,'disp',col,stroke=stroke,sfill=(6,6,12),alpha=alpha,scale=scale)
def card(base,title,sub,cx,cy,w,col,alpha=1.0,dim=0.0,tags=()):
    f1=font('disp',fit_text(title,64,'disp',w-80)); f2=font('dispb',40); f3=font('disp',34)
    h=210+(70 if tags else 0)
    L=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle((2,2,w-3,h-3),28,fill=(14,16,30,240),outline=col+(255,),width=5)
    d.text((40,62),title,font=f1,fill=HI+(255,),anchor='lm'); d.text((40,140),sub,font=f2,fill=col+(255,),anchor='lm')
    x=40
    for tg in tags:
        tw=f3.getlength(tg); d.rounded_rectangle((x,200,x+tw+40,252),26,fill=(40,30,50,255)); d.text((x+20,226),tg,font=f3,fill=(220,210,230,255),anchor='lm'); x+=tw+56
    if dim>0:
        g=L.convert('LA').convert('RGBA'); L=Image.blend(L,g,dim*0.8)
        ov=Image.new('RGBA',L.size,(0,0,0,int(110*dim))); L=Image.alpha_composite(L,Image.composite(ov,Image.new('RGBA',L.size,(0,0,0,0)),L.getchannel('A')))
    comp(base,L,(cx-w/2,cy-h/2),alpha)
def ringpulse(base,x,y,t,t0,col=YEL,label=None,ly=None):
    p=(t-t0)
    if p<0: return
    L=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    for k in range(2):
        q=((p*1.2+k*0.5)%1.0); r=40+70*q; a=int(230*(1-q)*min(1,p*4))
        d.ellipse((x-r,y-r,x+r,y+r),outline=col+(a,),width=6)
    d.ellipse((x-38,y-38,x+38,y+38),outline=col+(int(255*min(1,p*4)),),width=5)
    base.alpha_composite(L)
    if label: chip(base,label,x,ly if ly else y-110,col=col,size=38,alpha=min(1,p*4))
def flash(base,t,t0,dur=0.16,a=0.8):
    p=(t-t0)/dur
    if 0<=p<1: base.alpha_composite(Image.new('RGBA',(W,H),(255,246,226,int(255*a*(1-p)))))
def glitch(base,t,t0,n=3):
    f=int(round((t-t0)*FPS))
    if 0<=f<n:
        a=np.array(base); rng=np.random.default_rng(f+11)
        a[...,0]=np.roll(a[...,0],12,1); a[...,2]=np.roll(a[...,2],-12,1)
        for _ in range(6):
            y=rng.integers(0,H-60); h=rng.integers(10,60); a[y:y+h]=np.roll(a[y:y+h],int(rng.integers(-80,80)),1)
        base.paste(Image.fromarray(a))
# ---------------- captions ----------------
KEY={'lineage','айфоне','нулевых','утра','осады','сотни','драконов','другие','автобоем','интерлюд','гиран','пальцы','мир','компьютеров',
     '63','2,8','андроида','xs','нюанс','фанатский','ncsoft','бете','баги','27','ноября','2019','2m','класс','ник','живой','подпишись','древнее','2'}
def cap_chunks():
    ws=[]
    for w in WD:
        if w[2].startswith('-') and ws: ws[-1]=[ws[-1][0],w[1],ws[-1][2]+w[2],w[3]]; continue
        ws.append(list(w))
    out=[];cur=[]
    for k,w in enumerate(ws):
        cur.append(w); end=w[2][-1] in '.,?!…:' or k==len(ws)-1 or ws[k+1][3]!=w[3]
        if len(cur)>=3 or end or sum(len(x[2]) for x in cur)>15:
            out.append((cur[0][0],cur[-1][1],[x[2] for x in cur])); cur=[]
    res=[]
    for c in out:
        if res and len(c[2])==1 and len(res[-1][2])<=2 and res[-1][2][-1][-1] not in '.?!…' and c[0]-res[-1][1]<0.2 and sum(len(w) for w in res[-1][2]+c[2])<=17:
            p=res.pop(); res.append((p[0],c[1],p[2]+c[2]))
        else: res.append(c)
    return res
CAPS=cap_chunks()
def caption(base,t,y=1390):
    cur=None
    for k,(a,b,ws) in enumerate(CAPS):
        nxt=CAPS[k+1][0] if k+1<len(CAPS) else TOT
        if a-0.05<=t<min(nxt,b+0.5): cur=(a,ws)
    if not cur: return
    a,ws=cur; size=84
    words=[w.strip('«».,:—…?!') for w in ws]; words=[w for w in words if w]
    def lay(sz): return [text_layer(w.upper(),sz,'disp',YEL if w.lower() in KEY else WHITE,stroke=8,sfill=(6,6,12))[0] for w in words]
    ls=lay(size); sp=int(size*0.2); tw=sum(l.width for l in ls)-56*len(ls)+sp*(len(ls)-1)
    while tw>900 and size>56: size-=4; ls=lay(size); sp=int(size*0.2); tw=sum(l.width for l in ls)-56*len(ls)+sp*(len(ls)-1)
    u=eo((t-a)/0.15); x=540-tw/2-28
    for l in ls:
        s=0.88+0.12*u
        if u<1: l=l.resize((int(l.width*s),int(l.height*s)),Image.BICUBIC)
        comp(base,l,(x,y-l.height/2+14*(1-u)),u); x+=l.width-56*s+sp
def hud(base,t,s,alpha=1.0):
    f=font('mono',28); d=ImageDraw.Draw(base)
    L=Image.new('RGBA',(W,80),(0,0,0,0)); dd=ImageDraw.Draw(L)
    dd.text((130,40),s,font=f,fill=(230,220,200,int(200*alpha)),anchor='lm')
    if int(t*2)%2==0: dd.ellipse((96,32,112,48),fill=RED+(int(230*alpha),))
    base.alpha_composite(L,(0,250))
# ---------------- vignette / cover ----------------
VIG=vignette(None,0.55)
def cover():
    b=Image.new('RGBA',(W,H),DEEP+(255,)); b.alpha_composite(kb(shot('hook',1.2),1.12,0.5,0.45))
    darken(b,0.35); b.alpha_composite(VIG)
    g=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(g).rectangle((0,0,W,700),fill=(0,0,0,170)); b.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)))
    bigtxt(b,'LINEAGE 2',540,330,210,YEL,stroke=12)
    bigtxt(b,'НА АЙФОНЕ',540,520,150,HI,stroke=10)
    chip(b,'ТОТ САМЫЙ INTERLUDE 2006 ГОДА',540,1330,GOLD,size=50)
    return b
_cov=None
# ---------------- scenes ----------------
def frame(fi):
    global _cov
    if fi<COVER:
        if _cov is None: _cov=cover()
        return _cov
    t=(fi-COVER)/FPS; b=Image.new('RGBA',(W,H),DEEP+(255,))
    # P0 hook 0..5.16 — avatar over iPhone gameplay
    if t<pt(1,0)-0.1:
        ta=wt('айфоне')
        z=lerp(1.28,1.0,eo(t/0.45)) if t<ta else lerp(1.0,1.32,eo((t-ta)/0.35))
        b.alpha_composite(kb(shot('hook',t),z,0.5,0.4)); darken(b,0.18 if t<ta else 0.0)
        flash(b,t,0.0,0.2,0.9); flash(b,t,ta,0.16,0.7)
        s=eob(t/0.4,1.3); bigtxt(b,'LINEAGE 2',540,330,170,YEL,alpha=min(1,t/0.2),scale=0.85+0.15*s)
        if t>=wt('двухтысячных'): chip(b,'2003 · NCSOFT · КОРЕЯ',540,470,GOLD,size=44,alpha=min(1,(t-wt('двухтысячных'))/0.2))
        D=440*eob(min(1,t/0.35),1.2)*(1 if t<ta else lerp(1,0.0,eo((t-ta)/0.3)))
        avatar(b,t,540,1060,D)
        if t>=ta: stamp(b,'НА АЙФОНЕ',540,900,YEL,110,alpha=min(1,(t-ta)/0.12),scale=lerp(1.3,1.0,eo((t-ta)/0.2)))
    # P1 nostalgia 5.38..11.6 — PC footage windows
    elif t<pt(2,0)-0.1:
        t0=pt(1,0)-0.1; to=wt('осады'); tr=wt('рейды')
        if t<to: hwin(b,'pc_field' if t<wt('компьютерных') else 'pc_castle',t,t0 if t<wt('компьютерных') else wt('компьютерных'))
        elif t<tr: hwin(b,'pc_gate',t,to)
        else: hwin(b,'pc_raid',t,tr,border=RED)
        hud(b,t,'PC · 2003–2006 · '+('КОМПЬЮТЕРНЫЙ КЛУБ' if t<to else ('ОСАДА ЗАМКА' if t<tr else 'РЕЙД-БОСС')))
        if t>=wt('утра'):
            tt=wt('утра'); clock=f"0{min(6,int(2+(t-tt)*8))}:00" if t-tt<0.6 else '06:00'
            chip(b,'23:00 → '+clock,540,1180,GOLD,size=46,alpha=min(1,(t-tt)/0.15)*(1 if t<to+0.3 else max(0,1-(t-to-0.3)/0.2)))
        if t>=wt('сотни'): chip(b,'300+ ИГРОКОВ НА ОДНОЙ ОСАДЕ',540,1180,GOLD,size=42,alpha=min(1,(t-wt('сотни'))/0.15)*(1 if t<tr else max(0,1-(t-tr)/0.15)))
        flash(b,t,to,0.12,0.5); flash(b,t,tr,0.12,0.6)
    # P2 official mobile games 11.7..16.6 — cards
    elif t<pt(3,0)-0.1:
        t0=pt(2,0)-0.1
        b.alpha_composite(ImageEnhance.Brightness(kb(shot('pc_raid2',t-t0).resize((135,75)).filter(ImageFilter.GaussianBlur(3)),1.0)).enhance(0.35))
        hud(b,t,'ОФИЦИАЛЬНЫЕ МОБИЛЬНЫЕ ВЕРСИИ')
        td=wt('другие'); tg=wt('графикой')
        dim=eo((t-td)/0.3) if t>=td else 0
        for k,(ti,sb,tags,yy) in enumerate((('LINEAGE 2: REVOLUTION','2016 · NETMARBLE',('НОВАЯ ГРАФИКА','АВТОБОЙ'),560),('LINEAGE2M','2019 · NCSOFT',('UNREAL ENGINE 4','АВТОБОЙ'),900))):
            ts=t0+0.15+k*0.45; p=eo((t-ts)/0.35)
            if t>=ts: card(b,ti,sb,540+(1-p)*700*(1 if k==0 else -1),yy,860,TEAL if k==0 else (150,106,169),alpha=p,dim=dim,tags=tags if t>=tg-0.4 else ())
        if t>=td: stamp(b,'ДРУГИЕ ИГРЫ',540,1180,RED,96,alpha=min(1,(t-td)/0.12),scale=lerp(1.35,1.0,eo((t-td)/0.18)))
    # P3 same Interlude 16.6..22.2
    elif t<pt(4,0)-0.1:
        t0=pt(3,0)-0.1; tg=wt('гиран'); ts=wt('скиллы'); ti=wt('интерфейс'); tp=wt('только')
        if t<tg:
            b.alpha_composite(vfill('mon_phone',t,t0,1.0,1.08,0.5,0.4)); flash(b,t,t0,0.14,0.6)
            if t>=wt('интерлюд'): chip(b,'INTERLUDE · 2006',540,470,GOLD,size=50,alpha=min(1,(t-wt('интерлюд'))/0.15))
        elif t<ts:
            r=hwin(b,'giran',t,tg,y=820,ar=9); chip(b,'ЗАПИСЬ С ЭКРАНА ТЕЛЕФОНА',540,r[1]-60,GOLD,size=40)
        elif t<ti: b.alpha_composite(vfill('inv',t,ts,1.05,1.15,0.5,0.4))
        elif t<tp: b.alpha_composite(vfill('fight',t,ti,1.0,1.08,0.5,0.4))
        else:
            x,y,w,h=hwin(b,'giran2',t,tp,y=820,z0=1.0,z1=1.0,ar=9)
            ringpulse(b,x+0.135*w,y+0.56*h,t,tp,YEL,'ДЖОЙСТИК',y-60)
            ringpulse(b,x+0.865*w,y+0.79*h,t,tp+0.25,RED,'АТАКА',y+h+70)
        for tt in (tg,ts,ti,tp): flash(b,t,tt,0.1,0.35)
    # P4 same world 22.2..27.0
    elif t<pt(5,0)-0.1:
        t0=pt(4,0)-0.1; tc=wt('компьютеров')-0.5
        if t<tc:
            b.alpha_composite(vfill('same',t,t0,1.0,1.06,0.5,0.45))
            tm=wt('телефона')
            if t>=tm:
                p=eo((t-tm)/0.5); L=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
                y0,y1=760,1150; ye=lerp(y0,y1,p)
                d.line((540,y0,540,ye),fill=YEL+(255,),width=8)
                for k in range(3):
                    q=((t*1.5)+k/3)%1; yy=lerp(y0,y1,q)
                    if yy<=ye: d.ellipse((528,yy-12,552,yy+12),fill=HI+(255,))
                b.alpha_composite(L.filter(ImageFilter.GaussianBlur(3))); b.alpha_composite(L)
                chip(b,'ПК',540,y0-50,GOLD,size=44,alpha=p); chip(b,'ТЕЛЕФОН',540,y1+40,GOLD,size=44,alpha=p)
            if t>=wt('мир'): stamp(b,'ОДИН МИР',540,955,YEL,96,alpha=min(1,(t-wt('мир'))/0.12),scale=lerp(1.3,1,eo((t-wt('мир'))/0.2)))
        else:
            b.alpha_composite(vfill('laptop',t,tc,1.0,1.06,0.5,0.5)); chip(b,'ОДНОВРЕМЕННО: НОУТБУК + ТЕЛЕФОН',540,470,GOLD,size=40,alpha=min(1,(t-tc)/0.15))
    # P5 numbers
    elif t<pt(6,0)-0.1:
        t0=pt(5,0)-0.1; t63=wt('63'); tx=wt('хватит'); ti=wt('айфона')
        name,st=('andr',t0) if t<tx else (('crit',tx) if t<ti else ('load',ti))
        b.alpha_composite(vfill(name,t,st,1.0,1.06,0.5,0.45)); darken(b,0.55 if t>=t63 else 0.35)
        if t<t63:
            p=eo((t-t0)/0.4)
            for k,(lab,val,mx,col) in enumerate((('ПК-КЛИЕНТ',5.5,5.5,(150,106,169)),('МОБИЛКА',2.9,5.5,GOLD))):
                y=700+k*190; ww=int(760*val/mx*p)
                d=ImageDraw.Draw(b); d.rounded_rectangle((160,y,160+max(ww,20),y+90),20,fill=col+(255,))
                txt(b,lab,170,y-40,40,'disp',HI,stroke=5,anchor='lm'); txt(b,f'{val:.1f} ГБ'.replace('.',','),180+max(ww,20)+10,y+45,52,'disp',col,stroke=6,anchor='lm')
            chip(b,'СКОЛЬКО ВЕСИТ?',540,470,GOLD,size=50)
        else:
            items=[(t63,'63 МБ','APK-ФАЙЛ + 2,8 ГБ ДАННЫХ'),(tx,'2 ГБ ОЗУ','ANDROID 7.0+'),(ti,'iPHONE XS+','iOS 15 И НОВЕЕ')]
            cur=[it for it in items if t>=it[0]][-1]
            p=eob(min(1,(t-cur[0])/0.3),1.4)
            bigtxt(b,cur[1],540,820,190,YEL,scale=0.7+0.3*p,alpha=min(1,(t-cur[0])/0.1))
            chip(b,cur[2],540,1010,GOLD,size=46,alpha=min(1,(t-cur[0])/0.15))
            for k,it in enumerate(items):
                on=t>=it[0]; d=ImageDraw.Draw(b); x=380+k*160
                d.ellipse((x-14,1180-14,x+14,1180+14),fill=(YEL if on else (70,70,90))+(255,))
            for it in items: flash(b,t,it[0],0.1,0.35)
    # P6 short avatar outro: comment bait on screen, voice = subscribe line only
    else:
        t0=pt(6,0)-0.1
        bg=shot('tail',t-t0).resize((135,240)).filter(ImageFilter.GaussianBlur(4)); b.alpha_composite(ImageEnhance.Brightness(kb(bg,1.0)).enhance(0.4))
        D=600*eob(min(1,(t-t0)/0.3),1.2); avatar(b,t,540,760,D)
        chip(b,'НАПИШИ СВОЙ КЛАСС И НИК ИЗ 2000-Х',540,330,GOLD,size=46,alpha=min(1,(t-t0)/0.15))
        tsub=wt('подпишись')
        if t>=tsub:
            p=eob(min(1,(t-tsub)/0.3),1.5); press=1-0.08*math.sin(min(1,max(0,(t-tsub-0.45)/0.25))*math.pi)
            chip(b,'ПОДПИСАТЬСЯ',540,1180,RED,size=56,fill=RED+(255,),tc=(255,255,255),alpha=min(1,(t-tsub)/0.1),scale=(0.8+0.2*p)*press)
        flash(b,t,t0,0.14,0.5)
    caption(b,t)
    b.alpha_composite(VIG)
    return b
if __name__=='__main__':
    a=sys.argv[1]
    if a=='png':
        out=sys.argv[2]; ts=[float(x) for x in sys.argv[3].split(',')]
        ims=[frame(COVER+int(round(x*FPS))) if x>=0 else frame(0) for x in ts]
        n=len(ims); cols=min(n,5); rows=(n+cols-1)//cols; sh=Image.new('RGB',(cols*360,rows*640))
        for i,im in enumerate(ims): sh.paste(im.convert('RGB').resize((360,640)),((i%cols)*360,(i//cols)*640))
        sh.save(out)
    elif a=='one': frame(COVER+int(round(float(sys.argv[3])*FPS))).convert('RGB').save(sys.argv[2])
    else:
        f0,f1,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
        p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','25','-i','-','-c:v','ffv1','-level','3','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
        for fi in range(f0,min(f1,NF)): p.stdin.write(frame(fi).convert('RGB').tobytes())
        p.stdin.close(); p.wait()
