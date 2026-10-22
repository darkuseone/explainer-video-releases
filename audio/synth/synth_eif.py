# Синтез SFX для ролика eif9 (Эйфелева башня летом). numpy+scipy, детерминированно.
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
SR=48000; rs=np.random.RandomState(15)
def lp(x,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def save(n,x):
    x=x/np.max(np.abs(x)+1e-9)*0.89; d=int(SR*0.009); y=np.stack([x,np.concatenate([np.zeros(d),x[:-d]])],1)
    wavfile.write(n,SR,(y*32767).astype(np.int16)); print(n,len(x)/SR)
# 1. metal_groan: стон нагретого металла (тепловое расширение)
T=1.8; t=np.arange(int(SR*T))/SR; f=62+18*np.sin(2*np.pi*0.7*t)+6*rs.randn(len(t)).cumsum()/np.sqrt(len(t))*30
ph=2*np.pi*np.cumsum(f)/SR; x=sum(np.sin(k*ph)*np.exp(-k*0.35) for k in range(1,9))*(1+0.5*np.sign(np.sin(2*np.pi*9*t)))
save('metal_groan.wav',lp(x,1800)*np.sin(np.pi*t/T)**1.2)
# 2. rivet_ping: удар по заклёпке
T=1.2; t=np.arange(int(SR*T))/SR
save('rivet_ping.wav',sum(a*np.sin(2*np.pi*f*t)*np.exp(-t/d) for f,a,d in [(1520,1,0.35),(2380,0.6,0.22),(3960,0.4,0.12),(760,0.3,0.5)])+0.3*rs.randn(len(t))*np.exp(-t/0.004))
# 3. heat_shimmer: жаркое марево (воздушный свип)
T=2.0; t=np.arange(int(SR*T))/SR; n=rs.randn(len(t)); env=np.sin(np.pi*t/T)**2
save('heat_shimmer.wav',(bp(n,2000,7000)*(0.5+0.5*np.sin(2*np.pi*6*t))+0.6*bp(n,300,900))*env)
# 4. calc_beep: бип калькулятора
T=0.09; t=np.arange(int(SR*T))/SR; save('calc_beep.wav',np.sign(np.sin(2*np.pi*1850*t))*0.5*np.clip((T-t)/0.02,0,1))
# 5. frost_crack: морозный треск
T=0.5; t=np.arange(int(SR*T))/SR; x=np.zeros(len(t))
for k in range(14): i=rs.randint(0,len(t)-400); x[i:i+400]+=rs.randn(400)*np.exp(-np.arange(400)/60)*rs.rand()
save('frost_crack.wav',bp(x,1500,9000))
# 6. sun_sweep: солнце идёт по кругу (тёплый свип)
T=2.4; t=np.arange(int(SR*T))/SR; f=220*2**(t/T); ph=2*np.pi*np.cumsum(f)/SR
save('sun_sweep.wav',(np.sin(ph)+0.5*np.sin(1.5*ph)+0.3*np.sin(2*ph))*np.sin(np.pi*t/T)**2*(0.8+0.2*np.sin(2*np.pi*5*t)))
# 7. browser_click: клик и загрузка страницы
T=0.25; t=np.arange(int(SR*T))/SR; save('browser_click.wav',rs.randn(len(t))*np.exp(-t/0.003)+0.4*np.sin(2*np.pi*900*t)*np.exp(-t/0.05))
