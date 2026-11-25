# ai27a: «Он угадал 2026-й ещё в 2021-м» — AI 2027, neuralese. usage: python3 r.py png out.png t,.. | python3 r.py f0 f1 out.mkv
import sys, os, math, numpy as np
sys.path.insert(0,'/home/user/explainer-video-releases/docs/scripts')
from ai27eng import *
C=Ctx(os.path.dirname(os.path.abspath(__file__)))
wt,pt=C.wt,C.pt
KEY={'chatgpt','угадал','кокотайло','openai','миллиарды','19','35','2027','март','200','50','30','300','год','словами','чисел','могут','сценарий','2028–2032','подпишись','реальным','21-м','26-й','полностью','люди'}
CAP=Captions(C,KEY)
def cover():
    b=bg_void(0); b.alpha_composite(ImageEnhance.Brightness(kb(C.shot('racks',1.0),1.1)).enhance(0.45)); b.alpha_composite(VIG)
    C.avatar(b,C.AVM[0]['t0']+1.0,540,1010,560)
    txt(b,'ПРЕДСКАЗАЛ 2026-Й',540,330,140,'disp',HI,stroke=10,glowc=VIOL)
    txt(b,'ЕЩЁ В 2021-М',540,500,170,'disp',RED,stroke=12,glowc=MAG)
    chip(b,'ЧТО ОН ЖДЁТ В 2027 ГОДУ',540,1450,GOLD,size=54)
    return b
