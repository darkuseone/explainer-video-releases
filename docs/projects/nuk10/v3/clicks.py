import json,numpy as np,soundfile as sf
from scipy.signal import butter,sosfilt
c=json.load(open('cut.json')); y,sr=sf.read('vo3.wav'); y=y.mean(1) if y.ndim>1 else y
pre=sf.info('vo3_pre.wav').samplerate; 
hp=sosfilt(butter(4,4000,'hp',fs=sr,output='sos'),y)
def r(a,b): s=hp[max(0,int(a*sr)):int(b*sr)]; return 20*np.log10(np.sqrt(np.mean(s**2))+1e-12)
out=[]
for k,p in enumerate(c['P']):
    for edge,t in (('start',p['out'][0]),('end',p['out'][1])):
        spike=r(t-0.005,t+0.005)-r(t-0.06,t+0.06)
        out.append((k,edge,round(t,3),round(spike,1)))
mx=max(out,key=lambda x:x[3]); print('max HF spike at edge vs ±60ms (dB):',mx, 'n>3dB',sum(1 for x in out if x[3]>3))
json.dump(out,open('clicks.json','w'))
