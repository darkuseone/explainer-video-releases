# Синтез SFX и музыкальной подложки для ролика tri10 (тройная система с пульсаром). numpy+scipy, детерминированно. Лицензия: собственный синтез, без внешних сэмплов.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
SR=48000; rs=np.random.RandomState(2310)
def lp(x,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=4): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def save(n,x,stereo=True,peak=0.89):
    x=x/np.max(np.abs(x)+1e-9)*peak; d=int(SR*0.009)
    y=np.stack([x,np.concatenate([np.zeros(d),x[:-d]])],1) if stereo else x
    wavfile.write(n,SR,(y*32767).astype(np.int16)); print(n,len(x)/SR)
def tt(T): return np.arange(int(SR*T))/SR
# 1. pulsar_tick: сухой высокий тик пульсара (быстрая серия)
T=0.5; t=tt(T); x=np.zeros(len(t))
for k in range(8):
    t0=k*0.055; u=np.clip(t-t0,0,None); x+=np.where(t>=t0,np.sin(2*np.pi*2400*u)*np.exp(-u/0.006),0)*(0.5+0.5*(k/7))
save('pulsar_tick.wav',x)
# 2. spin_up: раскрутка (растущий тон + шум) для счётчика оборотов
T=1.4; t=tt(T); q=t/T; f=80+1800*q**2.2
x=np.sin(2*np.pi*np.cumsum(f)/SR)*0.5+np.sin(2*np.pi*np.cumsum(f*2.01)/SR)*0.2
x+=hp(rs.randn(len(t)),2500)*0.12*q; x*=np.minimum(1,t/0.05)*(1-np.clip((t-1.25)/0.15,0,1))
save('spin_up.wav',x)
# 3. supernova_boom: взрыв (низкий удар + шумовой разлёт)
T=2.2; t=tt(T); n=rs.randn(len(t))
x=lp(n,900)*np.exp(-t/0.5)*1.0+hp(n,1500)*np.exp(-t/0.12)*0.7
f=90*np.exp(-t*3)+32; x+=1.0*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.9)
save('supernova_boom.wav',x)
# 4. star_fade: звезда остывает (падающий тон, гаснущий)
T=1.6; t=tt(T); f=900*np.exp(-t*1.8)+110; x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.7)*0.8+0.3*np.sin(2*np.pi*np.cumsum(f*1.5)/SR)*np.exp(-t/0.4)
save('star_fade.wav',x)
# 5. gravity_pull: невидимая тяга (нарастающий низкий свист + пульсация)
T=2.2; t=tt(T); q=t/T; f=70+220*q**1.6; x=np.sin(2*np.pi*np.cumsum(f)/SR)*(0.6+0.4*np.sin(2*np.pi*(3+9*q)*t))
x+=0.3*lp(rs.randn(len(t)),400)*q; x*=np.sin(np.pi*np.clip(q,0,1))**0.6
save('gravity_pull.wav',x)
# 6. chaos_rumble: хаос трёх тел (рваный грохот)
T=2.6; t=tt(T); x=lp(rs.randn(len(t)),260)*(0.6+0.4*np.sin(2*np.pi*5.5*t+np.sin(t*9)*3))
for k in range(9):
    t0=rs.uniform(0.1,2.3); u=np.clip(t-t0,0,None); x+=np.where(t>=t0,hp(rs.randn(len(t)),1200)*np.exp(-u/0.04),0)*0.5
x*=np.sin(np.pi*np.clip(t/T,0,1))**0.5
save('chaos_rumble.wav',x)
# 7. calm_chime: тихо, орбиты устойчивы (чистый мягкий аккорд)
T=2.0; t=tt(T); x=sum(np.sin(2*np.pi*f*t)*np.exp(-t/0.9)*a for f,a in [(262,1),(392,0.7),(523,0.5),(784,0.25)])
save('calm_chime.wav',x*np.minimum(1,t/0.01))
# 8. orbit_tick: тик счётчика лет
T=0.12; t=tt(T); x=np.sin(2*np.pi*1500*t)*np.exp(-t/0.012)+0.3*hp(rs.randn(len(t)),4000)*np.exp(-t/0.005)
save('orbit_tick.wav',x)
# 9. bed_tri10: тёмная космическая подложка 64 c (дрон + медленные пады + редкие тики пульсара), 100% синтез
T=64.0; t=tt(T)
def pad(f,det,a,ph): return a*(np.sin(2*np.pi*f*t+ph)+np.sin(2*np.pi*f*(1+det)*t)+np.sin(2*np.pi*f*(1-det)*t+1))/3
x=pad(55,0.003,0.8,0)+pad(82.4,0.004,0.5,1.2)+pad(110,0.005,0.35,2.1)
chord=[(0,[220,261.6,329.6]),(16,[196,246.9,293.7]),(32,[174.6,220,261.6]),(48,[196,246.9,329.6])]
for s,fs in chord:
    env=np.clip((t-s)/4,0,1)*np.clip((s+16.5-t)/4,0,1)
    for f in fs: x+=0.16*np.sin(2*np.pi*f*t)*env*(0.7+0.3*np.sin(2*np.pi*0.11*t))
x*= (0.8+0.2*np.sin(2*np.pi*0.05*t))
# «пульсар»: мягкий тик 2.5 раз/с, нарастает к середине
per=0.4; tick=np.zeros(len(t))
for k in range(int(T/per)):
    i=int(k*per*SR); L=int(0.05*SR)
    if i+L<len(t): tick[i:i+L]+=np.sin(2*np.pi*1100*np.arange(L)/SR)*np.exp(-np.arange(L)/SR/0.012)*(0.25+0.5*np.sin(np.pi*k*per/T))
x+=0.12*tick
x+=0.05*lp(rs.randn(len(t)),1200)
x=lp(x,5000,2); f=int(SR*2); x[:int(SR*0.3)]*=np.linspace(0,1,int(SR*0.3)); x[-f:]*=np.linspace(1,0,f)
save('bed_tri10.wav',x,True,0.85)
