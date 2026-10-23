# Синтез SFX для ролика pos10 (позитрон в ловушке). numpy+scipy, детерминированно.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
SR=48000; rs=np.random.RandomState(1010)
def lp(x,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=4): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def save(n,x):
    x=x/np.max(np.abs(x)+1e-9)*0.89; d=int(SR*0.009); y=np.stack([x,np.concatenate([np.zeros(d),x[:-d]])],1)
    wavfile.write(n,SR,(y*32767).astype(np.int16)); print(n,len(x)/SR)
def tt(T): return np.arange(int(SR*T))/SR
# 1. annih_flash: вспышка аннигиляции (шумовой удар + падающий тон + суб)
T=1.2; t=tt(T); n=rs.randn(len(t))
x=hp(n,1800)*np.exp(-t/0.10)*0.9+lp(n,500)*np.exp(-t/0.06)*1.2
f=1400*np.exp(-t*5)+60; x+=0.8*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.35)
x+=0.9*np.sin(2*np.pi*48*t)*np.exp(-t/0.4)
save('annih_flash.wav',x)
# 2. pair_capture: две дорожки сходятся и склеиваются
T=1.0; t=tt(T); q=t/T
f1=1500-1000*q**0.8; f2=300+700*q**0.8
x=np.sin(2*np.pi*np.cumsum(f1)/SR)*0.6+np.sin(2*np.pi*np.cumsum(f2)/SR)*0.6
x*=np.sin(np.pi*np.clip(q,0,1))**0.7
ping=np.where(t>0.85,np.sin(2*np.pi*880*(t-0.85))*np.exp(-(t-0.85)/0.05),0)
save('pair_capture.wav',x*0.7+ping*0.8)
# 3. field_hum: гул электромагнитного поля
T=1.6; t=tt(T); x=np.sin(2*np.pi*55*t)+0.5*np.sin(2*np.pi*110*t)+0.25*np.sin(2*np.pi*165*t+0.5)
x*=(0.75+0.25*np.sin(2*np.pi*7*t)); x+=0.12*lp(rs.randn(len(t)),300)
save('field_hum.wav',x*np.sin(np.pi*np.clip(t/T,0,1))**0.5)
# 4. electron_strip: электрон сорван полем (щелчок и взлетающий свист)
T=0.8; t=tt(T); f=400+3500*(t/T)**2; x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.3)
x+=hp(rs.randn(len(t)),3000)*np.exp(-t/0.02)*1.0
save('electron_strip.wav',x)
# 5. cold_crystal: ледяной стеклянный шимер (холод 0,3 К)
T=1.6; t=tt(T); x=np.zeros(len(t))
for k in range(14):
    t0=rs.uniform(0,0.9); f=rs.uniform(2800,7200); u=np.clip(t-t0,0,None)
    x+=np.where(t>=t0,np.sin(2*np.pi*f*u)*np.exp(-u/0.35),0)*rs.uniform(0.15,0.5)
x+=0.15*hp(rs.randn(len(t)),6000)*np.sin(np.pi*np.clip(t/T,0,1))
save('cold_crystal.wav',x)
# 6. level_drop: ступени вниз по уровням энергии
T=1.6; t=tt(T); x=np.zeros(len(t))
for i,(t0,f) in enumerate([(0.0,880),(0.35,700),(0.75,520),(1.15,330)]):
    u=np.clip(t-t0,0,None); x+=np.where(t>=t0,(np.sin(2*np.pi*f*u)+0.3*np.sin(4*np.pi*f*u))*np.exp(-u/0.18),0)*(0.6+0.15*i)
save('level_drop.wav',x)
# 7. quantum_ping: мягкий итоговый звон основного состояния
T=1.2; t=tt(T); x=(np.sin(2*np.pi*392*t)+0.5*np.sin(2*np.pi*784*t)+0.2*np.sin(2*np.pi*1176*t))*np.exp(-t/0.45)
save('quantum_ping.wav',x*np.minimum(1,t/0.004))
# 8. stealth_slide: тихий скользящий шум (проход тайком)
T=1.3; t=tt(T); n=rs.randn(len(t)); env=np.sin(np.pi*np.clip(t/T,0,1))**2
save('stealth_slide.wav',bp(n,300,1800)*env*0.7+0.3*np.sin(2*np.pi*(180+120*t/T)*t)*env)
