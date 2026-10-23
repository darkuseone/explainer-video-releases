# Синтез SFX и подложки для ролика nuk10 (ядерный взрыв vs Земля). numpy+scipy, детерминированно. Лицензия: собственный синтез, без внешних сэмплов.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
SR=48000; rs=np.random.RandomState(1945)
def lp(x,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=4): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def save(n,x,stereo=True,peak=0.89):
    x=x/np.max(np.abs(x)+1e-9)*peak; d=int(SR*0.009)
    y=np.stack([x,np.concatenate([np.zeros(d),x[:-d]])],1) if stereo else x
    wavfile.write(n,SR,(y*32767).astype(np.int16)); print(n,len(x)/SR)
def tt(T): return np.arange(int(SR*T))/SR
# 1. nuke_boom: взрыв (удар + шумовой разлёт + хвост)
T=2.6; t=tt(T); n=rs.randn(len(t))
x=lp(n,700)*np.exp(-t/0.7)+hp(n,1800)*np.exp(-t/0.08)*0.6+bp(n,200,900)*np.exp(-t/0.3)*0.6
f=110*np.exp(-t*4)+30; x+=1.1*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/1.0)
x*=np.minimum(1,t/0.004); save('nuke_boom.wav',x)
# 2. count_tick: тик счётчика (сухой щелчок)
T=0.09; t=tt(T); x=np.sin(2*np.pi*1900*t)*np.exp(-t/0.008)+0.3*hp(rs.randn(len(t)),5000)*np.exp(-t/0.004); save('count_tick.wav',x)
# 3. count_roll: быстрый ролл цифр (серия тиков с ускорением)
T=1.2; t=tt(T); x=np.zeros(len(t)); tk=0.0; i=0
while tk<T-0.05:
    u=np.clip(t-tk,0,None); x+=np.where(t>=tk,np.sin(2*np.pi*(1500+40*(i%7))*u)*np.exp(-u/0.007),0)*(0.4+0.6*tk/T); tk+=0.11*(1-0.85*tk/T)+0.012; i+=1
save('count_roll.wav',x)
# 4. crack_split: раскол (треск + низкий разлом)
T=1.8; t=tt(T); n=rs.randn(len(t))
x=hp(n,900)*np.exp(-t/0.05)*0.9+lp(n,300)*np.exp(-t/0.5)
for k in range(14):
    t0=rs.uniform(0,0.5); u=np.clip(t-t0,0,None); x+=np.where(t>=t0,bp(rs.randn(len(t)),2000,6000)*np.exp(-u/0.012),0)*0.5
f=60*np.exp(-t*2)+28; x+=0.9*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.8); save('crack_split.wav',x)
# 5. gravity_pull: сжатие, нарастающий низкий тон
T=1.8; t=tt(T); q=t/T; f=50+260*q**1.8; x=np.sin(2*np.pi*np.cumsum(f)/SR)*(0.6+0.4*np.sin(2*np.pi*(3+10*q)*t))
x+=0.25*lp(rs.randn(len(t)),500)*q; x*=np.sin(np.pi*np.clip(q,0,1))**0.6; save('gravity_pull.wav',x)
# 6. air_peel: срыв атмосферы (шипящий свист вниз-вверх)
T=2.0; t=tt(T); q=t/T; n=rs.randn(len(t)); x=np.zeros(len(t))
for k in range(30):
    fc=600+4500*q[k*(len(t)//30)]; 
x=bp(n,800,6000)*np.sin(np.pi*np.clip(q,0,1))**1.4*(0.6+0.4*np.sin(2*np.pi*7*t)); save('air_peel.wav',x)
# 7. sun_flare: вспышка Солнца (резкий светлый свист + подзвон)
T=1.4; t=tt(T); q=t/T; f=300+2600*q**0.7; x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.6)*0.6+hp(rs.randn(len(t)),3000)*np.exp(-t/0.25)*0.5
x+=0.4*np.sin(2*np.pi*1760*t)*np.exp(-t/0.5); x*=np.minimum(1,t/0.01); save('sun_flare.wav',x)
# 8. winter_drone: холодный дрон ядерной зимы
T=3.0; t=tt(T); x=sum(np.sin(2*np.pi*f*t+p)*a for f,a,p in [(41,1,0),(61.5,0.6,1),(82.2,0.4,2)])*(0.7+0.3*np.sin(2*np.pi*0.7*t))
x+=0.25*lp(rs.randn(len(t)),900)*np.sin(np.pi*t/T); x*=np.sin(np.pi*np.clip(t/T,0,1))**0.5; save('winter_drone.wav',x)
# 9. dot_pop: тихий щелчок точек людей
T=0.07; t=tt(T); x=np.sin(2*np.pi*700*t)*np.exp(-t/0.012); save('dot_pop.wav',x)
# 10. bed_nuk10: тёмный тревожный бед 58 c, пульс-«гейгер» + дрон, нарастает к финалу
T=58.0; t=tt(T)
def pad(f,det,a,ph): return a*(np.sin(2*np.pi*f*t+ph)+np.sin(2*np.pi*f*(1+det)*t)+np.sin(2*np.pi*f*(1-det)*t+1))/3
x=pad(46.2,0.003,0.9,0)+pad(69.3,0.004,0.5,1.0)+pad(92.5,0.005,0.3,2.0)
for s,fs in [(0,[185,220,277.2]),(14.5,[174.6,207.7,261.6]),(29,[155.6,185,233]),(43.5,[164.8,196,246.9])]:
    env=np.clip((t-s)/3.5,0,1)*np.clip((s+15-t)/3.5,0,1)
    for f in fs: x+=0.13*np.sin(2*np.pi*f*t)*env*(0.7+0.3*np.sin(2*np.pi*0.13*t))
x*=0.8+0.2*np.sin(2*np.pi*0.06*t)
per=0.5; k=np.zeros(len(t))
for j in range(int(T/per)):
    i=int(j*per*SR); L=int(0.18*SR)
    if i+L<len(t): u=np.arange(L)/SR; k[i:i+L]+=np.sin(2*np.pi*(52+40*np.exp(-u*30))*u)*np.exp(-u/0.07)*(0.35+0.4*min(1,j*per/T))
x+=0.55*k
tick=np.zeros(len(t))
for j in range(int(T*5)):
    i=int(rs.uniform(0,T-0.05)*SR); L=int(0.01*SR); tick[i:i+L]+=rs.randn(L)*np.exp(-np.arange(L)/SR/0.002)
x+=0.05*hp(tick,3000)
x+=0.04*lp(rs.randn(len(t)),1100)
x=lp(x,5500,2); f=int(SR*1.5); x[:int(SR*0.3)]*=np.linspace(0,1,int(SR*0.3)); x[-f:]*=np.linspace(1,0,f)
save('bed_nuk10.wav',x,True,0.85)
