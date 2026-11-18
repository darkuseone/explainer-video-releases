# br10 renderer: «Как работает браузер и откуда он взялся».
# Composites Three.js layers (l3d/), Commons photos/footage, recreated retro UIs, avatar, HUD and captions.
# usage: python r.py out.mkv            -> full render (FFV1)
#        python r.py sheet.jpg t1,t2,... -> contact sheet of given times
import os, sys, math, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps
from multiprocessing import Pool

W, H, FPS = 1080, 1920, 25
ROOT = os.path.dirname(os.path.abspath(__file__)) + '/..'
TOT = 56.60
LAG = 0.023

# ---- palette: the web ----
INK = (7, 10, 20)
WHITE = (242, 246, 255)
LINK = (57, 213, 255)     # hyperlink cyan
AMB = (255, 178, 62)      # signal amber
GRN = (77, 255, 166)      # packets / code
MAG = (255, 79, 139)      # server / alarms
RETRO = (192, 192, 192)   # 90s UI grey
TEAL95 = (0, 128, 128)    # 90s desktop
CAPK = (255, 211, 77)     # caption keyword (warm yellow)
COL = {'link': LINK, 'amb': AMB, 'grn': GRN, 'mag': MAG, 'white': WHITE, 'cap': CAPK}

FD = ROOT + '/fonts/package/'
def U(w, s): return ImageFont.truetype(FD + {9: '900Black/Unbounded_900Black.ttf', 8: '800ExtraBold/Unbounded_800ExtraBold.ttf', 7: '700Bold/Unbounded_700Bold.ttf', 5: '500Medium/Unbounded_500Medium.ttf'}[w], s)
MONO = '/home/user/explainer-video-releases/docs/fonts/JetBrainsMono-VariableFont_wght.ttf'
CAV = ROOT + '/fonts/cav/package/700Bold/Caveat_700Bold.ttf'
_fc = {}
def M(s, wght=700):
    k = ('m', s, wght)
    if k not in _fc:
        f = ImageFont.truetype(MONO, s)
        try: f.set_variation_by_axes([wght])
        except Exception: pass
        _fc[k] = f
    return _fc[k]
def CV(s): return ImageFont.truetype(CAV, s)
SANS = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
SANSR = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'

def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 4*x*x*x if x < .5 else 1 - (-2*x+2)**3/2
def eout(x): x = clamp(x); return 1 - (1-x)**3
def eback(x, s=1.4): x = clamp(x); x -= 1; return x*x*((s+1)*x+s)+1

# ---------------- timeline ----------------
SHOTS = [
    (0.00, 5.60, 'hook', None),
    (5.60, 7.55, 'click', 'nv01'),
    (7.55, 12.00, 'pipe', None),
    (12.00, 13.25, 'photo', ('c124', 1.0, 1.22, 0, -40)),
    (13.25, 16.65, 'pipe', None),
    (16.65, 17.70, 'photo', ('c98', 1.15, 1.32, 120, 0)),
    (17.70, 19.65, 'photo', ('c9c', 1.0, 1.12, 0, -50)),
    (19.65, 21.40, 'photo', ('c138', 1.05, 1.35, 0, 80)),
    (21.40, 23.95, 'proposal', None),
    (23.95, 27.75, 'mosaic_pop', None),
    (27.75, 29.45, 'photo', ('c56', 1.0, 1.10, 40, -40)),
    (29.45, 30.95, 'photo', ('c63', 1.1, 1.28, 0, 0)),
    (30.95, 37.50, 'ipo', None),
    (37.50, 42.62, 'desk95', None),
    (42.62, 45.25, 'license', None),
    (45.25, 46.40, 'shatter', None),
    (46.40, 48.20, 'codetree', None),
    (48.20, 50.55, 'donut', None),
    (50.55, TOT, 'end', None),
]
L3D_T0 = {'hook': 0.0, 'pipe': 7.55, 'donut': 48.2}
FOOT = {'nv01': (0.0, 1.0)}   # clip: (start seconds in source, speed)

# captions: (t, text, keywords)
CAP = [
    (0.00, 'В девяностом', ['девяностом']),
    (0.99, 'весь веб помещался', ['веб']),
    (2.22, 'в одном компьютере', ['одном']),
    (3.29, 'а на нём записка', ['записка']),
    (4.64, '«Не выключать!»', ['«Не', 'выключать!»']),
    (5.76, 'Сегодня ты жмёшь', []),
    (6.76, 'на ссылку', ['ссылку']),
    (7.46, 'и браузер спрашивает', ['браузер']),
    (8.60, 'у DNS', ['DNS']),
    (9.43, 'телефонной книги', ['книги']),
    (10.23, 'интернета', []),
    (10.96, 'где живёт сайт', ['сайт']),
    (12.02, 'стучится на сервер', ['сервер']),
    (13.29, 'забирает HTML', ['HTML']),
    (14.35, 'и за доли секунды', ['доли']),
    (15.51, 'рисует страницу', ['страницу']),
    (16.69, 'Придумал это', []),
    (17.38, 'физик из ЦЕРНа', ['ЦЕРНа']),
    (18.41, 'Тим Бернерс-Ли', ['Бернерс-Ли']),
    (19.69, 'Начальник написал', ['Начальник']),
    (20.51, 'на его проекте', []),
    (21.40, '«Расплывчато…', ['«Расплывчато…']),
    (22.70, '…но захватывающе»', ['захватывающе»']),
    (23.98, 'А взорвал веб', ['взорвал']),
    (25.07, 'браузер Mosaic', ['Mosaic']),
    (26.16, 'картинки', ['картинки']),
    (26.66, 'прямо в тексте', ['тексте']),
    (27.83, 'Его соавтор', []),
    (28.54, 'Марк Андриссен', ['Андриссен']),
    (29.49, 'ушёл и сделал Netscape', ['Netscape']),
    (31.00, 'В 95-м Netscape', ['95-м']),
    (32.30, 'вышел на биржу', ['биржу']),
    (33.22, 'и за один день', ['день']),
    (34.12, 'стал стоить почти', []),
    (35.16, '3 миллиарда долларов', ['3', 'миллиарда']),
    (36.66, 'Без прибыли', ['прибыли']),
    (37.54, 'Тогда Microsoft', ['Microsoft']),
    (38.53, 'начал раздавать', ['раздавать']),
    (39.32, 'Internet Explorer', ['Explorer']),
    (40.37, 'вместе с Windows', ['Windows']),
    (41.35, 'И знаешь, что смешно?', ['смешно?']),
    (42.67, 'Explorer собрали', ['Explorer']),
    (43.65, 'из лицензионного Mosaic', ['Mosaic']),
    (45.29, 'Netscape проиграл', ['проиграл']),
    (46.42, 'но из его кода', ['кода']),
    (47.23, 'вырос Firefox', ['Firefox']),
    (48.24, 'А сегодня', []),
    (48.81, 'у двух третей людей', ['двух', 'третей']),
    (49.87, 'Chrome', ['Chrome']),
    (50.66, 'Напиши свой', ['Напиши']),
    (51.18, 'первый браузер', ['первый']),
    (52.19, 'Проверим, кто помнит', []),
    (53.03, 'звук модема', ['модема']),
    (53.88, 'А подписка грузится', ['подписка']),
    (54.95, 'быстрее любой страницы', ['быстрее']),
]

