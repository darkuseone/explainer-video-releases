# Синтез SFX для ролика hum9 (мычание с зажатым носом). numpy+scipy, детерминированно.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
SR=48000; rs=np.random.RandomState(9)
def lp(x,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def save(n,x):
    x=x/np.max(np.abs(x)+1e-9)*0.89; d=int(SR*0.009); y=np.stack([x,np.concatenate([np.zeros(d),x[:-d]])],1)
    wavfile.write(n,SR,(y*32767).astype(np.int16)); print(n,len(x)/SR)
def buzz(f,t):
    ph=2*np.pi*np.cumsum(f)/SR; return sum(np.sin(k*ph)/k**1.2 for k in range(1,14))
# 1. hum_choke: носовое «ммм», которое душится за ~2 с (поток падает)
T=3.0; t=np.arange(int(SR*T))/SR; f=118+4*np.sin(2*np.pi*5*t)-10*np.clip((t-1.2)/1.5,0,1)
env=np.clip(t/0.08,0,1)*np.clip(1-(t-0.9)/1.6,0,1)**1.5
x=lp(buzz(f,t),900)*env; x+=0.15*bp(rs.randn(len(t)),300,900)*np.clip((t-1.4)/0.6,0,1)*np.clip((2.8-t)/0.6,0,1)
save('hum_choke.wav',x)
# 2. air_flow: поток воздуха через нос (шипение)
T=1.6; t=np.arange(int(SR*T))/SR; save('air_flow.wav',bp(rs.randn(len(t)),900,4200)*np.sin(np.pi*t/T)**1.5)
# 3. pressure_rise: давление нарастает (тон вверх + сжатие)
T=3.4; t=np.arange(int(SR*T))/SR; f=70+90*(t/T)**1.4; ph=2*np.pi*np.cumsum(f)/SR
save('pressure_rise.wav',(np.sin(ph)+0.4*np.sin(2*ph)+0.2*lp(rs.randn(len(t)),400))*(t/T)**0.8*np.clip((T-t)/0.08,0,1))
# 4. cheek_squeak: резиновый скрип надутых щёк
T=0.7; t=np.arange(int(SR*T))/SR; f=520+380*np.sin(np.pi*t/T)+30*np.sin(2*np.pi*31*t); ph=2*np.pi*np.cumsum(f)/SR
save('cheek_squeak.wav',(np.sin(ph)+0.3*np.sign(np.sin(ph)))*np.sin(np.pi*t/T)**0.7)
# 5. bagpipe_sad: волынка сдувается (бурдон + падающая мелодия)
T=1.5; t=np.arange(int(SR*T))/SR; dr=buzz(np.full(len(t),110.0),t); f=np.where(t<0.5,660,np.where(t<1.0,587,520))*(1-0.12*np.clip((t-1.0)/0.5,0,1))
save('bagpipe_sad.wav',(0.5*lp(dr,1200)+lp(buzz(f,t),3000))*np.clip(t/0.05,0,1)*np.clip((T-t)/0.3,0,1))
# 6. flag_flap: хлопок флага
T=0.5; t=np.arange(int(SR*T))/SR; save('flag_flap.wav',bp(rs.randn(len(t)),150,2500)*np.exp(-t/0.07)*(1+0.6*np.sin(2*np.pi*22*t)))
# 7. sniff_block: шмыг заложенным носом
T=0.6; t=np.arange(int(SR*T))/SR; save('sniff_block.wav',bp(rs.randn(len(t)),1200,5000)*np.sin(np.pi*t/T)**2*(0.6+0.4*np.sign(np.sin(2*np.pi*18*t))))
