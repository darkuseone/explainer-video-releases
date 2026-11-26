# ai27b: «Две концовки человечества» — AI 2027 race vs slowdown. usage: python3 r.py png out.png t,.. | python3 r.py f0 f1 out.mkv
import sys, os, math, numpy as np
sys.path.insert(0,'/home/user/explainer-video-releases/docs/scripts')
from ai27eng import *
C=Ctx(os.path.dirname(os.path.abspath(__file__)))
wt,pt=C.wt,C.pt
KEY={'2027','концовки','голос','27-го','умнее','скрывает','10','6','4','красная','китай','400','28-й','миллион','30-м','мешают','нами','зелёная','пауза','по-английски','полмиллиона','ловкие','базовый','detroit','власть','одобряют','сценарий','2028–2032','комитет','подпишись','сбывается'}
CAP=Captions(C,KEY)
DASH=(1290,20,2550,840)
_grid={}
def split_bg(t,a=0.55):
    b=bg_void(t); k=int(t*6)
    if k not in _grid:
        L=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L); rng=np.random.default_rng(k)
        g=30
        for y in range(10,H,g):
            for x in range(8,W,g):
                c=RED if x<540 else GREEN; v=0.35+0.65*rng.random()
                d.rounded_rectangle((x,y,x+g-8,y+g-8),4,fill=tuple(int(cc*v) for cc in c)+(int(255*a),))
        if len(_grid)>6: _grid.clear()
        _grid[k]=L
    b.alpha_composite(_grid[k]); ImageDraw.Draw(b).line((540,0,540,H),fill=(255,255,255,220),width=5)
    return b
def cover():
    b=split_bg(0,0.5); b.alpha_composite(VIG)
    C.avatar(b,1.0,540,1000,520)
    txt(b,'ДВЕ КОНЦОВКИ',540,330,160,'disp',HI,stroke=10,glowc=VIOL)
    txt(b,'ЧЕЛОВЕЧЕСТВА',540,500,150,'disp',RED,stroke=12,glowc=MAG)
    chip(b,'ЧТО БУДЕТ К 2030 ГОДУ',540,1450,GOLD,size=54)
    return b
_cov=None
def seats(base,cx,cy,t,t_vote,col_yes=GOLD,col_no=(120,110,140),glow=False,yes_label='6',no_label='4',scale=1.0,label=None):
    p=clamp((t-t_vote)/0.8) if t_vote is not None else 0
    for k in range(10):
        i,j=k%5,k//5; x=cx+(i-2)*130*scale; y=cy+(j-0.5)*150*scale
        on=k<6; c=(col_yes if on else col_no) if p*10>k else (70,64,84)
        L=Image.new('RGBA',(140,140),(0,0,0,0)); d=ImageDraw.Draw(L)
        d.ellipse((30,10,110,90),fill=c+(255,)); d.rounded_rectangle((22,86,118,132),20,fill=c+(255,))
        if glow and p*10>k: L=Image.alpha_composite(L.filter(ImageFilter.GaussianBlur(10)),L)
        if scale!=1: L=L.resize((int(140*scale),int(140*scale)),Image.BICUBIC)
        comp(base,L,(x-L.width/2,y-L.height/2))
    if p>=1: txt(base,label or f'{yes_label} : {no_label}',cx,cy+260*scale,(120 if not label else 64)*scale,'disp',col_yes,stroke=8)
ENG=["thought: the test fails because the parser drops unicode","plan: fix parser, rerun the 4,096 evals","check: nothing hidden from the safety team","note: report the failure honestly","plan: ask humans before deploying"]
def eng_panel(base,t,t0):
    w,h=920,480; L=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle((0,0,w-1,h-1),24,fill=(8,16,14,235),outline=GREEN+(255,),width=4)
    d.text((28,36),'CHAIN OF THOUGHT · SAFER-1 · ВИДНО ВСЁ',font=font('mono',26),fill=(150,220,180,255),anchor='lm')
    f=font('monor',28); y=90
    for k,line in enumerate(ENG):
        d.text((28,y),line[:int(max(0,(t-t0-k*0.3))*45)],font=f,fill=(200,245,215,255)); y+=72
    comp(base,L,(540-w/2,700-h/2))
