import numpy as np
from scipy.io import wavfile
sr,x=wavfile.read('raw.wav'); x=x.astype(np.float32)/32768
h=int(sr*0.01); nf=len(x)//h; r=np.sqrt(np.mean(x[:nf*h].reshape(nf,h)**2,1)+1e-12); db=20*np.log10(r)
sil=db<-40;i=0
while i<nf:
    if sil[i]:
        j=i
        while j<nf and sil[j]: j+=1
        if (j-i)>=8: print(round(i*.01,2),round(j*.01,2),round((j-i)*.01,2))
        i=j
    else: i+=1
print(nf*.01)
