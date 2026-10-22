import numpy as np
from scipy.io import wavfile
sr,x=wavfile.read('raw.wav'); x=x.astype(np.float32)/32768
h=int(sr*0.01); nf=len(x)//h; r=np.sqrt(np.mean(x[:nf*h].reshape(nf,h)**2,1)+1e-12); db=20*np.log10(r)
sil=db<-40; runs=[];i=0
while i<nf:
    if sil[i]:
        j=i
        while j<nf and sil[j]: j+=1
        runs.append((i*.01,j*.01)); i=j
    else: i+=1
OVR={}
out=[];pos=0.0
for a,b in runs:
    L=b-a
    if L<0.18 or a<0.2 or b>65.86: continue
    N=OVR.get((round(a,2),round(b,2)),max(0.12,0.2*L)); keep=N/2
    out.append(x[int(pos*sr):int((a+keep)*sr)]); pos=b-keep
y=np.concatenate(out+[x[int(pos*sr):]])
wavfile.write('pre.wav',sr,(np.clip(y,-1,1)*32767).astype(np.int16)); print('dur',len(y)/sr)
