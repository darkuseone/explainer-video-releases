import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
SR=48000; rng=np.random.default_rng(10)
def lp(x,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=4): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def env(n,a,r): t=np.arange(n)/SR; e=np.minimum(1,t/max(a,1e-4))*np.exp(-np.maximum(0,t-a)/r); return e
def norm(x,pk=0.9): return x/np.max(np.abs(x))*pk
def w(name,x): sf.write(name,norm(x).astype(np.float32),SR); print(name,len(x)/SR)
# bed 60 s
T=60.5; n=int(T*SR); t=np.arange(n)/SR
chords=[(110,164.8,220),(98,146.8,196),(87.3,130.8,174.6),(103.8,155.6,207.6)]
pad=np.zeros(n)
for k in range(int(T/8)+1):
    s=int(k*8*SR); e=min(n,int((k+1)*8*SR)+SR)
    if s>=n: break
    tt=np.arange(e-s)/SR; seg=np.zeros(e-s)
    for f in chords[k%4]:
        for d in(-0.15,0.15): seg+=np.sign(np.sin(2*np.pi*(f+d)*tt))*0.3+np.sin(2*np.pi*(f+d)*tt)
    fade=np.minimum(1,np.minimum(tt/1.0,(tt[-1]-tt)/1.0)); pad[s:e]+=seg*fade
pad=lp(pad,900)*(0.8+0.2*np.sin(2*np.pi*0.125*t))
# pulse 100 bpm soft kick + hat
pulse=np.zeros(n); beat=60/100
for i in range(int(T/beat)):
    s=int(i*beat*SR); L=int(0.35*SR)
    if s+L>n: break
    tt=np.arange(L)/SR; f=45+60*np.exp(-tt*30); k=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*9)
    pulse[s:s+L]+=k*(1.0 if i%2==0 else 0.55)
    hs=s+int(beat/2*SR); hl=int(0.05*SR)
    if hs+hl<n: pulse[hs:hs+hl]+=hp(rng.standard_normal(hl),7000)*np.exp(-np.arange(hl)/SR*80)*0.15
shim=bp(rng.standard_normal(n),3000,6000)*0.05*(0.5+0.5*np.sin(2*np.pi*0.07*t))
arp=np.zeros(n); notes=[440,523.3,659.3,523.3]
for i in range(int(T/(beat/2))):
    s=int(i*beat/2*SR); L=int(0.25*SR)
    if s+L>n: break
    tt=np.arange(L)/SR; arp[s:s+L]+=np.sin(2*np.pi*notes[i%4]*tt)*np.exp(-tt*14)*0.12
bed=norm(pad)*0.5+norm(pulse)*0.45+shim+arp*(t>4.7)
bed[:int(0.02*SR)]*=np.linspace(0,1,int(0.02*SR))
w('bed_onc10.wav',np.stack([bed,np.roll(bed,240)],1)[:,0])
# sfx
def whoosh(d=0.5):
    L=int(d*SR); tt=np.arange(L)/SR; x=rng.standard_normal(L); out=np.zeros(L)
    for i in range(0,L,480):
        fc=300+5000*(i/L); seg=bp(x[max(0,i-2400):i+480],fc*0.7,fc*1.3)[-480:]; out[i:i+len(seg)]=seg[:min(480,L-i)]
    return out*np.sin(np.pi*tt/d)**2
w('sfx_whoosh.wav',whoosh())
L=int(0.8*SR); tt=np.arange(L)/SR; f=38+90*np.exp(-tt*22); w('sfx_hit.wav',np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*5)+lp(rng.standard_normal(L),2000)*np.exp(-tt*40)*0.4)
L=int(0.5*SR); tt=np.arange(L)/SR; w('sfx_ding.wav',(np.sin(2*np.pi*1318*tt)+0.5*np.sin(2*np.pi*2637*tt)+0.3*np.sin(2*np.pi*3951*tt))*np.exp(-tt*8))
L=int(0.04*SR); w('sfx_tick.wav',hp(rng.standard_normal(L),3000)*np.exp(-np.arange(L)/SR*150))
L=int(0.3*SR); tt=np.arange(L)/SR; g=np.sign(np.sin(2*np.pi*(200+800*(rng.random(L)>0.97).cumsum()%7*60)*tt))*((tt*40).astype(int)%2); w('sfx_glitch.wav',bp(g+rng.standard_normal(L)*0.5,400,6000)*np.exp(-tt*6))
L=int(0.5*SR); tt=np.arange(L)/SR; w('sfx_stamp.wav',lp(rng.standard_normal(L),1500)*np.exp(-tt*25)+np.sin(2*np.pi*80*tt)*np.exp(-tt*14)*0.8)
L=int(0.25*SR); tt=np.arange(L)/SR; w('sfx_pop.wav',np.sin(2*np.pi*(600+900*np.exp(-tt*40))*tt)*np.exp(-tt*25))
