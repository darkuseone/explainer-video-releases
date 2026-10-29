import numpy as np,soundfile as sf,subprocess,json
SR=48000; TOT=56.0; N=int(TOT*SR)
K='/workspace/bang10/kit/'; R='/workspace/explainer-video-releases/audio/sfx/'
# ---- voice: approved light chain ----
subprocess.run(['ffmpeg','-v','error','-y','-i','audio/vo_final_raw.wav','-af',
 'bass=g=1.8:f=150,treble=g=-1:f=7000,deesser=i=0.3,acompressor=ratio=1.8:attack=25:release=200:threshold=-20dB,loudnorm=I=-16:TP=-1.5:LRA=11','-ar','48000','-ac','1','audio/vo_proc.wav'],check=True)
vo,_=sf.read('audio/vo_proc.wav'); v=np.zeros(N); v[:min(N,len(vo))]=vo[:N]
# ---- bed: library ElevenLabs track UwUT4 (ours), drop aligned to reveal 35.40 ----
m,_=sf.read('audio/m.wav'); bar=60/124*4; s=1.356
def seg(a,b): return m[int(a*SR):int(b*SR)]
def cat(parts,n=int(0.02*SR)):
    o=parts[0]
    for p in parts[1:]:
        r=np.linspace(1,0,n)[:,None]; o=np.concatenate([o[:-n],o[-n:]*r+p[:n]*(1-r),p[n:]])
    return o
bed=cat([seg(s,s+3*bar),seg(s,44.0),seg(44.0-4*bar,46.0)])[:N]
bed=np.pad(bed,((0,max(0,N-len(bed))),(0,0)))
t=np.arange(N)/SR
# voice envelope (50 ms rms, 150 ms hold)
w=int(0.05*SR); e=np.sqrt(np.convolve(v**2,np.ones(w)/w,'same')); act=(20*np.log10(e+1e-9)>-40).astype(float)
h=int(0.25*SR); act=np.convolve(act,np.ones(h),'same')>0; g=np.where(act,1.0,0.0)
k=int(0.12*SR); g=np.convolve(g,np.ones(k)/k,'same')
duck=-19*g + -13*(1-g)        # relative to voice level; calibrated below
dip=-3*np.clip((t-28.5)/0.8,0,1)*(t<35.35)   # twist dip
fade=np.clip((TOT-0.05-t)/1.2,0,1)
gain_db=duck+dip
# calibrate: bed LUFS-ish -> make bed integrated ~ voice-19 under voice
def lufs(x):
    import pyloudnorm as pl; return pl.Meter(SR).integrated_loudness(x)
try:
    Lv=lufs(v); Lb=lufs(bed.mean(1))
except Exception: Lv=-16; Lb=-13.5
bed=bed*10**((Lv-Lb)/20)*(10**(gain_db/20)*fade)[:,None]
# ---- sfx ----
sfx=np.zeros((N,2))
def put(p,t0,db,pan=0.0):
    y,sr=sf.read(p); y=y.mean(1) if y.ndim>1 else y
    if sr!=SR:
        import scipy.signal as ss; y=ss.resample_poly(y,SR,sr)
    y=y*10**(db/20); i=int(t0*SR); j=min(N,i+len(y))
    if i<0: y=y[-i:]; i=0
    l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4)
    sfx[i:j,0]+=y[:j-i]*l*1.414; sfx[i:j,1]+=y[:j-i]*r*1.414
from shots import S
cuts=[x[0] for x in S[1:]]
for n,c in enumerate(cuts):
    if abs(c-35.40)<0.01: continue
    put(K+'whoosh-short_%d.wav'%(n%3+1),c-0.08,-25,pan=[-0.3,0.3,0][n%3])
put(K+'drop_1.wav',0.0,-16)
TH=[9.40,14.56,15.06,17.82,25.62,26.34,28.94,31.50,33.88,34.66,37.20,46.5,46.9,48.3,53.84,54.48]
for n,x in enumerate(TH): put(R+'warm/reveal_slide_thud_%d.wav'%(n%3+1),x-0.19,-19)
def counter(a,d,v0,v1):
    last=None;lt=-1;n=0
    for f in np.arange(a,a+d+0.001,0.004):
        p=min(1,(f-a)/d); p=3*p*p-2*p**3; val=int(round(v0+(v1-v0)*p)) if v1-v0<50 else int((v0+(v1-v0)*p)/100)
        if val!=last and f-lt>=0.066: put(R+'ui/picker_tick_%d.wav'%(n%3+1),f,-15); lt=f; n+=1
        last=val
    put(R+'warm/counter_land_latch.wav',a+d-0.004,-13); return n
print('ticks',counter(4.0,0.75,2016,2026),counter(43.32,0.8,0,2899))
for n,x in enumerate(np.linspace(20.04,20.74,6)): put(K+'tick-crisp_%d.wav'%(n%3+1),x,-27,pan=(-0.3+0.12*n))
put(K+'riser_1.wav',33.2,-24); put(K+'drop_1.wav',35.38,-13); put(K+'hit_1.wav',35.40,-16); put(K+'swell_1.wav',35.5,-26)
put(K+'click_1.wav',40.9,-20); put(K+'click_2.wav',38.9,-24)
put(K+'swell_2.wav',54.2,-26)
# voice guard: sfx >=9 dB under voice in 50ms windows
se=np.sqrt(np.convolve(sfx.mean(1)**2,np.ones(w)/w,'same'))
lim=np.where(e>10**(-40/20), e*10**(-9/20)/(se+1e-9),10.0); lim=np.minimum(1,lim)
lim=np.minimum.accumulate(lim[::-1])[::-1]*0+lim
gg=np.convolve(lim,np.ones(int(0.01*SR))/int(0.01*SR),'same'); sfx=sfx*gg[:,None]
mix=bed+sfx+v[:,None]
sf.write('audio/mix_pre.wav',mix,SR,subtype='FLOAT')
sf.write('audio/bed_only.wav',bed,SR,subtype='FLOAT'); sf.write('audio/sfx_only.wav',sfx,SR,subtype='FLOAT')
