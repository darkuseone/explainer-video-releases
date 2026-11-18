# dim10 renderer: composites footage, Three.js layers (l3d/), avatar, HUD and captions.
# usage: python r.py out.mkv            -> full render (FFV1)
#        python r.py sheet.jpg t1,t2,... -> contact sheet of given times
import os, sys, math, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from multiprocessing import Pool

W, H, FPS = 1080, 1920, 25
ROOT = os.path.dirname(os.path.abspath(__file__)) + '/..'
TOT = 58.22
LAG = 0.023

# ---- palette: every dimension has its own colour ----
INK = (10, 13, 26)
D0 = (243, 245, 255)   # 0D point / text
D1 = (63, 210, 255)    # 1D line
D2 = (138, 123, 255)   # 2D plane
D3 = (255, 178, 62)    # 3D volume
D4 = (255, 79, 163)    # 4D
T = (124, 240, 255)    # time
D5 = (185, 140, 255)   # 5D+ / hidden dimensions
DIM = {'d0': D0, 'd1': D1, 'd2': D2, 'd3': D3, 'd4': D4, 't': T, 'd5': D5}

FD = ROOT + '/fonts/package/'
def U(w, s): return ImageFont.truetype(FD + {9: '900Black/Unbounded_900Black.ttf', 8: '800ExtraBold/Unbounded_800ExtraBold.ttf', 7: '700Bold/Unbounded_700Bold.ttf', 5: '500Medium/Unbounded_500Medium.ttf'}[w], s)
MONO = '/home/user/explainer-video-releases/docs/fonts/JetBrainsMono-VariableFont_wght.ttf'
def M(s, wght=700):
    f = ImageFont.truetype(MONO, s)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f

def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 4*x*x*x if x < .5 else 1 - (-2*x+2)**3/2
def eout(x): x = clamp(x); return 1 - (1-x)**3
def eback(x, s=1.4): x = clamp(x); x -= 1; return x*x*((s+1)*x+s)+1

# ---------------- timeline ----------------
# shots: (t0, t1, kind, arg)
SHOTS = [
    (0.00, 3.58, 'avatar_hook', None),
    (3.58, 7.30, '3d', 'retina'),
    (7.30, 22.82, '3d', 'build'),
    (22.82, 25.36, 'foot', 'earth'),
    (25.36, 28.72, '3d', 'spacetime'),
    (28.72, 31.84, 'drops', None),
    (31.84, 35.92, 'foot', 'cosmic1'),
    (35.92, 40.00, 'foot', 'cosmic2'),
    (40.00, 46.12, '3d', 'hose'),
    (46.12, 50.02, '3d', 'cy'),
    (50.02, 52.90, 'foot', 'stars'),
    (52.90, TOT, 'avatar_end', 'buildend'),
]
L3D_T0 = {'retina': 3.58, 'build': 7.30, 'spacetime': 25.36, 'hose': 40.0, 'cy': 46.12, 'buildend': 52.9}
FOOT = json.load(open(ROOT + '/b/foot.json')) if os.path.exists(ROOT + '/b/foot.json') else {}

