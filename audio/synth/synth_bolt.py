# Синтез SFX для ролика bolt9 (молния). numpy+scipy, детерминированно (seed). Лицензия: свои, свободно.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
SR=48000
def bp(x,lo,hi,o=4): return sosfilt(butter(o,[lo,hi],'band',fs=SR,output='sos'),x)
def lp(x,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=4): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def save(n,x,st=True):
    x=x/np.max(np.abs(x)+1e-9)*0.89
    if st:
        d=int(SR*0.011); y=np.stack([x,np.concatenate([np.zeros(d),x[:-d]])*0.92+x*0.08],1)
    else: y=x
    wavfile.write(n,SR,(y*32767).astype(np.int16)); print(n,len(x)/SR)
rs=np.random.RandomState(9)
# 1. crack_thunder: сухой треск близкого удара + раскат
T=4.5; t=np.arange(int(SR*T))/SR; n=rs.randn(len(t))
crack=hp(n,1500)*np.exp(-t/0.05)*1.4
rumb=lp(n,180)*(1-np.exp(-t/0.08))*np.exp(-t/1.4)*(1+0.6*np.sin(2*np.pi*3.1*t)*np.sin(2*np.pi*0.7*t))
mid=bp(n,200,1200)*np.exp(-t/0.5)*0.5
save('thunder_crack_close.wav',crack+rumb*6+mid)
# 2. thunder_roll: далёкий раскат
T=5; t=np.arange(int(SR*T))/SR; n=rs.randn(len(t))
env=np.clip(t/0.6,0,1)*np.exp(-np.clip(t-0.6,0,None)/1.6); mod=1+0.8*np.abs(lp(rs.randn(len(t)),6,2))*40
save('thunder_roll_far.wav',lp(n,140)*env*mod)
# 3. zap: электрический разряд (дребезг 50–120 Гц + шипение)
T=0.9; t=np.arange(int(SR*T))/SR; n=rs.randn(len(t))
buzz=np.sign(np.sin(2*np.pi*(90+40*rs.rand())*t+3*np.sin(2*np.pi*13*t)))*0.4
gate=(lp(rs.rand(len(t))>0.55,300,2)>0.3).astype(float)
save('zap_electric.wav',(hp(n,2500)*0.8+buzz)*gate*np.exp(-t/0.35))
# 4. leader_step: короткий электрический щелчок-шаг (3 варианта)
for k in range(3):
    T=0.12; t=np.arange(int(SR*T))/SR; n=rs.randn(len(t))
    save(f'leader_step_{k+1}.wav',(hp(n,3000+800*k)*np.exp(-t/0.012)+bp(n,600,2000)*np.exp(-t/0.03)*0.4))
# 5. bass_hit_sub: удар на числа (саб 45 Гц + клик)
T=1.2; t=np.arange(int(SR*T))/SR
f=45+60*np.exp(-t/0.04); ph=2*np.pi*np.cumsum(f)/SR
save('bass_hit_sub.wav',np.sin(ph)*np.exp(-t/0.45)+hp(rs.randn(len(t)),2000)*np.exp(-t/0.006)*0.5)
# 6. hum_static: гул напряжения под грозу (бед)
T=6; t=np.arange(int(SR*T))/SR
h=sum(np.sin(2*np.pi*50*k*t)/k for k in range(1,8))*0.3+lp(rs.randn(len(t)),400)*2
save('hum_static_bed.wav',h*np.clip(t/0.5,0,1)*np.clip((T-t)/0.5,0,1))