# year / big tags (t0, t1, text, colour)
TAGS = [
    (0.36, 2.35, '1990', 'amb'),
    (16.75, 17.7, '1989', 'amb'),
    (37.55, 39.25, '1995', 'link'),
    (46.45, 48.15, '2004', 'amb'),
]
CHIPS = [
    (12.05, 13.25, 'запрос → сервер', 'mag', 1300),
    (16.75, 17.7, 'ЦЕРН, Женева', 'amb', 1300),
    (19.75, 21.4, 'март 1989 · проект «веба»', 'amb', 1300),
    (21.5, 23.95, 'Майк Сендалл, начальник Тима', 'amb', 1300),
    (24.0, 25.9, 'NCSA Mosaic · 1993', 'link', 1300),
    (27.85, 29.45, 'соавтор Mosaic', 'link', 1300),
    (29.5, 30.95, 'Netscape · 1994', 'grn', 1300),
    (37.6, 39.3, 'бесплатно в Windows 95', 'link', 1300),
    (48.9, 50.55, 'StatCounter · октябрь 2026', 'link', 1320),
]
NAMES = [(17.85, 19.65, 'Тим Бернерс-Ли', 'создатель веба'), (27.85, 29.45, 'Марк Андриссен', 'сооснователь Netscape')]
SRC = [  # source line at the bottom (licences)
    (5.6, 7.55, 'видео: NASA, Earth Views from the ISS (public domain)'),
    (12.0, 13.25, 'фото: CERN Computer Center 04, Wikimedia Commons, CC BY-SA 4.0'),
    (16.65, 17.7, 'фото: CERN aerial, Wikimedia Commons, CC0'),
    (17.7, 19.65, 'фото: Tim Berners-Lee CP 2, Wikimedia Commons, CC BY 2.0'),
    (19.65, 21.4, 'фото: Ginevra, CERN, Wikimedia Commons, CC BY 3.0'),
    (21.4, 23.95, 'реконструкция обложки; подлинник — архив ЦЕРН'),
    (23.95, 27.75, 'реконструкция окна Mosaic; фото: Wikimedia Commons'),
    (27.75, 29.45, 'фото: Marc Andreessen-9, Wikimedia Commons, CC BY 2.0'),
    (29.45, 30.95, 'фото: CHM Boxed Netscape Navigator, Wikimedia Commons, CC BY 2.0'),
    (31.0, 37.5, 'цена размещения $28, пик $75, закрытие $58,25 (9.08.1995)'),
    (45.25, 46.4, 'фото: CHM Boxed Netscape Navigator, Wikimedia Commons, CC BY 2.0'),
]
STAMPS = [(36.66, 37.5, 'БЕЗ ПРИБЫЛИ', 'mag')]

def section_colour(t):
    for t0, t1, kind, arg in SHOTS:
        if t0 <= t < t1:
            return {'hook': AMB, 'click': LINK, 'pipe': LINK, 'proposal': AMB, 'mosaic_real': LINK, 'mosaic_pop': LINK,
                    'ipo': GRN, 'desk95': LINK, 'license': MAG, 'shatter': MAG, 'codetree': AMB, 'donut': LINK, 'end': AMB}.get(kind, AMB if t < 23.95 else LINK if t < 30.95 else GRN if t < 37.5 else MAG)
    return AMB

# ---------------- assets ----------------
_cache = {}
def img(path, mode='RGB'):
    k = (path, mode)
    if k not in _cache:
        if len(_cache) > 300: _cache.clear()
        _cache[k] = Image.open(path).convert(mode)
    return _cache[k]