# captions: (t, text, {word: colour})
CAP = [
    (2.09, 'а видишь только два', {'два': 'd2'}),
    (3.69, 'Сетчатка глаза плоская', {'плоская': 'd2'}),
    (5.45, 'объём тебе дорисовывает мозг', {'объём': 'd3'}),
    (7.36, 'Соберём мир с нуля', {'нуля': 'd0'}),
    (8.67, 'Точка', {'Точка': 'd0'}),
    (9.24, 'ноль измерений', {'ноль': 'd0'}),
    (10.28, 'Протяни её', {}),
    (11.28, 'линия', {'линия': 'd1'}),
    (12.63, 'вбок — квадрат', {'квадрат': 'd2'}),
    (14.54, 'вверх — куб', {'куб': 'd3'}),
    (16.20, 'А теперь сдвинь куб', {'сдвинь': 'd4'}),
    (17.70, 'куда не показывает', {}),
    (18.66, 'ни одна стрелка', {'стрелка': 'd4'}),
    (19.88, 'Это тессеракт', {'тессеракт': 'd4'}),
    (21.31, 'Мы видим', {}),
    (21.74, 'только его тень', {'тень': 'd4'}),
    (22.81, 'но четвёртое измерение', {'четвёртое': 't'}),
    (24.05, 'у тебя уже есть', {'есть': 't'}),
    (25.36, 'Это время', {'время': 't'}),
    (26.25, 'Теория Эйнштейна', {'Эйнштейна': 't'}),
    (27.18, 'сшила его с пространством', {'пространством': 't'}),
    (28.76, 'А 5D?', {'5D?': 'd5'}),
    (29.63, 'В кино это когда', {'кино': 'd1'}),
    (30.46, 'на тебя брызгают водой', {'водой': 'd1'}),
    (31.89, 'А в физике', {'физике': 'd5'}),
    (32.63, 'пятое измерение', {'пятое': 'd5'}),
    (33.50, 'добавил математик', {}),
    (34.46, 'по имени Теодор Калуца', {'Калуца': 'd5'}),
    (35.97, 'больше ста лет назад', {'ста': 'd3'}),
    (37.48, 'чтобы объединить', {}),
    (38.16, 'гравитацию', {'гравитацию': 'd3'}),
    (38.84, 'и электромагнетизм', {'электромагнетизм': 'd1'}),
    (40.12, 'Почему его не видно?', {'видно?': 'd5'}),
    (41.46, 'Оно свёрнуто', {'свёрнуто': 'd5'}),
    (42.16, 'в крошечное колечко', {'колечко': 'd5'}),
    (43.51, 'как шланг', {'шланг': 'd1'}),
    (44.20, 'издалека — линия', {'линия': 'd1'}),
    (45.28, 'вблизи — трубка', {'трубка': 'd5'}),
    (46.14, 'Теория струн', {'струн': 'd5'}),
    (47.10, 'просит 10 измерений', {'10': 'd5'}),
    (48.65, 'М-теория — 11', {'11': 'd4'}),
    (50.10, 'Только вот', {}),
    (51.00, 'ни одного лишнего', {'лишнего': 'd4'}),
    (51.87, 'пока не нашли', {'нашли': 'd4'}),
    (52.95, 'Напиши, что бы', {'Напиши,': 'd4'}),
    (53.88, 'ты спрятал', {'спрятал': 'd4'}),
    (54.58, 'в четвёртом измерении', {'четвёртом': 'd4'}),
    (55.67, 'А подписаться можно', {'подписаться': 'd3'}),
    (56.63, 'и в нашем, трёхмерном', {'трёхмерном': 'd3'}),
]
CAP_END = TOT

# big dimension tags (t0, t1, text, colour)
TAGS = [
    (8.67, 11.87, '0D', 'd0'), (11.87, 13.87, '1D', 'd1'), (13.87, 15.57, '2D', 'd2'),
    (15.57, 19.88, '3D', 'd3'), (19.88, 22.82, '4D', 'd4'),
    (25.36, 28.72, '3+1', 't'),
    (28.76, 31.84, '5D?', 'd5'), (32.63, 35.92, '5D', 'd5'),
    (47.53, 48.80, '10', 'd5'), (48.80, 50.02, '11', 'd4'),
]
# small chips (t0, t1, text, colour, y)
CHIPS = [
    (4.40, 7.30, '3D  →  2D', 'd1', 1330),
    (9.24, 11.87, 'x · y · z · w = 0', 'd0', 1330),
    (21.90, 22.82, '16 вершин · 32 ребра · 8 кубов', 'd4', 1330),
    (22.82, 25.00, '4-е измерение = ?', 't', 1330),
    (26.30, 28.72, 'x · y · z  +  t', 't', 1330),
    (34.46, 35.92, 'Теодор Калуца · 1921', 'd5', 1330),
    (38.16, 40.00, 'гравитация + свет = 5D', 'd5', 1330),
    (44.20, 46.12, '+1 свёрнутое измерение', 'd5', 1330),
    (51.00, 52.90, 'найдено: 0', 'd4', 1330),
]
STAMPS = [(31.24, 31.84, 'НЕ ФИЗИКА', 'd4')]

def section_colour(t):
    c = D0
    for t0, t1, txt, col in TAGS:
        if t >= t0: c = DIM[col]
    if 22.8 <= t < 28.72: c = T
    if t >= 52.9: c = D3
    return c

# ---------------- assets ----------------
_cache = {}
def img(path, mode='RGB'):
    k = (path, mode)
    if k not in _cache:
        if len(_cache) > 400: _cache.clear()
        _cache[k] = Image.open(path).convert(mode)
    return _cache[k]