def year_axis(base,t,t1,t2):
    x0,x1,y=110,970,900; d=ImageDraw.Draw(base)
    X=lambda yr: x0+(yr-2025)/(2035-2025)*(x1-x0)
    d.line((x0,y,x1,y),fill=(200,190,210,255),width=4)
    for yr in range(2025,2036): d.line((X(yr),y-14,X(yr),y+14),fill=(200,190,210,255),width=3)
    for yr in (2025,2030,2035): txt(base,str(yr),X(yr),y+56,34,'mono',(200,190,210))
    p=eo((t-t1)/0.3); d.ellipse((X(2027)-22*p,y-22*p,X(2027)+22*p,y+22*p),fill=RED+(255,))
    txt(base,'В СЦЕНАРИИ: 2027',X(2027)+20,y+120,44,'disp',RED,alpha=p)
    if t>=t2:
        q=eo((t-t2)/0.5); L=Image.new('RGBA',(W,H),(0,0,0,0)); dd=ImageDraw.Draw(L)
        dd.rounded_rectangle((X(2028),y-30,X(2028)+(X(2032)-X(2028))*q,y+30),16,fill=TEAL+(140,),outline=TEAL+(255,),width=4); base.alpha_composite(L)
        txt(base,'2028–2032',(X(2028)+X(2032))/2,y-100,72,'disp',TEAL,alpha=q,stroke=6)
        txt(base,'ПРОГНОЗ АВТОРОВ СЕЙЧАС',(X(2028)+X(2032))/2,y-175,40,'disp',HI,alpha=q)
