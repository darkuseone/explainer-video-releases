# Синтез SFX для ролика eif10 (Эйфелева башня, +15 см). numpy+scipy, детерминированно.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
SR=48000; rs=np.random.RandomState(110)
def lp(x,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=4): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def save(n,x):
    x=x/np.max(np.abs(x)+1e-9)*0.89; d=int(SR*0.009); y=np.stack([x,np.concatenate([np.zeros(d),x[:-d]])],1)
    wavfile.write(n,SR,(y*32767).astype(np.int16)); print(n,len(x)/SR)
def tt(T): return np.arange(int(SR*T))/SR
# 1. heartbeat_pair: два глухих удара сердца (перед поворотом)
T=1.0; t=tt(T)
def thump(t0,f0,a):
    u=np.clip(t-t0,0,None); e=np.where(t>=t0,np.exp(-u/0.07),0); f=f0*np.exp(-u*9)+38
    return a*np.sin(2*np.pi*np.cumsum(f)/SR)*e
save('heartbeat_pair.wav',lp(thump(0.02,95,1.0)+thump(0.34,80,0.75),240))
# 2. glass_shatter: карточка факта разваливается
T=1.3; t=tt(T); n=rs.randn(len(t)); x=hp(n,3000)*np.exp(-t/0.12)*0.8
for k in range(26):
    t0=rs.uniform(0.02,0.55); f=rs.uniform(2500,7500); u=np.clip(t-t0,0,None)
    x+=np.where(t>=t0,np.sin(2*np.pi*f*u)*np.exp(-u/rs.uniform(0.02,0.08)),0)*rs.uniform(0.15,0.5)
x+=lp(rs.randn(len(t)),600)*np.exp(-t/0.05)*1.2
save('glass_shatter.wav',x)
# 3. tape_ratchet: трещотка рулетки при замере
T=1.2; t=tt(T); x=np.zeros(len(t))
for i in range(22):
    t0=0.03+i*0.045*(1+0.02*i); idx=int(t0*SR)
    if idx+800<len(t): x[idx:idx+800]+=bp(rs.randn(800),1500,6000)*np.exp(-np.arange(800)/110)*0.8
save('tape_ratchet.wav',x+0.15*bp(rs.randn(len(t)),400,1800)*np.sin(np.pi*t/T))
# 4. thermo_rise: тон растёт вместе с градусником
T=1.3; t=tt(T); f=180+900*(t/T)**1.6; ph=2*np.pi*np.cumsum(f)/SR
save('thermo_rise.wav',(np.sin(ph)+0.4*np.sin(2*ph)+0.15*rs.randn(len(t)))*np.sin(np.pi*np.clip(t/T,0,1))**0.6*np.where(t<T-0.08,1,(T-t)/0.08))
# 5. arrow_swish: стрелка уезжает вбок
T=0.6; t=tt(T); n=rs.randn(len(t)); env=np.sin(np.pi*np.clip(t/T,0,1))**2
save('arrow_swish.wav',bp(n,1500,9000)*env*(0.4+0.6*(t/T))+0.4*lp(n,500)*env)
# 6. lean_creak: башню ведёт в сторону (низкий скрип)
T=1.6; t=tt(T); f=48+12*np.sin(2*np.pi*1.3*t); ph=2*np.pi*np.cumsum(f)/SR
x=sum(np.sin(k*ph)*np.exp(-k*0.4) for k in range(1,7))*(1+0.4*np.sign(np.sin(2*np.pi*11*t)))
save('lean_creak.wav',lp(x,900)*np.sin(np.pi*np.clip(t/T,0,1))**1.3)
