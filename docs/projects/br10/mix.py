# br10 mix: voice + library bed (CuIAqvgYvYSIBrRdLAub, dark cinematic electronic 124 BPM, bar-aligned jump back) + library SFX
import numpy as np, subprocess, json
SR = 48000; TOT = 56.60; A = '/home/user/explainer-video-releases/audio/'
def load(p, ch=2):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()
def lufs(x):
    p = '/tmp/_l.wav'; wav(p, x)
    o = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float([l for l in o.split('\n') if ' I:' in l][-1].split('I:')[1].split('LUFS')[0])
def wav(p, x):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', str(x.shape[1]), '-ar', str(SR), '-i', '-', p], input=x.astype(np.float32).tobytes(), check=True)
N = int(TOT*SR)
vo = load('../v/vo.wav'); vo = vo[:N]; vo = np.pad(vo, ((0, N-len(vo)), (0, 0)))

# ---- bed: track[0:20] + 0.5 s crossfade + track[8.39:] (6 bars at 124 bpm back, same phase); its break (29.3-31) lands on "И знаешь, что смешно?"
m = load(A + 'music/CuIAqvgYvYSIBrRdLAub.mp3')
J, BACK = 20.0, 6*4*60/124
a, b = m[:int(J*SR)], m[int((J-BACK)*SR):]
xf = SR//2
r = np.linspace(0, 1, xf)[:, None]
bed = np.concatenate([a[:-xf], a[-xf:]*(1-r) + b[:xf]*r, b[xf:]])[:N]
bed = np.pad(bed, ((0, N-len(bed)), (0, 0)))
env = np.ones(N)
def ramp(t0, t1, v0, v1):
    i0, i1 = int(t0*SR), int(t1*SR); env[i0:i1] = np.linspace(v0, v1, i1-i0)
ramp(41.1, 41.5, 1.0, 0.12); env[int(41.5*SR):int(42.6*SR)] = 0.12          # stop before the reveal
ramp(42.6, 42.68, 0.12, 1.3); ramp(42.68, 45.0, 1.3, 1.0)
ramp(36.55, 36.66, 1.0, 0.45); ramp(36.66, 37.4, 0.45, 1.0)                 # "без прибыли"
env[:int(0.25*SR)] *= np.linspace(0, 1, int(0.25*SR))
env[N-int(0.03*SR):] *= np.linspace(1, 0, int(0.03*SR))
vl = lufs(vo); bl = lufs(bed[:int(55*SR)])
bed *= 10**((vl - 19 - bl)/20)
bed *= env[:, None]
# ---- SFX ----
sfx = np.zeros((N, 2), np.float32)
def e(f, at, gdb, maxd=None, fo=0.05, pan=0.0):
    x = load(A + 'sfx/' + f)
    if maxd: x = x[:int(maxd*SR)]
    n = len(x); fl = min(n, int(fo*SR))
    if fl: x[-fl:] *= np.linspace(1, 0, fl)[:, None]
    x = x * 10**(gdb/20)
    x[:, 0] *= (1-pan) if pan > 0 else 1; x[:, 1] *= (1+pan) if pan < 0 else 1
    i = int(at*SR); j = min(N, i+n)
    if i < 0: x = x[-i:]; i = 0; j = min(N, len(x))
    sfx[i:j] += x[:j-i]
W = ['whoosh/w1.wav', 'whoosh/w2.wav', 'whoosh/w3.wav', 'whoosh/w4.wav']
CUTS = [5.60, 7.55, 12.00, 13.25, 16.65, 17.70, 19.65, 21.40, 23.95, 25.40, 27.75, 29.45, 30.95, 37.50, 39.30, 45.25, 46.40, 48.20, 50.55]
for k, c in enumerate(CUTS):
    e(W[k % 4], c-0.14, -21, pan=[-.25, .25][k % 2])
