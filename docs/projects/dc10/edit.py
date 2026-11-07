# dc10 voice edit: take B, drop sentence 9, normalise long pauses in the silence floor, tempo 1.03 (rubberband, formant-safe)
import numpy as np,soundfile as sf,subprocess,json
y,sr=sf.read('takeB.wav'); assert sr==48000
CUT=[(54.40,59.10)]   # "Так что гонка нейросетей теперь ещё и гонка за электричество." removed for length
keep=[];a=0
for c0,c1 in CUT: keep.append(y[int(a*sr):int(c0*sr)]); a=c1
keep.append(y[int(a*sr):]); 
def xf(parts,n=int(0.02*sr)):
    o=parts[0]
    for p in parts[1:]:
        r=np.linspace(1,0,n); o=np.concatenate([o[:-n],o[-n:]*r+p[:n]*(1-r),p[n:]])
    return o
z=xf(keep)
hop=int(0.005*sr); win=int(0.02*sr)
rms=np.array([np.sqrt(np.mean(z[i:i+win]**2)+1e-12) for i in range(0,len(z)-win,hop)]); db=20*np.log10(rms)
floor=np.percentile(db[db<-45],10) if np.any(db<-45) else -60
thr=floor+6
q=db<max(thr,-50)
# pauses: runs of quiet >= 60ms
runs=[];i=0
while i<len(q):
    if q[i]:
        j=i
        while j<len(q) and q[j]: j+=1
        if (j-i)*hop/sr>=0.06: runs.append((i*hop/sr,j*hop/sr))
        i=j
    else: i+=1
parts=[];a=0;log=[]
for s,e in runs:
    d=e-s
    if s<0.2 or e>len(z)/sr-0.1: continue
    tgt=0.36 if d>0.5 else (0.27 if d>0.32 else d)
    if d-tgt<0.03: continue
    head=min(d*0.6,tgt*0.6+0.0); tail=tgt-head   # keep the decay after the phrase (head) and lead-in before the next (tail)
    parts.append(z[int(a*sr):int((s+head)*sr)]); a=e-tail; log.append((round(s,2),round(d,2),round(tgt,2)))
parts.append(z[int(a*sr):]); z2=xf(parts)
nz=np.where(np.abs(z2)>10**(-50/20))[0]; z2=z2[max(0,nz[0]-int(0.05*sr)):nz[-1]+int(0.4*sr)]
sf.write('vo_edit_pre.wav',z2,sr,subtype='FLOAT')
subprocess.run(['ffmpeg','-v','error','-y','-i','vo_edit_pre.wav','-af','rubberband=tempo=1.03:pitch=1:formant=preserved:transients=smooth:detector=soft:window=standard','-ar','48000','vo_edit.wav'],check=True)
z3,_=sf.read('vo_edit.wav'); print('floor',round(floor,1),'pauses shortened',len(log),'len pre',round(len(z2)/sr,2),'final',round(len(z3)/sr,2))
json.dump({'cut':CUT,'pauses':log,'tempo':1.03},open('edit_log.json','w'))
