import numpy as np,soundfile as sf
from scipy.signal import butter,sosfilt,fftconvolve
SR=48000
def L(n):
    y,sr=sf.read('c/'+n+'.wav'); y=y.mean(1) if y.ndim>1 else y; return y/np.abs(y).max()
def lp(y,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),y)
def hp(y,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),y)
def bp(y,a,b): return sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),y)
def db(x): return 10**(x/20)
rs=np.random.RandomState(3)
def room(y,t=0.35,wet=0.18,lpf=3500):
    n=int(t*SR); ir=rs.randn(n)*np.exp(-np.arange(n)/SR*7/t); ir=lp(ir,lpf); ir/=np.sqrt((ir**2).sum())
    w=np.pad(fftconvolve(y,ir),(0,1))[:len(y)+n]; d=np.pad(y,(0,n)); return d+wet*w*np.abs(d).max()/max(1e-9,np.abs(w).max())*3
def mix(parts,dur):
    o=np.zeros(int(dur*SR))
    for y,off,g in parts:
        i=int(off*SR); j=min(len(o),i+len(y)); o[i:j]+=y[:j-i]*db(g)
    return o
def air(dur,f1=500,f2=2600,dec=8):
    n=int(dur*SR); x=rs.randn(n); x=np.cumsum(x); x=hp(x,40); x=bp(x,f1,f2)  # brownish, banded
    env=np.minimum(1,np.arange(n)/(0.012*SR))*np.exp(-np.arange(n)/SR*dec); return x/np.abs(x).max()*env
def fin(y,name,peak=-3):
    n=int(0.006*SR); y=y.copy(); y[-n:]*=np.linspace(1,0,n)
    y=y/np.abs(y).max()*db(peak); sf.write(name,np.stack([y,y],1).astype(np.float32),SR,subtype='PCM_24')
# --- counter-end candidates
fin(room(mix([(lp(L('knock_wood'),3000),0,0),(lp(L('fit_key_thock'),2500),0.004,-6),(L('cut_hit_punch'),0,-7),(air(0.45),0.01,-17)],0.6),0.4,0.15),'cA.wav')
fin(room(mix([(L('fit_land.light_fingertip_book'),0,0),(lp(L('knock_desk'),2500),0.002,-4),(L('whoosh_big_thump_airy'),0,-9),(air(0.5,400,2200,7),0.0,-15)],0.7),0.45,0.18),'cB.wav')
fin(room(mix([(lp(L('tap_table'),2800),0,0),(lp(L('knock_wood'),2200),0.018,-5),(L('cut_hit_sub'),0,-8),(air(0.4,600,3000,9),0.02,-18)],0.6),0.35,0.15),'cC.wav')
# --- text reveal candidates (thud lands at 0.20 s = text onset)
def rev(sw,apex,th,thg,name,lpf=3800):
    s=lp(L(sw),lpf); a=int(apex*SR); s=s[max(0,a-int(0.2*SR)):]   # cut so swipe apex at 0.2s
    s*=np.minimum(1,np.arange(len(s))/(0.06*SR))
    fin(room(mix([(s,0,-3),(L(th),0.19,thg),(air(0.25,300,1800,14),0.19,-20)],0.75),0.3,0.12,3000),name)
rev('swipe_velvet',0.265,'pro_pop_in_deep',-2,'rA.wav')
rev('swipe_cloth',0.176,'pro_tap_soft',-1,'rB.wav')
rev('swipe_paper',0.130,'fit_land.light_fingertip_book',-3,'rC.wav',3200)