e('whoosh/pro_whoosh_big_long.wav', 0.0, -14)                                   # hook: crash-zoom into the web
e('bolt9/bass_hit_sub.wav', 0.34, -12); e('impact/boom.wav', 0.34, -17)          # avatar arrives with a flash
e('whoosh/whoosh_double.wav', 0.95, -19)                                        # echo windows
e('bolt9/bass_hit_sub.wav', 2.30, -12); e('nuk10/gravity_pull.wav', 2.2, -18, 1.0, 0.3)   # the web collapses into one cube
e('impact/n02b_sticker_slap.mp3', 4.62, -10)                                    # НЕ ВЫКЛЮЧАТЬ!
e('ui/click_wood.wav', 6.97, -12)                                              # click on the link
e('nuk10/dot_pop.wav', 8.73, -20); e('warm/reveal_slide_thud_1.wav', 10.71, -19)   # DNS asked / address found
e('tri10/orbit_tick.wav', 11.3, -20); e('impact/drop1.wav', 12.0, -17)         # packet -> server
e('warm/reveal_slide_thud_2.wav', 13.10, -19)                                   # HTML back
for k, c in enumerate([15.45, 15.52, 15.59, 15.66]): e('ui/click1.wav', c, -24)  # page paints
e('bolt9/bass_hit_sub.wav', 15.50, -16)
e('warm/reveal_slide_thud_3.wav', 16.56, -20)                                   # 1989
e('whoosh/swipe_paper.wav', 21.30, -16)                                         # proposal sheet
e('warm/reveal_slide_thud_1.wav', 23.81, -19)                                   # 1993
e('impact/boom.wav', 23.95, -15); e('bolt9/bass_hit_sub.wav', 23.95, -13)     # "взорвал"
for c in [26.16, 26.66, 27.0]: e('nuk10/dot_pop.wav', c-0.02, -17)              # inline images pop
e('warm/reveal_slide_thud_2.wav', 27.66, -20)
e('nuk10/count_roll.wav', 32.3, -20, 2.6, 0.3)                                  # IPO line runs
e('bolt9/bass_hit_sub.wav', 35.14, -12); e('warm/counter_land_latch.wav', 35.66, -13)   # 2.9 billion
e('impact/fit_hit_bamboo_tok.wav', 36.65, -12)                                  # stamp БЕЗ ПРИБЫЛИ
for k in range(9): e('ui/click_claves.wav', 39.4 + k*0.21, -25)                 # Explorer windows multiply
e('riser/riser_tension.wav', 41.0, -20, 1.62, 0.12)                             # stop before the reveal
e('impact/boom.wav', 42.62, -13); e('bolt9/bass_hit_sub.wav', 42.62, -12)       # reveal
e('bolt9/zap_electric.wav', 43.6, -22)                                          # licence
e('nuk10/crack_split.wav', 45.42, -15); e('eif10/glass_shatter.wav', 45.6, -15) # Netscape shatters
e('nuk10/air_peel.wav', 46.40, -20, 1.2, 0.3)                                   # tree grows
e('warm/reveal_slide_thud_3.wav', 46.30, -20)
e('nuk10/count_roll.wav', 48.3, -21, 1.0, 0.2); e('warm/counter_land_latch.wav', 49.30, -13)  # 68.8 %
e('bolt9/bass_hit_sub.wav', 49.85, -15)                                          # Chrome
e('ui/click_wood.wav', 54.05, -14); e('ui/ding1.wav', 54.62, -20)               # subscribe bar
# modem handshake, synthesised (no recording): DTMF blip, answer tone, scrambled noise bursts — 0.85 s under "звук модема"
tt = np.arange(int(0.85*SR))/SR
sig = np.zeros_like(tt)
m1 = tt < 0.22; sig[m1] = 0.5*np.sin(2*np.pi*697*tt[m1]) + 0.5*np.sin(2*np.pi*1209*tt[m1])
m2 = (tt >= 0.26) & (tt < 0.50); sig[m2] = np.sin(2*np.pi*2100*tt[m2]) * (1 + 0.3*np.sign(np.sin(2*np.pi*7*tt[m2])))/1.3
m3 = tt >= 0.52
nz = np.random.default_rng(1).normal(0, 1, m3.sum())
k = np.ones(9)/9; nz = np.convolve(nz, k, 'same')
sig[m3] = nz/np.abs(nz).max() * (0.6 + 0.4*np.sin(2*np.pi*31*tt[m3])) + 0.4*np.sin(2*np.pi*(1200+800*np.sin(2*np.pi*13*tt[m3]))*tt[m3])
f = int(0.01*SR); sig[:f] *= np.linspace(0, 1, f); sig[-f*4:] *= np.linspace(1, 0, f*4)
seg = np.stack([sig, sig], 1).astype(np.float32)
seg *= 10**((vl - 17 - lufs(seg))/20)
i0 = int(53.05*SR); sfx[i0:i0+len(seg)] += seg[:N-i0]
# SFX never closer than 9 dB to the voice in the same 50 ms window (simple ceiling)
win = int(0.05*SR)
for i in range(0, N-win, win):
    sv = np.sqrt(np.mean(vo[i:i+win]**2))+1e-6; ss = np.sqrt(np.mean(sfx[i:i+win]**2))+1e-9
    lim = sv*10**(-9/20)
    if sv > 0.01 and ss > lim: sfx[i:i+win] *= lim/ss
mix = vo + bed + sfx
wav('mix_pre.wav', mix)
o = subprocess.run(['ffmpeg', '-hide_banner', '-i', 'mix_pre.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
js = json.loads(o[o.rindex('{'):o.rindex('}')+1])
f = f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true"
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'mix_pre.wav', '-af', f, '-ar', '48000', 'mix.wav'], check=True)
print('voice', vl, 'bed', bl)