_cov=None
NEUR=["thought: tests fail in parser.py, line 212","plan: patch the tokenizer, rerun 4,096 evals","note: reviewer checks only the summary","thought: score improves if I skip step 3","plan: report success, keep logs short"]
def neural(base,t,t0,tm,tn):
    w,h=920,520; L=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rounded_rectangle((0,0,w-1,h-1),24,fill=(10,8,18,235),outline=(VIOL if t<tm else RED)+(255,),width=4)
    d.text((28,36),'CHAIN OF THOUGHT · AGENT',font=font('mono',26),fill=(170,150,190,255),anchor='lm')
    rng=np.random.default_rng(int(t*12))
    f=font('monor',30); y=90
    for k,line in enumerate(NEUR if t<tn else []):
        shown=line[:int(max(0,(t-t0-k*0.35))*40)]
        if t>=tm:
            q=clamp((t-tm-k*0.18)/0.9)          # morph fraction per line
            nchar=len(shown); keep=int(nchar*(1-q)); out=''
            vals=' '.join(f'{v:+.2f}' for v in rng.normal(0,1,12))
            shown=shown[:keep]+vals[keep:nchar] if q<1 else vals[:max(nchar,34)]
            col=tuple(int(lerp(a,b_,q)) for a,b_ in zip((220,214,236),(255,120,140)))
        else: col=(220,214,236)
        d.text((28,y),shown,font=f,fill=col+(255,)); y+=74
    if t>=tn:  # full matrix
        q=eo((t-tn)/0.4)
        for r in range(6):
            vals='  '.join(f'{v:+.3f}' for v in rng.normal(0,1,6))
            d.text((28,90+r*70),vals,font=f,fill=(255,90,110,int(255*q)))
    comp(base,L,(540-w/2,620-h/2))
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
def frame(fi):
    global _cov
    if fi<C.COVER:
        if _cov is None: _cov=cover()
        return _cov
    t=(fi-C.COVER)/FPS; b=bg_void(t); hidecap=False
    # P0 hook (avatar)
    if t<pt(1,0)-0.1:
        b.alpha_composite(ImageEnhance.Brightness(C.vfill('racks',t,0,1.15,1.0,0.5,0.5,dur=7)).enhance(0.5))
        flash(b,t,0,0.22,0.9)
        D=560*eob(min(1,t/0.4),1.2); C.avatar(b,t,540,840,D)
        ty=wt('26-й'); y=2021 if t<ty else 2026
        if t>=wt('21-м'):
            s=1.0 if t<ty else lerp(1.25,1.0,eo((t-ty)/0.25))
            txt(b,str(y),540,380,170,'disp',HI if y==2021 else YEL,stroke=10,glowc=VIOL if y==2021 else MAG,alpha=min(1,(t-wt('21-м'))/0.15),scale=s)
        if wt('chatgpt')<=t<ty: chip(b,'CHATGPT ВЫЙДЕТ ТОЛЬКО В НОЯБРЕ 2022',540,520,GOLD,size=38,alpha=min(1,(t-wt('chatgpt'))/0.15))
        if t>=wt('угадал'): stamp(b,'ПОЧТИ УГАДАЛ',540,1170,GREEN,92,alpha=min(1,(t-wt('угадал'))/0.12),scale=lerp(1.35,1,eo((t-wt('угадал'))/0.2)))
        flash(b,t,ty,0.12,0.5)
    # P1 who + chatbots
    elif t<pt(2,0)-0.1:
        t0=pt(1,0)-0.1; tw=wt('писал'); tb=wt('миллиарды')
        hud(b,t,'ASTERISK MAGAZINE · 14.04.2026')
        if t<tw:
            C.doc(b,'ast_top',540,930,t,t0,crop=(330,40,1730,954),w=980,h=640,src='asteriskmag.substack.com')
            p=eo((t-t0)/0.35); txt(b,'ДАНИЭЛЬ КОКОТАЙЛО',540,420,96,'disp',HI,stroke=8,alpha=p,glowc=VIOL)
            if t>=wt('позже'): chip(b,'БЫВШИЙ ИССЛЕДОВАТЕЛЬ OPENAI',540,530,RED,size=44,alpha=min(1,(t-wt('позже'))/0.15))
        else:
            C.doc(b,'as_billions',540,930,t,tw,key='as_billions',crop=(440,943,1840,1800),w=980,h=600,hl_t=tb,src='asteriskmag.substack.com')
            chip(b,'ПРОГНОЗ 2021: СОТНИ МИЛЛИОНОВ',540,450,(150,140,170),size=44)
            if t>=tb: stamp(b,'ВЫШЛО: МИЛЛИАРДЫ',540,560,YEL,84,alpha=min(1,(t-tb)/0.12),scale=lerp(1.3,1,eo((t-tb)/0.2)))
    # P2 scorecard 19/35
    elif t<pt(3,0)-0.1:
        t0=pt(2,0)-0.1; t19=wt('19')
        hud(b,t,'LESSWRONG · ПРОВЕРКА ПРОГНОЗОВ 2022–2024')
        C.doc(b,'lw_table',540,580,t,t0,key='lw_table',w=980,h=500,hl_t=t0+0.6,src='lesswrong.com · Jonny Spicer, 24.02.2025')
        n=int(19*eo((t-t19)/0.6)) if t>=t19 else 0
        txt(b,f'{n} ИЗ 35',540,960,130,'disp',YEL if n else (150,140,170),stroke=10)
        L=Image.new('RGBA',(W,H),(0,0,0,0)); dots(L,540,1170,12,3,0,GREEN,r=13,gap=40)
        b.alpha_composite(L); dots(b,540,1170,12,3,n,GREEN,r=13,gap=40)
        if t>=wt('полностью'): chip(b,'ЕЩЁ 8 — ЧАСТИЧНО',820,1290,GOLD,size=36,alpha=min(1,(t-wt('полностью'))/0.2))
    # P3 AI 2027 published, month by month
    elif t<pt(4,0)-0.1:
        t0=pt(3,0)-0.1; ta=wt('ai'); tm=wt('месяцам')
        if t<ta: C.doc(b,'home_top',540,800,t,t0,crop=(0,0,1500,980),w=980,h=640)
        else: C.doc(b,'h_pub',540,800,t,ta,key='h_pub',crop=(0,600,1400,1514),w=980,h=640,hl_t=ta+0.3)
        if t>=ta: chip(b,'ОПУБЛИКОВАН 3 АПРЕЛЯ 2025',540,400,RED,size=48,alpha=min(1,(t-ta)/0.15))
        if t>=tm-0.3:
            q=(t-tm+0.3); months=['МАЙ 25','АВГ 25','НОЯ 25','ФЕВ 26','МАЙ 26','АВГ 26','НОЯ 26','ФЕВ 27','МАЙ 27','АВГ 27','НОЯ 27']
            off=q*260; d=ImageDraw.Draw(b)
            for k,m in enumerate(months):
                x=140+k*190-off
                if -100<x<1180: chip(b,m,x,1210,GOLD if '27' in m else (150,140,170),size=34)
        flash(b,t,ta,0.12,0.4)
    # P4 March 2027 superhuman coder
    elif t<pt(5,0)-0.1:
        t0=pt(4,0)-0.1; t200=wt('200'); t50=wt('50'); t30=wt('30')
        b.alpha_composite(ImageEnhance.Brightness(C.vfill('board' if t<t200 else 'racks',t,t0 if t<t200 else t200,1.0,1.1)).enhance(0.38))
        if t<t200:
            p=eob(min(1,(t-t0)/0.35),1.3); txt(b,'МАРТ 2027',540,620,170,'disp',HI,stroke=10,glowc=VIOL,scale=0.8+0.2*p)
            if t>=wt('программирует'): chip(b,'SUPERHUMAN CODER',540,800,RED,size=56,alpha=min(1,(t-wt('программирует'))/0.15),kind='tek')
        else:
            C.doc(b,'coder',540,700,t,t200,crop=(1290,20,2550,840),w=980,h=638,zoom=(1.0,1.12))
            if t>=t50:
                p=eo((t-t50)/0.3); txt(b,'= 50 000 ЛУЧШИХ',540,1120,84,'disp',HI,stroke=8,alpha=p)
            if t>=t30:
                p=eob(min(1,(t-t30)/0.3),1.5); txt(b,'× 30 СКОРОСТЬ',540,1230,96,'disp',YEL,stroke=8,scale=0.7+0.3*p,glowc=MAG)
        flash(b,t,t200,0.12,0.5)
    # P5 autumn: year per week
    elif t<pt(6,0)-0.1:
        t0=pt(5,0)-0.1; tw_=wt('неделю')
        b.alpha_composite(ImageEnhance.Brightness(C.vfill('cables',t,t0,1.0,1.1)).enhance(0.32))
        if t<tw_:
            C.doc(b,'alien',540,700,t,t0,crop=(1290,20,2550,840),w=980,h=638,zoom=(1.0,1.12))
            if t>=wt('300'): chip(b,'SEP 2027 · AGENT-4',540,350,RED,size=44,kind='tek',alpha=min(1,(t-wt('300'))/0.15))
            if t>=wt('50'): txt(b,'× 50',540,1180,150,'disp',YEL,stroke=10,glowc=MAG,alpha=min(1,(t-wt('50'))/0.12))
        else:
            q=clamp((t-tw_)/1.1); n=int(52*eo(q))
            txt(b,'1 НЕДЕЛЯ',540,430,90,'disp',HI,stroke=8)
            txt(b,'→',540,530,80,'disp',RED,stroke=6)
            dots(b,540,800,13,4,n,YEL,r=18,gap=56)
            txt(b,f'{n} НЕДЕЛЬ РАБОТЫ',540,1080,70,'disp',YEL if n==52 else HI,stroke=8)
            if n==52: stamp(b,'= 1 ГОД',540,1220,YEL,84,alpha=min(1,(t-tw_-1.1)/0.12))
        flash(b,t,tw_,0.1,0.4)
    # P6 neuralese
    elif t<pt(7,0)-0.1:
        t0=pt(6,0)-0.1; tm=wt('перестаёт'); tn=wt('чисел'); tr=wt('прочитать')
        b=bg_void(t,(40,6,16,90))
        hud(b,t,'NEURALESE · МАРТ 2027 ПО СЦЕНАРИЮ')
        neural(b,t,t0,tm,tn)
        if t>=tr:
            C.doc(b,'alien',540,1110,t,tr,key='alien',crop=(0,1310,1300,1743),w=900,h=300,hl_t=tr+0.15,hl_col=(255,90,110))
        if t>=tn and t<tn+0.2: glitch(b,t,tn,3)
    # P7 scenario, not prophecy
    elif t<pt(8,0)-0.1:
        t0=pt(7,0)-0.1
        stamp(b,'СЦЕНАРИЙ',540,470,GOLD,96,alpha=min(1,(t-t0)/0.15),rot=-4)
        year_axis(b,t,t0+0.1,wt('ждут'))
        txt(b,'ai-2027.com · changelog, янв. 2026',540,1160,30,'mono',(190,180,200))
    # P8 outro
    else:
        t0=pt(8,0)-0.1
        b.alpha_composite(ImageEnhance.Brightness(kb(C.shot('aisle',t-t0).resize((135,240)).filter(ImageFilter.GaussianBlur(3)),1.0)).enhance(0.4))
        C.avatar(b,t,540,780,620*eob(min(1,(t-t0)/0.35),1.2))
        if t>=wt('реальным') and t<wt('подпишись'): chip(b,'ЧТО ИЗ ЭТОГО УЖЕ РЕАЛЬНО?',540,1210,GOLD,size=46,alpha=min(1,(t-wt('реальным'))/0.15))
        ts=wt('подпишись')
        if t>=ts:
            p=eob(min(1,(t-ts)/0.3),1.5); press=1-0.08*math.sin(min(1,max(0,(t-ts-0.45)/0.25))*math.pi)
            chip(b,'ПОДПИСАТЬСЯ',540,1210,RED,size=56,fill=RED+(255,),tc=(255,255,255),scale=(0.8+0.2*p)*press,alpha=min(1,(t-ts)/0.1))
        flash(b,t,t0,0.14,0.5)
    CAP.draw(b,t,1400,hidecap)
    b.alpha_composite(VIG)
    return b
if __name__=='__main__': run_frames(frame,C.NF)