rng = np.random.default_rng(11)
STARS = [(rng.uniform(0, W), rng.uniform(0, H*1.3), rng.uniform(.6, 2.2), rng.uniform(.25, .9)) for _ in range(300)]
def background(t, c=None):
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im, 'RGBA')
    off = (t*14) % 90
    for x in range(-90, W+90, 90): d.line([(x+off*0.3, 0), (x+off*0.3, H)], fill=(57, 213, 255, 13), width=1)
    for y in range(-90, H+90, 90): d.line([(0, y+off), (W, y+off)], fill=(57, 213, 255, 13), width=1)
    for x, y, r, a in STARS:
        yy = (y - t*9*r) % (H*1.3) - H*0.15
        d.ellipse([x-r, yy-r, x+r, yy+r], fill=(200, 230, 255, int(150*a)))
    c = c or section_colour(t)
    glow = Image.new('L', (W//8, H//8), 0)
    gd = ImageDraw.Draw(glow); gd.ellipse([W//8*0.1, H//8*0.28, W//8*0.9, H//8*0.66], fill=60)
    glow = glow.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR)
    return Image.composite(Image.new('RGB', (W, H), c), im, glow.point(lambda v: v*0.45))

_VG = None
def VIGN():
    global _VG
    if _VG is None:
        v = Image.new('L', (W//4, H//4), 0); ImageDraw.Draw(v).ellipse([-W//4*0.3, -H//4*0.1, W//4*1.3, H//4*1.1], fill=255)
        _VG = v.filter(ImageFilter.GaussianBlur(30)).resize((W, H), Image.BILINEAR)
    return _VG
def vig(base, k=0.75):
    return Image.composite(base, Image.new('RGB', (W, H), INK), VIGN().point(lambda v: int(255-(255-v)*k)))

def grade(im):
    # cool, slightly contrasty grade so archive photos sit in the palette
    im = ImageOps.autocontrast(im, cutoff=1)
    r, g, b = im.split()
    r = r.point(lambda v: int(v*0.96)); b = b.point(lambda v: min(255, int(v*1.06+6)))
    return Image.merge('RGB', (r, g, b))

def cover_fit(src, w, h):
    s = max(w/src.width, h/src.height)
    return src.resize((max(w, int(src.width*s+0.5)), max(h, int(src.height*s+0.5))), Image.LANCZOS)

def kb(src, t, t0, t1, z0=1.0, z1=1.08, dx=0, dy=0):
    u = ease((t-t0)/max(.01, t1-t0)); z = z0+(z1-z0)*u
    sw, sh = src.size
    s = max(W/sw, H/sh)*z
    cx, cy = sw/2 - dx*u/s, sh/2 - dy*u/s
    a = 1/s
    return src.transform((W, H), Image.AFFINE, (a, 0, cx - a*W/2, 0, a, cy - a*H/2), resample=Image.BICUBIC)

_graded = {}
def photo_src(name):
    if name not in _graded:
        _graded[name] = grade(img(f'{ROOT}/foot/{name}.jpg'))
    return _graded[name]

def framed_photo(t, t0, t1, name, z0, z1, dx, dy):
    # sharp photo window over a blurred, darkened copy of itself (no stretching of wide photos)
    src = photo_src(name)
    bg = kb(src, t, t0, t1, 1.0, 1.05).resize((W//8, H//8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
    bg = Image.blend(bg, Image.new('RGB', (W, H), INK), 0.55)
    ww, hh = 960, 1040
    u = ease((t-t0)/max(.01, t1-t0)); z = z0+(z1-z0)*u
    sw, sh = src.size
    s = max(ww/sw, hh/sh)*z
    cx, cy = sw/2 - dx*u/s, sh/2 - dy*u/s
    a = 1/s
    win = src.transform((ww, hh), Image.AFFINE, (a, 0, cx - a*ww/2, 0, a, cy - a*hh/2), resample=Image.BICUBIC)
    pop = eback((t-t0)/0.25, 1.2)
    sc = 0.94 + 0.06*pop
    win = win.resize((int(ww*sc), int(hh*sc)), Image.BICUBIC)
    x, y = (W - win.width)//2, 740 - win.height//2 + 40
    sh_ = Image.new('L', (W, H), 0); ImageDraw.Draw(sh_).rounded_rectangle([x+10, y+18, x+win.width+10, y+win.height+18], 30, fill=170)
    bg = Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), bg, sh_.filter(ImageFilter.GaussianBlur(18)))
    m = rounded_mask(win.width, win.height, 30)
    bg.paste(win, (x, y), m)
    d = ImageDraw.Draw(bg, 'RGBA')
    d.rounded_rectangle([x-3, y-3, x+win.width+3, y+win.height+3], 32, outline=(*section_colour(t), 200), width=4)
    return bg

_vid = {}
def vframe(name, t, t0):
    start, speed = FOOT[name]
    i = int((t - t0)*FPS*speed) + 1
    d = f'{ROOT}/b/shots/{name}'
    n = len(os.listdir(d))
    return img(f'{d}/f{max(1, min(i, n)):04d}.jpg')

def layer3d(name, t):
    i = int(round((t - L3D_T0[name]) * FPS)) + 1
    d = f"{ROOT}/l3d/{name}"
    n = len(os.listdir(d))
    return img(f"{d}/f{max(1, min(i, n)):04d}.png", 'RGBA')

def add_glow(base, lay, strength=1.0, radius=16, dx=0, dy=0, scale=1.0):
    if scale != 1.0:
        lay = lay.resize((int(W*scale), int(H*scale)), Image.BICUBIC)
    if dx or dy or scale != 1.0:
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh.paste(lay, (int((W-lay.width)/2+dx), int((H-lay.height)/2+dy)), lay); lay = sh
    a = lay.split()[3]
    rgb = Image.composite(lay.convert('RGB'), Image.new('RGB', (W, H), (0, 0, 0)), a)
    g = rgb.resize((W//4, H//4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius/4)).resize((W, H), Image.BILINEAR)
    if strength != 1: g = g.point(lambda v: min(255, int(v*strength)))
    base = ImageChops.add(base, g)
    base.paste(lay, (0, 0), lay)
    return base

def rounded_mask(w, h, r):
    m = Image.new('L', (w*2, h*2), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w*2-1, h*2-1], r*2, fill=255)
    return m.resize((w, h), Image.LANCZOS)

# ---- avatar ----
AVD = ROOT + '/av/fr'
AV_SEG = {'A': (0.0, 0.0), 'B': (50.5, 5.6)}   # (timeline start, clip start)
AVN = None
def av_frame(t):
    global AVN
    if AVN is None: AVN = len(os.listdir(AVD))
    seg = 'B' if t >= 30 else 'A'
    ts, cs = AV_SEG[seg]
    i = int(round((t - ts + cs + LAG) * FPS)) + 1
    return img(f"{AVD}/f{max(1, min(i, AVN)):04d}.jpg")

FACE = (400, 470)  # face centre in the 720x1280 avatar frame
AVW = 714
def avatar_rect(base, t, rect, src_w, radius, border=True, alpha=1.0, col=None):
    x, y, w, h = [int(round(v)) for v in rect]
    fr = av_frame(t)
    sw = src_w; sh = sw*h/w
    cx, cy = FACE
    box = (cx-sw/2, cy-sh/2, cx+sw/2, cy+sh/2)
    crop = fr.transform((w, h), Image.EXTENT, box, resample=Image.BICUBIC)
    m = rounded_mask(w, h, max(1, int(radius)))
    if alpha < 1: m = m.point(lambda v: int(v*alpha))
    if border:
        gl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
        gd.rounded_rectangle([x-6, y-6, x+w+6, y+h+6], radius+6, outline=(*(col or section_colour(t)), int(210*alpha)), width=4)
        base = add_glow(base, gl, 1.2, 22)
    base.paste(crop, (x, y), m)
    return base

def browser_frame(w, h, col, title='', alpha=255, bar=46):
    # outline of a browser window: title bar with three dots + address pill
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w-1, h-1], 26, outline=(*col, alpha), width=4)
    d.rounded_rectangle([0, 0, w-1, bar], 26, fill=(*INK, int(alpha*0.85)))
    d.line([(0, bar), (w, bar)], fill=(*col, alpha), width=3)
    for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        d.ellipse([22+i*30-8, bar//2-8, 22+i*30+8, bar//2+8], fill=(*c, alpha))
    if w < 220: return im
    d.rounded_rectangle([120, 10, w-24, bar-10], 14, fill=(255, 255, 255, int(alpha*0.12)))
    if title: d.text((140, bar//2), title, font=M(22, 600), fill=(*WHITE, alpha), anchor='lm')
    return im

# ---- text helpers ----
def text_layer(txt, font, fill, stroke=0, stroke_fill=INK):
    bb = font.getbbox(txt, stroke_width=stroke)
    w, h = bb[2]-bb[0]+8, bb[3]-bb[1]+8
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((-bb[0]+4, -bb[1]+4), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

FIT = []
def place(base, lay, cx, cy, scale=1.0, alpha=1.0, glow=None, glow_r=18, check=True, rot=0):
    if rot: lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    if scale != 1.0:
        lay = lay.resize((max(1, int(lay.width*scale)), max(1, int(lay.height*scale))), Image.BICUBIC)
    if alpha < 1:
        a = lay.split()[3].point(lambda v: int(v*alpha)); lay = lay.copy(); lay.putalpha(a)
    x, y = int(cx - lay.width/2), int(cy - lay.height/2)
    if check: FIT.append((x, y, x+lay.width, y+lay.height))
    if glow:
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        col = Image.new('RGBA', lay.size, (*glow, 255)); col.putalpha(lay.split()[3].point(lambda v: int(v*.8)))
        g.paste(col, (x, y), col)
        gg = g.filter(ImageFilter.GaussianBlur(glow_r))
        base = Image.alpha_composite(base.convert('RGBA'), gg).convert('RGB')
    base.paste(lay, (x, y), lay)
    return base

def cap_y(t):
    if t < 5.6: return 1478
    if t >= 50.55: return 1478
    if 7.55 <= t < 12.0 or 13.25 <= t < 16.65: return 1505
    return 1440

def caption(base, t):
    cur = None
    for k, (t0, txt, kw) in enumerate(CAP):
        t1 = CAP[k+1][0] if k+1 < len(CAP) else TOT
        if t0 <= t < t1: cur = (t0, txt, kw)
    if not cur: return base
    t0, txt, kw = cur
    size = 70
    words = txt.split(' ')
    while True:
        f = U(8, size)
        parts = [text_layer(w, f, CAPK if w in kw else WHITE, stroke=6, stroke_fill=(5, 6, 10)) for w in words]
        sp = int(size*0.22)
        tw = sum(p.width for p in parts) + sp*(len(parts)-1)
        if tw <= 860 or size <= 48: break
        size -= 2
    lines = [parts]
    if tw > 860:
        half = (len(parts)+1)//2; lines = [parts[:half], parts[half:]]
    lh = int(size*1.32)
    canvas = Image.new('RGBA', (900, lh*len(lines)+16), (0, 0, 0, 0))
    for li, ln in enumerate(lines):
        lw = sum(p.width for p in ln) + sp*(len(ln)-1); x = (900-lw)//2
        for p in ln:
            canvas.paste(p, (x, li*lh + (lh - p.height)//2 + 8), p); x += p.width+sp
    u = eout((t-t0)/0.16)
    return place(base, canvas, 540, cap_y(t), scale=0.9+0.1*u, alpha=u, glow=(0, 0, 0), glow_r=14)

def tags(base, t):
    for t0, t1, txt, col in TAGS:
        if t0 <= t < t1:
            u = eback((t-t0)/0.24, 1.2); a = clamp((t-t0)/0.12)*clamp((t1-t)/0.12)
            hk = t < 5.6
            y = 455
            base = place(base, text_layer(txt, U(9, 120 if hk else 150), COL[col]), 540 if not hk else 790, y if not hk else 430,
                         scale=1.25-0.25*u, alpha=a, glow=COL[col], glow_r=26)
    return base

def chip_layer(txt, col):
    f = M(32, 700)
    bb = f.getbbox(txt)
    tw, th = bb[2]-bb[0], f.getbbox('ЁЙgy')[3]-f.getbbox('ЁЙgy')[1]
    w, h = tw+2*30, th+2*24
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 1, w-2, h-2], h//2, fill=(*INK, 210), outline=(*col, 255), width=3)
    d.text((30-bb[0], (h-th)//2 - f.getbbox('ЁЙgy')[1]), txt, font=f, fill=col)
    return im

def chips(base, t):
    for t0, t1, txt, col, y in CHIPS:
        if t0 <= t < t1:
            u = eout((t-t0)/0.22); a = u*clamp((t1-t)/0.12)
            base = place(base, chip_layer(txt, COL[col]), 540, y + 30*(1-u), alpha=a, glow=COL[col], glow_r=12)
    return base

def names(base, t):
    for t0, t1, nm, sub in NAMES:
        if t0 <= t < t1:
            u = eout((t-t0)/0.3); a = u*clamp((t1-t)/0.12)
            c = section_colour(t)
            f1, f2 = U(8, 52), M(28, 600)
            b1, b2 = f1.getbbox(nm), f2.getbbox(sub)
            w = max(b1[2], b2[2]) + 70; h = 150
            im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle([0, 0, w-1, h-1], 22, fill=(*INK, 225))
            d.rectangle([0, 18, 8, h-18], fill=(*c, 255))
            d.text((36, 22-b1[1]), nm, font=f1, fill=WHITE)
            d.text((36, 98-b2[1]), sub, font=f2, fill=c)
            base = place(base, im, 120 + w/2 - 40*(1-u), 1130, alpha=a)
    return base

def stamps(base, t):
    for t0, t1, txt, col in STAMPS:
        if t0 <= t < t1:
            c = COL[col]; f = U(9, 84)
            bb = f.getbbox(txt); w, h = bb[2]-bb[0]+80, bb[3]-bb[1]+64
            im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle([3, 3, w-4, h-4], 16, outline=c, width=9)
            d.rounded_rectangle([16, 16, w-17, h-17], 9, outline=c, width=3)
            d.text((40-bb[0], 32-bb[1]), txt, font=f, fill=c)
            u = clamp((t-t0)/0.22)
            base = place(base, im, 540, 1060, scale=1.35-0.35*eout(u), alpha=clamp(u*3), glow=c, glow_r=14, rot=-6)
    return base

def srcline(base, t):
    for t0, t1, txt in SRC:
        if t0 <= t < t1:
            d = ImageDraw.Draw(base, 'RGBA')
            d.text((540, 1592), txt, font=M(22, 500), fill=(220, 225, 240, 150), anchor='mm')
    return base

def hud(base, t):
    d = ImageDraw.Draw(base, 'RGBA')
    y = 300; c = section_colour(t)
    d.text((120, y), 'MB', font=U(9, 34), fill=WHITE, anchor='lm')
    d.text((212, y+2), 'БРАУЗЕР', font=M(24, 500), fill=(200, 205, 230, 170), anchor='lm')
    d.text((960, y+2), f"00:{t:04.1f}", font=M(26, 600), fill=(220, 225, 245, 230), anchor='rm')
    d.line([(120, y+34), (960, y+34)], fill=(255, 255, 255, 40), width=2)
    d.line([(120, y+34), (120 + 840*t/TOT, y+34)], fill=(*c, 230), width=3)
    return base

# =================== scenes ===================
# ---------- HOOK: crash-zoom through the web -> it collapses into one NeXT cube; avatar with browser-window echoes ----------
def window_tunnel(t, strength=1.0):
    base = Image.new('RGB', (W, H), INK); d = ImageDraw.Draw(base, 'RGBA')
    for k in range(14):
        ph = (k/14 + t*0.55) % 1.0
        s = 0.06 + ph**2.2*2.4
        w, h = 900*s, 1200*s
        a = int(150*strength*min(1, ph*3)*(1-ph)**0.5)
        cx, cy = 540 + math.sin(t*0.8+k)*30*s, 900
        col = [LINK, AMB, GRN, MAG][k % 4]
        d.rounded_rectangle([cx-w/2, cy-h/2, cx+w/2, cy+h/2], max(4, 40*s), outline=(*col, a), width=max(1, int(5*s)))
        bar = 60*s
        d.line([(cx-w/2, cy-h/2+bar), (cx+w/2, cy-h/2+bar)], fill=(*col, a), width=max(1, int(3*s)))
        for i in range(3): d.ellipse([cx-w/2+(28+i*34)*s-7*s, cy-h/2+bar/2-7*s, cx-w/2+(28+i*34)*s+7*s, cy-h/2+bar/2+7*s], fill=(*col, a))
    return base.filter(ImageFilter.GaussianBlur(0.6))

def hook(t):
    base = window_tunnel(t, 1.0 if t > 0.4 else 0.5)
    # 3D web globe -> NeXT cube; layer moves up above the card after the collapse
    lay = layer3d('hook', t)
    mv = ease((t-2.3)/0.6)
    base = add_glow(base, lay, 1.3, 20, dy=-430*mv, scale=1.0-0.55*mv)
    if t < 0.36:
        return base
    base = vig(base, 0.6)
    # card with the face, never covered by text
    cw, ch = 640-120*mv, 820-180*mv
    cx, cy = 540, 980 + 140*mv
    pop = eback((t-0.36)/0.32, 1.3)
    w, h = cw*(0.6+0.4*pop), ch*(0.6+0.4*pop)
    # echoes: the same Markus in other browser windows, cascading out and snapping back
    amp = max(0.0, 1-(t-0.36)/0.6)**2 + 0.8*max(0.0, 1-abs(t-1.05)/0.35)**2 + 0.7*max(0.0, 1-abs(t-4.66)/0.3)**2
    if amp > 0.02:
        for j, col in enumerate([LINK, AMB, GRN, MAG]):
            k = j+1
            ox, oy = (-1)**j*70*k*amp, -60*k*amp
            e = Image.new('RGB', (W, H), (0, 0, 0))
            e = avatar_rect(e, t - 0.04*k, (cx-w/2+ox, cy-h/2+oy, w, h), 440, 30, border=False)
            g = e.convert('L').point(lambda v: min(255, int(v*2.2)))
            tint = Image.composite(Image.new('RGB', (W, H), col), Image.new('RGB', (W, H), (0, 0, 0)), g)
            fr = browser_frame(int(w), int(h), col, alpha=int(255*min(1, amp)))
            tint.paste(fr, (int(cx-w/2+ox), int(cy-h/2+oy)), fr)
            base = ImageChops.screen(base, tint.point(lambda v: int(v*min(1.0, 0.4+amp*0.7))))
    base = avatar_rect(base, t, (cx-w/2, cy-h/2, w, h), 440, 30, col=AMB)
    fr = browser_frame(int(w)+12, 52, AMB, 'info.cern.ch' if t > 2.3 else 'web.1990')
    base.paste(fr, (int(cx-w/2-6), int(cy-h/2-58)), fr)
    if t < 0.52:
        base = Image.blend(base, Image.new('RGB', (W, H), WHITE), 0.8*(1-(t-0.36)/0.16))
    if 2.30 <= t < 2.42:
        base = Image.blend(base, Image.new('RGB', (W, H), WHITE), 0.5*(1-(t-2.30)/0.12))
    # "НЕ ВЫКЛЮЧАТЬ!" note slapped next to the cube (never over the face)
    if t >= 4.64:
        u = clamp((t-4.64)/0.2)
        f = CV(96)
        txt = 'НЕ ВЫКЛЮЧАТЬ!'
        bb = f.getbbox(txt)
        im = Image.new('RGBA', (bb[2]-bb[0]+70, bb[3]-bb[1]+60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, im.width-1, im.height-1], fill=(244, 239, 226, 245))
        d.text((35-bb[0], 30-bb[1]), txt, font=f, fill=(200, 16, 46))
        base = place(base, im, 540, 590, scale=1.6-0.6*eout(u), alpha=clamp(u*3), rot=-5, glow=(0, 0, 0), glow_r=20)
    return base

# ---------- click: typing footage + click ripple ----------
def click(t, t0, t1):
    fr = vframe('nv01', t, t0)
    base = kb(fr, t, t0, t1, 1.0, 1.12, 0, 0)
    base = Image.blend(base, Image.new('RGB', (W, H), INK), 0.3)
    base = vig(base, 0.7)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # floating link card in the middle
    u = eback((t-5.75)/0.35, 1.3)
    if u > 0:
        cw, ch = int(760*u), int(150*u)
        if cw > 10:
            x, y = 540-cw//2, 760-ch//2
            d.rounded_rectangle([x, y, x+cw, y+ch], 30, fill=(*INK, 225), outline=(*LINK, 255), width=4)
            if u > 0.8:
                d.text((540, 760), 'example.com/браузер', font=M(44, 700), fill=LINK, anchor='mm')
                d.line([(250, 792), (830, 792)], fill=LINK, width=3)
    tc = 6.99
    if t >= tc:
        q = t-tc
        for k in range(3):
            r = 30 + (q-k*0.12)*700
            if r > 30: d.ellipse([700-r, 800-r, 700+r, 800+r], outline=(*LINK, int(255*clamp(1-(q-k*0.12)/0.6))), width=6)
    # cursor
    cx, cy = 700 + 200*(1-ease((t-5.9)/0.9)), 800 + 300*(1-ease((t-5.9)/0.9))
    sc = 0.85 if 6.99 <= t < 7.12 else 1.0
    pts = [(0, 0), (0, 64), (16, 50), (28, 76), (40, 70), (28, 46), (50, 46)]
    d.polygon([(cx+x*sc*1.3, cy+y*sc*1.3) for x, y in pts], fill=WHITE, outline=INK)
    return add_glow(base, lay, 1.0, 14)

# ---------- pipe: the 3D page-load diagram ----------
def pipe(t):
    base = background(t, LINK)
    return add_glow(base, layer3d('pipe', t), 1.1, 16, dy=0, scale=0.72)

# ---------- proposal: recreated cover + Sendall's handwritten note ----------
def proposal(t, t0):
    base = background(t, AMB)
    u = eout((t-t0)/0.4)
    pw, ph = 760, 980
    paper = Image.new('RGBA', (pw, ph), (240, 236, 226, 255)); d = ImageDraw.Draw(paper)
    srng = np.random.default_rng(5)
    noise = Image.fromarray((srng.normal(0, 5, (ph, pw))+128).clip(0, 255).astype(np.uint8)).convert('L')
    paper = Image.composite(paper, Image.new('RGBA', (pw, ph), (225, 220, 208, 255)), noise.point(lambda v: 255 if v > 120 else 200))
    d = ImageDraw.Draw(paper)
    ft = ImageFont.truetype(SERIF, 46); fs = ImageFont.truetype(SANSR, 26)
    d.text((pw//2, 330), 'Information Management:', font=ft, fill=(30, 28, 34), anchor='mm')
    d.text((pw//2, 390), 'A Proposal', font=ft, fill=(30, 28, 34), anchor='mm')
    d.text((pw//2, 470), 'Tim Berners-Lee, CERN', font=fs, fill=(60, 58, 64), anchor='mm')
    d.text((pw//2, 510), 'March 1989', font=fs, fill=(60, 58, 64), anchor='mm')
    # mind-map sketch
    for (x, y, w_) in [(130, 640, 180), (420, 610, 200), (260, 760, 200), (500, 790, 170), (150, 880, 160)]:
        d.ellipse([x, y, x+w_, y+70], outline=(60, 58, 64), width=2)
    for a_, b_ in [((220, 675), (420, 645)), ((360, 760), (300, 710)), ((560, 680), (580, 790)), ((230, 880), (300, 830))]:
        d.line([a_, b_], fill=(60, 58, 64), width=2)
    # handwriting write-on
    hw = 'Vague but exciting...'
    k = clamp((t-21.45)/1.2)
    n = int(len(hw)*k)
    fh = CV(68)
    d.text((70, 180), hw[:n], font=fh, fill=(28, 52, 160))
    if k >= 1:
        d.line([(70, 200+40), (70+fh.getlength(hw), 245)], fill=(28, 52, 160), width=3)
    paper = paper.rotate(-3 + 3*u, expand=True, resample=Image.BICUBIC)
    base = place(base, paper, 540, 790 + 80*(1-u), scale=0.82 + 0.06*u, alpha=clamp(u*2), glow=(0, 0, 0), glow_r=30, check=False)
    return base

# ---------- Mosaic: real screenshot, then inline images "explode" into the text ----------
def retro_window(w, h, title, body_fn=None):
    im = Image.new('RGB', (w, h), RETRO); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w-1, h-1], outline=(255, 255, 255)); d.rectangle([1, 1, w-2, h-2], outline=(128, 128, 128))
    d.rectangle([4, 4, w-5, 40], fill=(0, 0, 128))
    d.text((14, 22), title, font=ImageFont.truetype(SANS, 24), fill=WHITE, anchor='lm')
    for i in range(3): d.rectangle([w-36-i*32, 9, w-12-i*32, 35], fill=RETRO, outline=(40, 40, 40))
    d.rectangle([10, 50, w-11, 86], fill=WHITE, outline=(100, 100, 100))
    d.text((18, 68), 'URL: http://www.ncsa.uiuc.edu/', font=ImageFont.truetype(SANSR, 20), fill=(20, 20, 20), anchor='lm')
    d.rectangle([10, 96, w-11, h-11], fill=WHITE, outline=(100, 100, 100))
    return im

def mosaic_real(t, t0, t1):
    src = photo_src('c48') if False else img(f'{ROOT}/foot/c48.jpg')
    base = background(t, LINK)
    u = eback((t-t0)/0.3, 1.2)
    s = 800/src.width*(0.9+0.1*u)*(1+0.06*ease((t-t0)/(t1-t0)))
    im = src.resize((int(src.width*s), int(src.height*s)), Image.LANCZOS)
    base = place(base, im.convert('RGBA'), 540, 905, check=False, glow=LINK, glow_r=26)
    if t < t0+0.14:
        base = Image.blend(base, Image.new('RGB', (W, H), WHITE), 0.7*(1-(t-t0)/0.14))
    return base

def mosaic_pop(t, t0):
    base = background(t, LINK)
    w, h = 900, 980
    win = retro_window(w, h, 'NCSA Mosaic: Document View')
    d = ImageDraw.Draw(win)
    fb = ImageFont.truetype(SERIF, 40); fr_ = ImageFont.truetype(SANSR, 24)
    d.text((40, 130), 'Welcome to the Web!', font=fb, fill=(10, 10, 10))
    lines_y = [200, 240, 280, 560, 600, 640, 680, 900]
    for i, y in enumerate(lines_y):
        d.rectangle([40, y, 40 + [800, 760, 520, 300, 300, 260, 300, 700][i], y+16], fill=(150, 150, 160))
    d.text((40, 320), 'link: hypertext', font=fr_, fill=(0, 0, 238)); d.line([(40, 348), (205, 348)], fill=(0, 0, 238), width=2)
    # inline images pop in (first one on "картинки")
    pops = [(26.16, 'c98', (40, 380, 430, 540)), (26.66, 'c15', (480, 380, 860, 540)), (27.0, 'c9', (380, 560, 860, 860))]
    for tp, nm, (x0, y0, x1, y1) in pops:
        q = t - tp
        if q < 0: continue
        sc = eback(q/0.28, 1.8)
        pw, ph = int((x1-x0)*sc), int((y1-y0)*sc)
        if pw < 4 or ph < 4: continue
        p = cover_fit(photo_src(nm), x1-x0, y1-y0).crop((0, 0, x1-x0, y1-y0)).resize((pw, ph), Image.BICUBIC)
        win.paste(p, (int((x0+x1)/2-pw/2), int((y0+y1)/2-ph/2)))
    u = eback((t-t0)/0.3, 1.2)
    if t < t0+0.14: base = Image.blend(base, Image.new('RGB', (W, H), WHITE), 0.7*(1-(t-t0)/0.14))
    base = place(base, win.convert('RGBA'), 540, 850, scale=0.70+0.1*u, check=False, glow=LINK, glow_r=24)
    # burst particles on each pop
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    for tp, nm, (x0, y0, x1, y1) in pops:
        q = t - tp
        if 0 <= q < 0.6:
            cx = 540 + ((x0+x1)/2 - w/2)*0.8; cy = 850 + ((y0+y1)/2 - h/2)*0.8
            for k in range(26):
                a = k*2.399; r = 40 + q*900*(0.6+0.4*((k*37) % 10)/10)
                al = int(255*(1-q/0.6))
                dd.ellipse([cx+math.cos(a)*r-5, cy+math.sin(a)*r-5, cx+math.cos(a)*r+5, cy+math.sin(a)*r+5], fill=(*[LINK, AMB, WHITE][k % 3], al))
    return add_glow(base, lay, 1.2, 12)

# ---------- IPO chart ----------
IPO = [(0.0, 28.0), (0.12, 28), (0.22, 71), (0.35, 75), (0.5, 66), (0.62, 70), (0.78, 60), (0.9, 61), (1.0, 58.25)]
def ipo(t, t0):
    base = background(t, GRN)
    d = ImageDraw.Draw(base, 'RGBA')
    x0, x1, y0, y1 = 140, 940, 1150, 560   # chart box (y0 bottom)
    def Y(v): return y0 - (v-0)/85*(y0-y1)
    for v in [0, 25, 50, 75]:
        d.line([(x0, Y(v)), (x1, Y(v))], fill=(77, 255, 166, 40), width=2)
        d.text((x0-16, Y(v)), f'${v}', font=M(26, 500), fill=(200, 255, 225, 150), anchor='rm')
    d.text((x0, y0+40), '9 авг 1995, NASDAQ: NSCP', font=M(28, 600), fill=(200, 255, 225, 200), anchor='lm')
    # line draws during 32.3..35.0
    k = clamp((t-32.3)/2.6)
    pts = []
    for i in range(len(IPO)-1):
        a, b = IPO[i], IPO[i+1]
        for s in np.linspace(0, 1, 12):
            u = a[0]+(b[0]-a[0])*s
            if u <= k: pts.append((x0+(x1-x0)*u, Y(a[1]+(b[1]-a[1])*s)))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    if len(pts) > 1:
        poly = pts + [(pts[-1][0], y0), (pts[0][0], y0)]
        dl.polygon(poly, fill=(77, 255, 166, 50))
        dl.line(pts, fill=(*GRN, 255), width=8, joint='curve')
        px, py = pts[-1]
        dl.ellipse([px-14, py-14, px+14, py+14], fill=WHITE)
    # $28 marker
    if t > 31.6:
        dl.text((x0+10, Y(28)-40), 'размещение $28', font=M(28, 700), fill=AMB)
    if k > 0.35:
        dl.text((x0+(x1-x0)*0.35, Y(75)-46), 'пик $75', font=M(30, 700), fill=WHITE, anchor='mm')
    base = add_glow(base, lay, 1.2, 14)
    # big counter: market value
    if t >= 34.7:
        q = ease((t-34.7)/1.0)
        v = 0.1 + 2.8*q
        txt = f'${v:.1f} млрд'.replace('.', ',')
        base = place(base, text_layer(txt, U(9, 120), GRN, stroke=4), 540, 470, scale=1.0+0.15*max(0, 1-(t-35.16)/0.3) if t > 35.16 else 1.0, glow=GRN, glow_r=24)
    elif t >= 31.0:
        base = place(base, text_layer('NETSCAPE', U(9, 110), WHITE), 540, 470, alpha=clamp((t-31.0)/0.2)*clamp((34.7-t)/0.15), glow=GRN, glow_r=20)
    if t >= 36.66:  # stop on "без прибыли": chart desaturates under the stamp
        base = Image.blend(base, base.convert('L').convert('RGB'), 0.5)
    return base

# ---------- Windows 95: Explorer is handed out with the OS ----------
def desk95(t, t0):
    base = Image.new('RGB', (W, H), TEAL95)
    d = ImageDraw.Draw(base)
    # taskbar
    d.rectangle([0, 1720, W, 1920], fill=RETRO); d.line([(0, 1721), (W, 1721)], fill=WHITE, width=3)
    d.rectangle([20, 1740, 220, 1800], fill=RETRO, outline=(40, 40, 40)); d.text((120, 1770), 'Пуск', font=ImageFont.truetype(SANS, 34), fill=(0, 0, 0), anchor='mm')
    # icons
    fi = ImageFont.truetype(SANSR, 24)
    for i, nm in enumerate(['Мой компьютер', 'Корзина', 'Internet Explorer']):
        x, y = 70, 420 + i*190
        d.rectangle([x+30, y, x+110, y+80], fill=[(200, 200, 200), (160, 170, 180), (57, 140, 255)][i], outline=(0, 0, 0))
        d.text((x+70, y+110), nm, font=fi, fill=WHITE, anchor='mm')
    # Explorer windows multiply across the desktop (cascade)
    n = int(clamp((t-39.35)/1.9)*9) + (1 if t >= 39.35 else 0)
    for k in range(n):
        x, y = 260 + k*48, 600 + k*62
        win = retro_window(560, 440, 'Internet Explorer')
        dw = ImageDraw.Draw(win)
        dw.text((40, 160), 'Добро пожаловать', font=ImageFont.truetype(SERIF, 34), fill=(10, 10, 10))
        for j in range(4): dw.rectangle([40, 230+j*40, 480-j*60, 246+j*40], fill=(150, 150, 160))
        base.paste(win, (x, y))
    if t >= 41.30:   # "И знаешь, что смешно?" — the stop before the reveal
        u = ease((t-41.30)/0.5)
        base = Image.blend(base, base.convert('L').convert('RGB'), 0.75*u)
        base = Image.blend(base, Image.new('RGB', (W, H), INK), 0.5*u)
    return base

# ---------- the reveal: Explorer = licensed Mosaic ----------
def license_scene(t, t0):
    base = background(t, MAG)
    if t < t0+0.16:
        base = Image.blend(base, Image.new('RGB', (W, H), WHITE), 0.85*(1-(t-t0)/0.16))
    wA = retro_window(420, 330, 'NCSA Mosaic'); wB = retro_window(420, 330, 'Internet Explorer 1.0')
    for wv, lab in [(wA, 'Mosaic'), (wB, 'Explorer')]:
        dw = ImageDraw.Draw(wv); dw.text((210, 200), lab, font=ImageFont.truetype(SERIF, 52), fill=(10, 10, 10), anchor='mm')
    u = eback((t-t0)/0.35, 1.3)
    base = place(base, wA.convert('RGBA'), 540, 610, scale=0.8+0.2*u, check=False, glow=LINK, glow_r=20)
    v = eback((t-t0-0.5)/0.35, 1.3)
    if t > t0+0.5:
        base = place(base, wB.convert('RGBA'), 540, 1150, scale=0.8+0.2*v, check=False, glow=MAG, glow_r=20)
    # code stream from Mosaic into Explorer
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    q = t - (t0+0.3)
    if q > 0:
        for k in range(18):
            ph = (k/18 + q*0.9) % 1.0
            y = 790 + ph*190; x = 540 + math.sin(k*1.7+q*3)*60
            d.text((x, y), ['{', '}', '<a>', '01', 'img', '#'][k % 6], font=M(30, 700), fill=(*GRN, int(255*math.sin(ph*math.pi))), anchor='mm')
    base = add_glow(base, lay, 1.3, 12)
    if t >= 43.65:
        base = place(base, chip_layer('лицензия Spyglass на код Mosaic', MAG), 540, 880, alpha=eout((t-43.65)/0.2), glow=MAG, glow_r=12)
    return base

# ---------- Netscape shatters ----------
SHARDS = None
def shatter(t, t0):
    global SHARDS
    base = background(t, MAG)
    src = photo_src('c63')
    w = 900; h = int(src.height*w/src.width)
    im = src.resize((w, h), Image.LANCZOS)
    x0, y0 = 90, 820 - h//2
    q = t - (t0+0.35)
    if q <= 0:
        base.paste(im, (x0, y0))
        d = ImageDraw.Draw(base, 'RGBA'); d.rectangle([x0-3, y0-3, x0+w+3, y0+h+3], outline=(*MAG, 200), width=4)
        if t > t0+0.2:  # crack lines
            for k in range(7):
                a = k*0.9+0.3
                d.line([(540, 820), (540+math.cos(a)*600, 820+math.sin(a)*400)], fill=(255, 255, 255, 230), width=3)
        return base
    if SHARDS is None:
        r = np.random.default_rng(3); SHARDS = []
        for gx in range(6):
            for gy in range(5):
                SHARDS.append((gx*w//6, gy*h//5, w//6, h//5, r.uniform(-1, 1), r.uniform(-1.4, 0.2), r.uniform(-40, 40)))
    for sx, sy, sw, sh, vx, vy, rot in SHARDS:
        p = im.crop((sx, sy, sx+sw, sy+sh)).convert('RGBA')
        p = p.rotate(rot*q, expand=True, resample=Image.BICUBIC)
        X = x0 + sx + vx*700*q - (p.width-sw)/2
        Y = y0 + sy + vy*600*q + 1400*q*q - (p.height-sh)/2
        a = clamp(1-q/0.8)
        if a > 0:
            al = p.split()[3].point(lambda v: int(v*a)); p.putalpha(al)
            base.paste(p, (int(X), int(Y)), p)
    return base

# ---------- code tree: from the open Netscape code a tree (Mozilla -> Firefox) grows ----------
def codetree(t, t0):
    base = background(t, AMB)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # falling code rain
    for k in range(40):
        x = 60 + (k*97) % 960
        y = ((k*173 + (t-t0)*500) % 1300) + 380
        d.text((x, y), ['</>', '{ }', '0x', 'js', 'css', '<p>'][k % 6], font=M(28, 600), fill=(*GRN, 90))
    # tree: trunk + branches drawn progressively
    g = ease((t-t0)/1.3)
    nodes = [((540, 1200), (540, 980), '1998: код открыт', LINK), ((540, 980), (330, 800), 'Mozilla', AMB), ((540, 980), (760, 760), 'Firefox · 2004', AMB)]
    for i, (a, b, lab, c) in enumerate(nodes):
        u = clamp(g*3 - i)
        if u <= 0: continue
        bx, by = a[0]+(b[0]-a[0])*u, a[1]+(b[1]-a[1])*u
        d.line([a, (bx, by)], fill=(*c, 255), width=10)
        if u >= 1:
            d.ellipse([b[0]-18, b[1]-18, b[0]+18, b[1]+18], fill=(*c, 255))
            f = M(34, 700); tw = f.getlength(lab)
            lx = min(max(b[0] + (230 if i == 0 else 0), 130 + tw/2), 950 - tw/2)
            d.text((lx, b[1]-50 + (50 if i == 0 else 0)), lab, font=f, fill=c, anchor='mm')
    d.text((540, 1250), 'Netscape', font=U(8, 48), fill=(*WHITE, 230), anchor='mm')
    return add_glow(base, lay, 1.2, 14)

# ---------- donut: Chrome share ----------
def donut(t):
    base = background(t, LINK)
    base = add_glow(base, layer3d('donut', t), 1.1, 16, dy=20)
    q = ease((t-48.3)/1.0)
    v = 68.8*q
    base = place(base, text_layer(f'{v:.1f}%'.replace('.', ','), U(9, 140), LINK, stroke=4), 540, 520, glow=LINK, glow_r=24)
    if t > 49.87:
        base = place(base, text_layer('Chrome', U(8, 64), WHITE), 540, 1215, alpha=clamp((t-49.87)/0.15))
    return base

# ---------- ending: avatar over modem LEDs, subscribe bar loads instantly ----------
def ending(t, t0):
    base = vig(window_tunnel(t, 0.7), 0.6)
    u = eback((t-t0)/0.4, 1.1)
    w, h = 620*u, 700*u
    if w > 4:
        base = avatar_rect(base, t, (540-w/2, 820-h/2, w, h), 520, 30, alpha=clamp((t-t0)/0.15), col=AMB)
        fr_ = browser_frame(int(w)+12, 52, AMB, 'подписка')
        base.paste(fr_, (int(540-w/2-6), int(820-h/2-58)), fr_)
    # modem handshake visual on "звук модема"
    if 53.03 <= t < 53.9:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for k in range(60):
            x = 140 + k*13.3
            a = abs(math.sin(k*0.7 + t*40))*90*(1-abs((t-53.45)/0.45))
            d.line([(x, 1270-a), (x, 1270+a)], fill=(*GRN, 220), width=6)
        base = add_glow(base, lay, 1.2, 10)
    # subscribe bar
    if t >= 54.05:
        q = ease((t-54.05)/0.55)
        d = ImageDraw.Draw(base, 'RGBA')
        d.rounded_rectangle([190, 1240, 890, 1300], 30, fill=(*INK, 220), outline=(*AMB, 255), width=4)
        d.rounded_rectangle([196, 1246, 196+688*q, 1294], 26, fill=(*AMB, 255))
        d.text((540, 1270), f'подписка {int(100*q)}%', font=M(32, 800), fill=WHITE if q < 0.55 else INK, anchor='mm')
    return base

def frame(fi):
    t = fi / FPS
    shot = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1])
    t0, t1, kind, arg = shot
    FIT.clear()
    if kind == 'hook': base = hook(t)
    elif kind == 'click': base = click(t, t0, t1)
    elif kind == 'pipe': base = pipe(t)
    elif kind == 'photo': base = framed_photo(t, t0, t1, *arg)
    elif kind == 'proposal': base = proposal(t, t0)
    elif kind == 'mosaic_real': base = mosaic_real(t, t0, t1)
    elif kind == 'mosaic_pop': base = mosaic_pop(t, t0)
    elif kind == 'ipo': base = ipo(t, t0)
    elif kind == 'desk95': base = desk95(t, t0)
    elif kind == 'license': base = license_scene(t, t0)
    elif kind == 'shatter': base = shatter(t, t0)
    elif kind == 'codetree': base = codetree(t, t0)
    elif kind == 'donut': base = donut(t)
    else: base = ending(t, t0)
    base = tags(base, t)
    base = chips(base, t)
    base = names(base, t)
    base = stamps(base, t)
    base = caption(base, t)
    base = srcline(base, t)
    base = hud(base, t)
    for (x0, y0, x1, y1) in FIT:
        if x0 < 60 or x1 > W-60 or y0 < 200 or y1 > 1560:
            open('fit_fail.log', 'a').write(f'TEXT-FIT FAIL frame {fi} t={t:.2f} box {(x0, y0, x1, y1)}\n')
    return base

def render_chunk(args):
    a, b, path = args
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'ffv1', '-level', '3', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    for fi in range(a, b):
        p.stdin.write(frame(fi).tobytes())
    p.stdin.close(); p.wait()
    return path

if __name__ == '__main__':
    out = sys.argv[1]
    if len(sys.argv) > 2:
        ts = [float(x) for x in sys.argv[2].split(',')]
        ims = [frame(int(round(t*FPS))).resize((270, 480)) for t in ts]
        cols = min(8, len(ims)); rows = (len(ims)+cols-1)//cols
        S = Image.new('RGB', (270*cols, 480*rows))
        for i, im in enumerate(ims): S.paste(im, ((i % cols)*270, (i//cols)*480))
        S.save(out); sys.exit()
    N = int(round(TOT*FPS)); K = 4
    edges = [N*i//K for i in range(K+1)]
    parts = [(edges[i], edges[i+1], f'{out}.p{i}.mkv') for i in range(K)]
    with Pool(K) as pool: res = pool.map(render_chunk, parts)
    with open(out + '.txt', 'w') as f:
        for r in res: f.write(f"file '{os.path.abspath(r)}'\n")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', out+'.txt', '-c', 'copy', out], check=True)
    print('done', N)
