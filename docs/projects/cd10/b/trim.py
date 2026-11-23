# pause compressor: RMS 10ms, -40 dB; pauses >=0.18 s -> max(0.12, 0.2*len); long (>=0.5) keep >=0.28 (смысловые)
import numpy as np, wave, sys, json
def rd(p):
    w=wave.open(p); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768; return x,sr
def wr(p,x,sr):
    w=wave.open(p,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes()); w.close()
x,sr=rd(sys.argv[1]); W=int(sr*0.01); n=len(x)//W
db=20*np.log10(np.sqrt((x[:n*W].reshape(n,W)**2).mean(1)+1e-12)); sil=db<-40
runs=[];i=0
while i<n:
    if sil[i]:
        j=i
        while j<n and sil[j]: j+=1
        runs.append((i,j)); i=j
    else: i+=1
out=[];pos=0;mp=[]  # map (orig_t, new_t)
newt=0.0
for a,b in runs:
    L=(b-a)*0.01
    if L<0.18 or a==0: continue
    keep=max(0.12,0.2*L)
    if L>=0.5: keep=max(keep,0.28)
    if b>=n: keep=min(L,0.3)
    s0=a*W; s1=b*W; k=int(keep*sr)
    seg=x[pos:s0]; out.append(seg); mp.append((pos/sr,newt)); newt+=len(seg)/sr
    out.append(x[s0:s0+k//2]); out.append(x[s1-(k-k//2):s1]); newt+=k/sr
    print(f"{a*0.01:6.2f} {L:.2f} -> {keep:.2f}")
    pos=s1
out.append(x[pos:]); mp.append((pos/sr,newt))
y=np.concatenate(out); wr(sys.argv[2],y,sr); print('dur',len(y)/sr)
json.dump(mp,open(sys.argv[2]+'.map.json','w'))