rng = np.random.default_rng(11)
STARS = [(rng.uniform(0, W), rng.uniform(0, H*1.3), rng.uniform(.6, 2.2), rng.uniform(.25, .9)) for _ in range(420)]
def background(t):
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im, 'RGBA')
    # faint blueprint grid drifting
    off = (t*14) % 90
    for x in range(-90, W+90, 90): d.line([(x+off*0.3, 0), (x+off*0.3, H)], fill=(138, 123, 255, 14), width=1)
    for y in range(-90, H+90, 90): d.line([(0, y+off), (W, y+off)], fill=(138, 123, 255, 14), width=1)
    for x, y, r, a in STARS:
        yy = (y - t*9*r) % (H*1.3) - H*0.15
        tw = a*(0.75+0.25*math.sin(t*2+x))
        d.ellipse([x-r, yy-r, x+r, yy+r], fill=(220, 230, 255, int(255*tw)))
    # soft radial light in section colour
    c = section_colour(t)
    glow = Image.new('L', (W//8, H//8), 0)
    gd = ImageDraw.Draw(glow); gd.ellipse([W//8*0.1, H//8*0.28, W//8*0.9, H//8*0.66], fill=60)
    glow = glow.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR)
    im = Image.composite(Image.new('RGB', (W, H), c), im, glow.point(lambda v: v*0.5))
    return im

def vignette():
    v = Image.new('L', (W//4, H//4), 0); d = ImageDraw.Draw(v)
    d.ellipse([-W//4*0.25, -H//4*0.2, W//4*1.25, H//4*1.2], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(40)).resize((W, H), Image.BILINEAR)
    return v
VIG = None

def kb(frame, t, t0, t1, z0=1.0, z1=1.07, dx=0, dy=0):
    u = ease((t-t0)/max(.01, t1-t0)); z = z0+(z1-z0)*u
    cx, cy = W/2+dx*u, H/2+dy*u
    a = 1/z
    return frame.transform((W, H), Image.AFFINE, (a, 0, cx - a*W/2, 0, a, cy - a*H/2), resample=Image.BICUBIC)

def footage(name, t, t0, t1):
    meta = FOOT[name]
    i = int((t - t0) * FPS * meta.get('speed', 1.0)) + 1
    p = f"{ROOT}/b/shots/{name}/f{min(i, meta['n']):04d}.jpg"
    fr = img(p)
    return kb(fr, t, t0, t1, 1.0, 1.06)

def layer3d(name, t):
    i = int(round((t - L3D_T0[name]) * FPS)) + 1
    d = f"{ROOT}/l3d/{name}"
    n = len(os.listdir(d))
    return img(f"{d}/f{max(1, min(i, n)):04d}.png", 'RGBA')

def add_glow(base, lay, strength=1.0, radius=16, dy=0):
    if dy:
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh.paste(lay, (0, dy)); lay = sh; dy = 0
    a = lay.split()[3]
    rgb = Image.composite(lay.convert('RGB'), Image.new('RGB', (W, H), (0, 0, 0)), a)
    g = rgb.resize((W//4, H//4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius/4)).resize((W, H), Image.BILINEAR)
    if strength != 1: g = g.point(lambda v: min(255, v*strength))
    base = ImageChops.add(base, g)
    base.paste(lay, (0, dy), lay)
    return base

# ---- avatar ----
AVD = ROOT + '/av/fr'
AV_SEG = {'A': (0.0, 0.0), 'B': (52.84, 4.18)}   # (timeline start, clip start)
def av_frame(t):
    seg = 'B' if t >= 50 else 'A'
    ts, cs = AV_SEG[seg]
    i = int(round((t - ts + cs + LAG) * FPS)) + 1
    return img(f"{AVD}/f{max(1, min(i, 235)):04d}.jpg")

def rounded_mask(w, h, r):
    m = Image.new('L', (w*2, h*2), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w*2-1, h*2-1], r*2, fill=255)
    return m.resize((w, h), Image.LANCZOS)

FACE = (400, 520)  # face centre in the 714x1280 avatar frame
def avatar_rect(base, t, rect, src_w, radius, border=True, alpha=1.0):
    x, y, w, h = [int(round(v)) for v in rect]
    fr = av_frame(t)
    sw = src_w; sh = sw*h/w
    cx = FACE[0] + (357 - FACE[0])*clamp((sw-520)/(714-520))
    cy = FACE[1] + (640 - FACE[1])*clamp((sw-520)/(714-520))
    box = (cx-sw/2, cy-sh/2, cx+sw/2, cy+sh/2)
    crop = fr.transform((w, h), Image.EXTENT, box, resample=Image.BICUBIC)
    m = rounded_mask(w, h, max(1, int(radius)))
    if alpha < 1: m = m.point(lambda v: int(v*alpha))
    if border:
        gl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
        gd.rounded_rectangle([x-6, y-6, x+w+6, y+h+6], radius+6, outline=(*section_colour(t), int(200*alpha)), width=4)
        base = add_glow(base, gl, 1.2, 22)
    base.paste(crop, (x, y), m)
    return base

# ---- text helpers ----
def text_layer(txt, font, fill, stroke=0, stroke_fill=INK):
    bb = font.getbbox(txt, stroke_width=stroke)
    w, h = bb[2]-bb[0]+8, bb[3]-bb[1]+8
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((-bb[0]+4, -bb[1]+4), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

FIT = []
def place(base, lay, cx, cy, scale=1.0, alpha=1.0, glow=None, glow_r=18, check=True):
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

def caption(base, t):
    cur = None
    for k, (t0, txt, kw) in enumerate(CAP):
        t1 = CAP[k+1][0] if k+1 < len(CAP) else CAP_END
        if t0 <= t < t1: cur = (t0, txt, kw)
    if not cur: return base
    t0, txt, kw = cur
    size = 68
    words = txt.split(' ')
    while True:
        f = U(8, size)
        parts = [text_layer(w, f, DIM[kw[w]] if w in kw else D0, stroke=5) for w in words]
        sp = int(size*0.20)
        tw = sum(p.width for p in parts) + sp*(len(parts)-1)
        if tw <= 860 or size <= 44: break
        size -= 2
    lines = [parts]
    if tw > 860:
        half = len(parts)//2 or 1; lines = [parts[:half], parts[half:]]
    lh = int(size*1.35)
    hh = lh*len(lines)
    canvas = Image.new('RGBA', (900, hh+20), (0, 0, 0, 0))
    for li, ln in enumerate(lines):
        lw = sum(p.width for p in ln) + sp*(len(ln)-1); x = (900-lw)//2
        for p in ln:
            canvas.paste(p, (x, li*lh + (lh - p.height)//2), p); x += p.width+sp
    u = eout((t-t0)/0.16)
    hl = [DIM[kw[w]] for w in words if w in kw]
    return place(base, canvas, 540, 1215, scale=0.9+0.1*u, alpha=u, glow=hl[0] if hl else (60, 60, 120), glow_r=16)

def tags(base, t):
    for t0, t1, txt, col in TAGS:
        if t0 <= t < t1:
            u = eback((t-t0)/0.24, 1.2); a = clamp((t-t0)/0.12)*clamp((t1-t)/0.12)
            lay = text_layer(txt, U(9, 200), DIM[col])
            base = place(base, lay, 540, 470, scale=1.25-0.25*u, alpha=a, glow=DIM[col], glow_r=26)
    return base

def chip_layer(txt, col):
    f = M(32, 700)
    bb = f.getbbox(txt)
    tw, th = bb[2]-bb[0], f.getbbox('ЁЙgy')[3]-f.getbbox('ЁЙgy')[1]
    w, h = tw+2*30, th+2*24
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 1, w-2, h-2], h//2, fill=(*INK, 200), outline=(*col, 255), width=3)
    d.text((30-bb[0], (h-th)//2 - f.getbbox('ЁЙgy')[1]), txt, font=f, fill=col)
    return im

def chips(base, t):
    for t0, t1, txt, col, y in CHIPS:
        if t0 <= t < t1:
            u = eout((t-t0)/0.22); a = u*clamp((t1-t)/0.12)
            base = place(base, chip_layer(txt, DIM[col]), 540, y + 30*(1-u), alpha=a, glow=DIM[col], glow_r=12)
    return base

def stamps(base, t):
    for t0, t1, txt, col in STAMPS:
        if t0 <= t < t1:
            c = DIM[col]; f = U(9, 76)
            bb = f.getbbox(txt); w, h = bb[2]-bb[0]+80, bb[3]-bb[1]+64
            im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle([3, 3, w-4, h-4], 16, outline=c, width=9)
            d.rounded_rectangle([16, 16, w-17, h-17], 9, outline=c, width=3)
            d.text((40-bb[0], 32-bb[1]), txt, font=f, fill=c)
            im = im.rotate(6, expand=True, resample=Image.BICUBIC)
            u = clamp((t-t0)/0.22)
            base = place(base, im, 540, 760, scale=1.35-0.35*eout(u), alpha=clamp(u*3), glow=c, glow_r=14)
    return base

def hud(base, t):
    d = ImageDraw.Draw(base, 'RGBA')
    y = 300; c = section_colour(t)
    d.text((120, y), 'MB', font=U(9, 34), fill=D0, anchor='lm')
    d.text((212, y+2), 'ИЗМЕРЕНИЯ', font=M(24, 500), fill=(200, 205, 230, 170), anchor='lm')
    d.text((960, y+2), f"00:{t:04.1f}", font=M(26, 600), fill=(220, 225, 245, 230), anchor='rm')
    d.line([(120, y+34), (960, y+34)], fill=(255, 255, 255, 40), width=2)
    d.line([(120, y+34), (120 + 840*t/TOT, y+34)], fill=(*c, 230), width=3)
    return base

def dim_flash(base, t):
    # stop before the twist, flash on "время"
    if 24.85 <= t < 25.36:
        u = ease((t-24.85)/0.4)
        g = base.convert('L').convert('RGB')
        base = Image.blend(base, g, 0.7*u)
        base = Image.blend(base, Image.new('RGB', (W, H), INK), 0.45*u)
    if 25.36 <= t < 25.56:
        base = Image.blend(base, Image.new('RGB', (W, H), D0), 0.75*(1-(t-25.36)/0.2))
    return base

def cover(base, t):
    # opening title over the full-screen avatar (frame 0 = cover)
    a = clamp((1.95 - t)/0.25)
    if a <= 0: return base
    f1 = U(9, 92); f2 = U(9, 128)
    base = place(base, text_layer('ТЫ ВИДИШЬ', f1, D0, stroke=6), 540, 470, alpha=a, glow=D2, glow_r=22, check=False)
    base = place(base, text_layer('ТОЛЬКО 2D', f2, D2, stroke=7), 540, 600, alpha=a, glow=D2, glow_r=30, check=False)
    return base

DROPS = [(rng.uniform(80, W-80), rng.uniform(0, 1), rng.uniform(0.6, 1.4)) for _ in range(140)]
def drops(t, t0):
    # "5D cinema": a screen frame and water splashing on the viewer (procedural)
    base = background(t)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    u = eout((t-t0)/0.4)
    d.rounded_rectangle([150, 640, 930, 1080], 18, outline=(*D5, int(220*u)), width=5)          # cinema screen
    for k in range(3): d.line([(230+k*260, 1080), (180+k*300, 1160)], fill=(*D5, int(90*u)), width=3)
    for x, ph, sp in DROPS:
        y = ((ph + (t-t0)*0.55*sp) % 1.0) * 1500 + 380
        ln = 38*sp
        d.line([(x, y), (x-4, y+ln)], fill=(*D1, int(200*u)), width=4)
        if (ph*7 + (t-t0)*3*sp) % 1.0 < 0.08:
            r = 10 + 30*((ph*7 + (t-t0)*3*sp) % 0.08)/0.08
            d.ellipse([x-r, 1330-r*0.3, x+r, 1330+r*0.3], outline=(*D1, 150), width=3)
    return add_glow(base, lay, 1.0, 14)

def frame(fi):
    t = fi / FPS
    shot = next(s for s in SHOTS if s[0] <= t < s[1]) if t < TOT else SHOTS[-1]
    t0, t1, kind, arg = shot
    FIT.clear()
    if kind == 'avatar_hook':
        base = background(t)
        u = ease((t-1.85)/0.45)     # full screen -> card
        rect = (0+230*u, 0+400*u, W-(W-620)*u, H-(H-660)*u)
        src = 714 - (714-520)*u
        base = avatar_rect(base, t, rect, src, 40*u, border=u > 0.05)
        base = cover(base, t)
    elif kind == 'avatar_end':
        base = background(t)
        lay = layer3d(arg, t)
        lay2 = lay.copy(); lay2.putalpha(lay.split()[3].point(lambda v: int(v*.45)))
        base = add_glow(base, lay2, 0.8, 18, dy=60)
        u = eback((t-t0)/0.4, 1.1)
        w, h = 620*u, 660*u
        base = avatar_rect(base, t, (540-w/2, 730-h/2, max(2, w), max(2, h)), 520, 40, alpha=clamp((t-t0)/0.15))
    elif kind == 'drops':
        base = drops(t, t0)
    elif kind == '3d':
        base = background(t)
        lay = layer3d(arg, t)
        base = add_glow(base, lay, 1.1, 18, dy={'spacetime': 30, 'hose': -40}.get(arg, -110))
    else:
        base = footage(arg, t, t0, t1)
    if kind == 'foot':
        global VIG
        if VIG is None: VIG = vignette()
        base = Image.composite(base, Image.new('RGB', (W, H), INK), VIG.point(lambda v: 60+v*0.75))
    base = dim_flash(base, t)
    base = tags(base, t)
    base = chips(base, t)
    base = stamps(base, t)
    if not (kind == 'avatar_hook' and t < 1.95):
        base = caption(base, t)
    base = hud(base, t)
    # text-fit: every text box inside the frame
    for (x0, y0, x1, y1) in FIT:
        if x0 < 60 or x1 > W-60 or y0 < 200 or y1 > 1500:
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