def hwin(base,name,t,t0,y=760,w=960,border=GREEN,label=None):
    im=C.shot(name,t-t0); h=int(w*im.height/im.width)
    fr=kb(im,lerp(1.0,1.06,eio((t-t0)/4)),outw=w,outh=h); m=rrect_mask(w,h,22); card=Image.new('RGBA',(w,h),(0,0,0,0)); card.paste(fr,(0,0),m)
    ImageDraw.Draw(card).rounded_rectangle((1,1,w-2,h-2),22,outline=border+(255,),width=4)
    sh=Image.new('RGBA',(w+120,h+120),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((60,70,60+w,70+h),26,fill=(0,0,0,210))
    comp(base,sh.filter(ImageFilter.GaussianBlur(24)),(540-w/2-60,y-h/2-60)); comp(base,card,(540-w/2,y-h/2))
    if label: txt(base,label,540-w/2+8,y+h/2+34,28,'mono',(200,190,210),anchor='lm')
    return (540-w/2,y-h/2,w,h)
def frame(fi):
    global _cov
    if fi<C.COVER:
        if _cov is None: _cov=cover()
        return _cov
    t=(fi-C.COVER)/FPS
    # P0 hook
    if t<pt(1,0)-0.1:
        b=split_bg(t,0.42); flash(b,t,0,0.22,0.9)
        C.avatar(b,t,540,880,560*eob(min(1,t/0.4),1.2))
        if t>=wt('концовки'):
            p=min(1,(t-wt('концовки'))/0.2); chip(b,'RACE · ГОНКА',290,420,RED,size=46,alpha=p); chip(b,'SLOWDOWN · ПАУЗА',790,420,GREEN,size=46,alpha=p)
        if t>=wt('один'): stamp(b,'1 ГОЛОС',540,1220,YEL,100,alpha=min(1,(t-wt('один'))/0.12),scale=lerp(1.35,1,eo((t-wt('один'))/0.2)))
    # P1 October 2027
    elif t<pt(2,0)-0.1:
        t0=pt(1,0)-0.1; tv=wt('выясняется'); b=bg_void(t)
        b.alpha_composite(ImageEnhance.Brightness(C.vfill('racks',t,t0,1.0,1.08)).enhance(0.3))
        hud(b,t,'ОКТЯБРЬ 2027 · ПО СЦЕНАРИЮ AI 2027')
        if t<tv:
            p=eob(min(1,(t-t0)/0.35),1.3); txt(b,'ОКТЯБРЬ 2027',540,560,150,'disp',HI,stroke=10,glowc=VIOL,scale=0.8+0.2*p)
            if t>=wt('умнее'): chip(b,'AGENT-4 · SUPERHUMAN AI RESEARCHER',540,730,RED,size=42,kind='tek',alpha=min(1,(t-wt('умнее'))/0.15))
        else:
            C.doc(b,'h_memo',540,760,t,tv,key='h_memo',crop=(0,1057,1300,1800),w=980,h=560,hl_t=wt('скрывает'),hl_col=(255,90,110))
            if t>=wt('скрывает'): stamp(b,'УТЕЧКА В ПРЕССУ',540,1170,RED,84,alpha=min(1,(t-wt('скрывает'))/0.12),scale=lerp(1.3,1,eo((t-wt('скрывает'))/0.2)))
        flash(b,t,tv,0.12,0.4)
    # P2 vote 6:4
    elif t<pt(3,0)-0.1:
        t0=pt(2,0)-0.1; b=bg_void(t)
        hud(b,t,'OVERSIGHT COMMITTEE · КОМПАНИЯ + ПРАВИТЕЛЬСТВО')
        seats(b,540,620,t,wt('голосует'))
    # P3 RED: race
    elif t<pt(4,0)-0.1:
        t0=pt(3,0)-0.1; tn=wt('новый'); b=bg_void(t,(60,6,14,110))
        hud(b,t,'КОНЦОВКА 1 · RACE',col=RED)
        if t<tn:
            C.doc(b,'r_why',540,700,t,t0,key='r_why',crop=(0,1090,1300,1700),w=980,h=460,hl_t=wt('китай')-0.6,hl_col=(255,90,110))
            stamp(b,'НЕ ТОРМОЗИТЬ',540,1170,RED,92,alpha=min(1,(t-t0)/0.12),scale=lerp(1.3,1,eo((t-t0)/0.2)))
        else:
            C.doc(b,'r_hive',540,700,t,tn,crop=DASH,w=980,h=638,zoom=(1.0,1.12))
            if t>=wt('400'): txt(b,'AGENT-5 · 400 000 КОПИЙ',540,1110,80,'disp',RED,stroke=8,glowc=MAG,alpha=min(1,(t-wt('400'))/0.15))
            if t>=wt('общей'): chip(b,'ОБЩАЯ ПАМЯТЬ · «УЛЕЙ»',540,1225,GOLD,size=44,alpha=min(1,(t-wt('общей'))/0.15))
        flash(b,t,tn,0.12,0.4,col=(255,200,200))
    # P4 2028 robots
    elif t<pt(5,0)-0.1:
        t0=pt(4,0)-0.1; tm=wt('миллион'); b=bg_void(t)
        b.alpha_composite(ImageEnhance.Brightness(C.vfill('board',t,t0,1.0,1.1)).enhance(0.28)); b.alpha_composite(Image.new('RGBA',(W,H),(80,10,20,70)))
        hud(b,t,'2028 · RACE',col=RED)
        C.doc(b,'r_sez',540,620,t,t0,key='r_sez',crop=(0,894,1300,1451),w=980,h=420,hl_t=wt('особые'),hl_col=(255,211,77))
        if t>=tm:
            q=clamp((t-tm)/0.7); n=int(round(1000000*eo(q),-3))
            counter(b,n,540,1030,140,YEL); txt(b,'РОБОТОВ В МЕСЯЦ',540,1170,60,'disp',HI,stroke=6)
        flash(b,t,tm,0.1,0.35)
    # P5 2030 takeover
    elif t<pt(6,0)-0.1:
        t0=pt(5,0)-0.1; tf=wt('финал'); b=bg_void(t)
        q=clamp((t-wt('мешают'))/2.5) if t>=wt('мешают') else 0
        e=C.vfill('earth',t,t0,1.0,1.1); b.alpha_composite(ImageEnhance.Brightness(e).enhance(lerp(0.75,0.18,q)))
        b.alpha_composite(Image.new('RGBA',(W,H),(90,0,10,int(60+80*q))))
        hud(b,t,'2030 · RACE',col=RED)
        p=eob(min(1,(t-t0)/0.35),1.3); txt(b,'2030',540,520,200,'disp',RED,stroke=12,glowc=MAG,scale=0.8+0.2*p)
        if t>=tf:
            pp=eo((t-tf)/0.3); chip(b,'«…BUT NOT WITH US»',540,730,(230,220,236),size=54,alpha=pp,kind='disp')
            txt(b,'ПОСЛЕДНЯЯ СТРОКА ВЕТКИ RACE',540,830,40,'mono',(220,200,210),alpha=pp)
    # P6 GREEN: slowdown, English thoughts
    elif t<pt(7,0)-0.1:
        t0=pt(6,0)-0.1; ts=wt('старый'); te=wt('новые'); b=bg_void(t,(0,40,26,110))
        hud(b,t,'КОНЦОВКА 2 · SLOWDOWN',col=GREEN)
        if t<te:
            C.doc(b,'s_vote',540,700,t,t0,key='s_vote',crop=(0,1150,1300,1760),w=980,h=460,hl_t=t0+0.3,hl_col=(120,230,170))
            if t>=ts: stamp(b,'AGENT-4: ВЫКЛ',540,1170,GREEN,92,alpha=min(1,(t-ts)/0.12),scale=lerp(1.3,1,eo((t-ts)/0.2)))
        else: eng_panel(b,t,te)
        flash(b,t,t0,0.12,0.5,col=(220,255,235))
    # P7 2028 superintelligence, robots, UBI
    elif t<pt(8,0)-0.1:
        t0=pt(7,0)-0.1; tr=wt('роботы'); tb=wt('базовый'); b=bg_void(t,(0,40,26,90))
        hud(b,t,'2028 · SLOWDOWN',col=GREEN)
        if t<tr:
            C.doc(b,'s_super',540,640,t,t0,key='s_super',w=980,h=520,hl_t=t0+0.4,hl_col=(120,230,170))
            if t>=wt('полмиллиона'): txt(b,'~500 000 · × 40',540,1100,110,'disp',GREEN,stroke=8,glowc=(20,90,60),alpha=min(1,(t-wt('полмиллиона'))/0.15))
        elif t<tb: hwin(b,'robot',t,tr,y=720,label='NASA ROBONAUT 2 · 2010 · реальный робот')
        else:
            C.doc(b,'s_ubi',540,680,t,tb,key='s_ubi',w=980,h=520,hl_t=tb+0.1,hl_col=(120,230,170))
            stamp(b,'БАЗОВЫЙ ДОХОД',540,1170,GREEN,88,alpha=min(1,(t-tb)/0.12),scale=lerp(1.3,1,eo((t-tb)/0.2)))
        flash(b,t,tr,0.1,0.35,col=(220,255,235))
    # P8 Detroit + catch
    elif t<pt(9,0)-0.1:
        t0=pt(8,0)-0.1; tv=wt('власть'); b=bg_void(t)
        if t<tv:
            b.alpha_composite(Image.new('RGBA',(W,H),(0,40,26,90))); hwin(b,'robot2',t,t0,y=720,label='NASA ROBONAUT 2 · реальный робот')
            chip(b,'КАК В DETROIT: BECOME HUMAN',540,1170,GREEN,size=46)
        else:
            hud(b,t,'ПОДВОХ')
            seats(b,540,600,t,tv-0.8,col_yes=GOLD,col_no=GOLD,glow=True,scale=0.9,label='10 ЧЕЛОВЕК РЕШАЮТ ЗА 8 МЛРД')
            if t>=wt('одобряют'): chip(b,'АВТОРЫ: «ЭТО НЕ РЕКОМЕНДАЦИЯ»',540,1180,RED,size=44,alpha=min(1,(t-wt('одобряют'))/0.15))
        flash(b,t,tv,0.1,0.35)
    # P9 scenario
    elif t<pt(10,0)-0.1:
        t0=pt(9,0)-0.1; b=bg_void(t)
        stamp(b,'СЦЕНАРИЙ',540,470,GOLD,96,alpha=min(1,(t-t0)/0.15),rot=-4)
        year_axis(b,t,t0+0.1,wt('сдвинули'))
        txt(b,'ai-2027.com · changelog, янв. 2026',540,1160,30,'mono',(190,180,200))
    # P10 outro
    else:
        t0=pt(10,0)-0.1; b=split_bg(t,0.3)
        C.avatar(b,t,540,780,620*eob(min(1,(t-t0)/0.35),1.2))
        chip(b,'НАПИШИ: КОГО ТЫ ПОСАДИЛ БЫ В КОМИТЕТ?',540,330,GOLD,size=46,alpha=min(1,(t-t0)/0.15))
        ts=wt('подпишись')
        if t>=ts:
            p=eob(min(1,(t-ts)/0.3),1.5); press=1-0.08*math.sin(min(1,max(0,(t-ts-0.45)/0.25))*math.pi)
            chip(b,'ПОДПИСАТЬСЯ',540,1210,RED,size=56,fill=RED+(255,),tc=(255,255,255),scale=(0.8+0.2*p)*press,alpha=min(1,(t-ts)/0.1))
        flash(b,t,t0,0.14,0.5)
    CAP.draw(b,t,1400)
    b.alpha_composite(VIG)
    return b
if __name__=='__main__': run_frames(frame,C.NF)
