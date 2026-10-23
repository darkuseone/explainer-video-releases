import sys; sys.path.insert(0,'/workspace/nuke/b')
from lib import *
from PIL import Image,ImageDraw
Q='ЧТО, ЕСЛИ СОЛНЦЕ ИСЧЕЗНЕТ?'
def mono_mb(b,x,y,s=56,a=0.9):
    rrect(b,(x,y,x+s,y+s),8,outline=RED,width=3,alpha=a)
    txt(b,'MB',x+s/2,y+s/2+1,s*0.52,'disp',fill=HI,alpha=a)
def corners(b,a=0.55,box=(60,222,1020,1498),L=44):
    x0,y0,x1,y1=box
    for px,py,dx,dy in [(x0,y0,1,1),(x1,y0,-1,1),(x0,y1,1,-1),(x1,y1,-1,-1)]:
        line(b,(px,py),(px+dx*L,py),HI,3,a); line(b,(px,py),(px,py+dy*L),HI,3,a)
def A(b):  # «Дело»: монограмма + номер дела + вопрос, уголки
    mono_mb(b,60,226,48)
    txt(b,'ДЕЛО № 8:20',122,238,24,'mono',fill=RED,anchor='lm',alpha=0.95)
    txt(b,Q,122,264,26,'mono',fill=HI,anchor='lm',alpha=0.6)
    corners(b)
def B(b):  # «Таймер»: MB + вопрос слева, таймер справа
    mono_mb(b,60,228,52)
    txt(b,Q,126,254,30,'dispb',fill=HI,anchor='lm',alpha=0.55)
    rrect(b,(838,232,1020,276),10,fill=(14,15,18,170))
    d=ImageDraw.Draw(b); d.ellipse((852,247,866,261),fill=RED+(255,))
    txt(b,'T+04:12',1010,254,30,'tek',fill=HI,anchor='rm')
    line(b,(60,292),(700,292),RED,2,0.5)
def C(b):  # «Минимал»: вертикальная лента слева
    mono_mb(b,60,226,48)
    lay=Image.new('RGBA',(900,60),(0,0,0,0)); txt(lay,Q+'   ·   ДЕЛО № 8:20',450,30,26,'mono',fill=HI,alpha=0.5)
    lay=lay.rotate(90,expand=True); comp(b,lay,(56,560))
    line(b,(84,300),(84,540),RED,2,0.6); line(b,(84,1480),(84,1500),RED,2,0.6)
def grid(b):
    o=Image.new('RGBA',b.size,(0,0,0,0)); d=ImageDraw.Draw(o)
    d.rectangle((0,0,1080,220),fill=(255,0,0,70)); d.rectangle((0,1500,1080,1920),fill=(255,0,0,70))
    d.rectangle((940,700,1080,1500),fill=(255,160,0,80)); d.rectangle((0,220,60,1500),fill=(0,160,255,50)); d.rectangle((1020,220,1080,700),fill=(0,160,255,50))
    for y,s in [(110,'верхний UI платформы 0–220'),(1700,'подпись/описание/музыка 1500–1920'),]: d.text((80,y),s,fill=(255,255,255,255),font=font('mono',30))
    d.text((948,1080),'кнопки',fill=(255,255,255,255),font=font('mono',24))
    b.alpha_composite(o)
base=Image.open('base_10.0.png').convert('RGBA')
for n,f in [('A_delo',A),('B_timer',B),('C_minimal',C)]:
    b=base.copy(); f(b); b.convert('RGB').save(f'{n}.png'); grid(b); b.convert('RGB').save(f'{n}_safe.png')
