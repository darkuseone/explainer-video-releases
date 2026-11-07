import numpy as np,soundfile as sf,subprocess,sys
sys.path.insert(0,'/workspace/dc10/render')
SR=48000; TOT=54.84; N=int(TOT*SR)
K='/workspace/sfx_library/bang10/kit/'; R='/workspace/explainer-video-releases/audio/sfx/'
subprocess.run(['ffmpeg','-v','error','-y','-i','audio/vo_edit.wav','-af',
 'bass=g=1.8:f=150,treble=g=-1:f=7000,deesser=i=0.3,acompressor=ratio=1.8:attack=25:release=200:threshold=-20dB,loudnorm=I=-16:TP=-1.5:LRA=11','-ar','48000','-ac','1','audio/vo_proc.wav'],check=True)
vo,_=sf.read('audio/vo_proc.wav'); v=np.zeros(N); v[:min(N,len(vo))]=vo[:N]
# bed: library track CuIAqv (124 BPM), +3 bars spliced at 38.37 so its natural ending lands under the final question
m,_=sf.read('audio/m.wav'); bar=60/124*4; A=38.37
def cat(parts,n=int(0.04*SR)):
    o=parts[0]
    for p in parts[1:]:
        r=np.linspace(1,0,n)[:,None]; o=np.concatenate([o[:-n],o[-n:]*r+p[:n]*(1-r),p[n:]])
    return o
bed=cat([m[:int(A*SR)],m[int((A-3*bar)*SR):]])[:N]
bed=np.pad(bed,((0,max(0,N-len(bed))),(0,0)))
t=np.arange(N)/SR
w=int(0.05*SR); e=np.sqrt(np.convolve(v**2,np.ones(w)/w,'same')); act=(20*np.log10(e+1e-9)>-40).astype(float)
h=int(0.25*SR); act=np.convolve(act,np.ones(h),'same')>0; g=np.where(act,1.0,0.0)
k=int(0.12*SR); g=np.convolve(g,np.ones(k)/k,'same')
duck=-19*g + -13*(1-g)
fadein=np.clip(t/0.3,0,1); fade=np.clip((TOT-0.05-t)/1.5,0,1)
import pyloudnorm as pl
M=pl.Meter(SR); Lv=M.integrated_loudness(v); Lb=M.integrated_loudness(bed.mean(1))
bed=bed*10**((Lv-Lb)/20)*(10**(duck/20)*fade*fadein)[:,None]
sfx=np.zeros((N,2))
def put(p,t0,db,pan=0.0):
    y,sr=sf.read(p); y=y.mean(1) if y.ndim>1 else y
    if sr!=SR:
        import scipy.signal as ss; y=ss.resample_poly(y,SR,sr)
    y=y*10**(db/20); i=int(t0*SR)
    if i<0: y=y[-i:]; i=0
    j=min(N,i+len(y))
    l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4)
    sfx[i:j,0]+=y[:j-i]*l*1.414; sfx[i:j,1]+=y[:j-i]*r*1.414
from shots import S
THERM={26.60,38.90,45.45}
for n,(c,key) in enumerate([(x[0],x[1]) for x in S[1:]]):
    if c in THERM: put(K+'whoosh-long_%d.wav'%(n%2+1),c-0.25,-25)
    else: put(K+'whoosh-short_%d.wav'%(n%3+1),c-0.08,-26,pan=[-0.3,0.3,0][n%3])
put(K+'hit_1.wav',0.0,-18)
TH=[3.70,10.34,13.54,17.68,25.82,29.80,31.96,41.20,47.14,49.24]
for n,x in enumerate(TH): put(R+'warm/reveal_slide_thud_%d.wav'%(n%3+1),x-0.19,-19)
def counter(a,d,v0,v1,step=1):
    last=None;lt=-1;n=0
    for f in np.arange(a,a+d+0.001,0.004):
        p=min(1,(f-a)/d); p=3*p*p-2*p**3; val=int((v0+(v1-v0)*p)/step)
        if val!=last and f-lt>=0.066: put(R+'ui/picker_tick_%d.wav'%(n%3+1),f,-15); lt=f; n+=1
        last=val
    put(R+'warm/counter_land_latch.wav',a+d-0.004,-13); return n
print('ticks',counter(27.30,0.8,0,500000,step=1000),counter(37.02,0.6,0,35))
for n,x in enumerate([19.95,20.18,20.37,20.66,20.83,21.10]): put(K+'key_%d.wav'%(n+1),x,-30,pan=0.2)
put(K+'click-confirm_1.wav',42.62,-21)
put(K+'riser_1.wav',43.9,-27); put(K+'swell_1.wav',50.40,-27)
se=np.sqrt(np.convolve(sfx.mean(1)**2,np.ones(w)/w,'same'))
lim=np.where(e>10**(-40/20), e*10**(-9/20)/(se+1e-9),10.0); lim=np.minimum(1,lim)
gg=np.convolve(lim,np.ones(int(0.01*SR))/int(0.01*SR),'same'); sfx=sfx*gg[:,None]
mix=bed+sfx+v[:,None]
sf.write('audio/mix_pre.wav',mix,SR,subtype='FLOAT')
sf.write('audio/bed_only.wav',bed,SR,subtype='FLOAT'); sf.write('audio/sfx_only.wav',sfx,SR,subtype='FLOAT')
print('Lv',Lv,'Lb',Lb)
