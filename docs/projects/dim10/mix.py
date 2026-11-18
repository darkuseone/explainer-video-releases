# dim10 mix: voice + library bed (space_cinematic_electronica_120bpm, extended by a bar-aligned loop) + library SFX
import numpy as np, subprocess, json
SR = 48000; TOT = 58.22; A = '/home/user/explainer-video-releases/audio/'
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
vo = load('../v/vo2.wav'); vo = vo[:N]; vo = np.pad(vo, ((0, N-len(vo)), (0, 0)))

# ---- bed: track[0:44] + 1 s crossfade + track[32:] (12 s = 6 bars at 120 bpm, same bar phase) ----
m = load(A + 'music/space_cinematic_electronica_120bpm.mp3')
a, b = m[:int(44*SR)], m[int(32*SR):]
xf = SR
r = np.linspace(0, 1, xf)[:, None]
bed = np.concatenate([a[:-xf], a[-xf:]*(1-r) + b[:xf]*r, b[xf:]])[:N]
bed = np.pad(bed, ((0, N-len(bed)), (0, 0)))
env = np.ones(N)
t = np.arange(N)/SR
def ramp(t0, t1, v0, v1):
    i0, i1 = int(t0*SR), int(t1*SR); env[i0:i1] = np.linspace(v0, v1, i1-i0)
env[:] = 1.0
ramp(24.70, 25.30, 1.0, 0.05); env[int(25.30*SR):int(25.36*SR)] = 0.05
ramp(25.36, 25.40, 0.05, 1.35); ramp(25.40, 28.0, 1.35, 1.0)
env[int(0*SR):int(0.3*SR)] *= np.linspace(0, 1, int(0.3*SR))
env[N-int(0.03*SR):] *= np.linspace(1, 0, int(0.03*SR))
vl = lufs(vo); bl = lufs(bed[:int(56*SR)])
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
for k, c in enumerate([3.58, 7.30, 22.82, 28.72, 31.84, 35.92, 40.0, 46.12, 50.02, 52.90]):
    e(W[k % 4], c-0.14, -21, pan=[-.25, .25][k % 2])
e('whoosh/pro_whoosh_big_long.wav', 0.0, -15)                     # hook: warp jump
e('bolt9/bass_hit_sub.wav', 0.34, -12); e('impact/boom.wav', 0.34, -17)   # arrival flash
e('impact/drop1.wav', 1.13, -16); e('whoosh/w4.wav', 1.10, -20)  # 4D echo burst
e('impact/drop1.wav', 3.11, -17)                                  # 2D
e('bolt9/bass_hit_sub.wav', 8.67-0.02, -15)                       # 0D: the point
for c in [10.3, 12.6, 14.5, 16.6]: e('nuk10/air_peel.wav', c, -22, 0.9, 0.3)   # extrusions
for k, c in enumerate([11.87, 13.87, 15.57]): e('impact/drop1.wav', c-0.02, -17)
e('bolt9/bass_hit_sub.wav', 19.88-0.02, -13); e('tri10/spin_up.wav', 19.9, -20)  # 4D
e('riser/riser_tension.wav', 23.10, -19, 2.24, 0.15)              # before the twist
e('impact/boom.wav', 25.36-0.02, -14); e('bolt9/bass_hit_sub.wav', 25.36-0.02, -13)
e('bolt9/bass_hit_sub.wav', 28.76-0.02, -16)                      # 5D?
e('impact/fit_hit_bamboo_tok.wav', 31.24-0.01, -13)               # stamp
e('impact/drop1.wav', 32.63-0.02, -17)                            # 5D
e('whoosh/pro_whoosh_big_long.wav', 41.45, -18)                   # zoom into the hose
e('warm/counter_land_latch.wav', 47.53-0.02, -13)                 # 10
e('warm/counter_land_latch.wav', 48.80-0.02, -13); e('bolt9/bass_hit_sub.wav', 48.80-0.02, -15)  # 11
e('warm/counter_land_latch.wav', 51.00-0.02, -14)                 # found: 0
for k, c in enumerate([4.40, 9.24, 21.90, 22.82, 26.30, 34.46, 38.16, 44.20]):
    e(f'warm/reveal_slide_thud_{k % 3 + 1}.wav', c-0.19, -20)       # chips
e('ui/click_wood.wav', 55.70, -15)
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
