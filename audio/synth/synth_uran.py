# Синтез SFX для ролика uran9 (год на Уране). numpy+scipy, детерминированно.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
SR=48000; rs=np.random.RandomState(4)
def lp(x,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def save(n,x):
    x=x/np.max(np.abs(x)+1e-9)*0.89; d=int(SR*0.009); y=np.stack([x,np.concatenate([np.zeros(d),x[:-d]])],1)
    wavfile.write(n,SR,(y*32767).astype(np.int16)); print(n,len(x)/SR)
# 1. planet_chime: холодный колокольчик для карточки планеты
T=1.6; t=np.arange(int(SR*T))/SR
save('planet_chime.wav',sum(np.sin(2*np.pi*f*t)*np.exp(-t/d)*a for f,d,a in [(880,0.9,1),(1320,0.5,0.5),(2217,0.25,0.3),(587,1.2,0.4)]))
# 2. party_horn_sad: грустная дудка (свисток вниз)
T=1.1; t=np.arange(int(SR*T))/SR; f=520-260*t/T+8*np.sin(2*np.pi*7*t); ph=2*np.pi*np.cumsum(f)/SR
save('party_horn_sad.wav',(np.sign(np.sin(ph))*0.5+np.sin(2*ph)*0.3)*np.clip(t/0.04,0,1)*np.clip((T-t)/0.2,0,1)*lp(np.ones(len(t)),50,1))
# 3. orbit_sweep: мягкий свип по орбите
T=1.4; t=np.arange(int(SR*T))/SR; n=rs.randn(len(t)); env=np.sin(np.pi*t/T)**2
save('orbit_sweep.wav',(lp(n,300)*(1-env)+lp(n,2800)*env)*env)
# 4. space_drone: низкий космический гул (бед)
T=8; t=np.arange(int(SR*T))/SR
save('space_drone_bed.wav',(np.sin(2*np.pi*55*t)+0.5*np.sin(2*np.pi*82.4*t+np.sin(2*np.pi*0.2*t))+0.3*lp(rs.randn(len(t)),200)*3)*np.clip(t/1,0,1)*np.clip((T-t)/1,0,1))
# 5. year_tick: тик счётчика лет
T=0.06; t=np.arange(int(SR*T))/SR
save('year_tick.wav',np.sin(2*np.pi*2400*t)*np.exp(-t/0.008))
