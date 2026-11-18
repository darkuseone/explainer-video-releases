# compress pauses in silence only (keep head+tail), then uniform tempo 1.06 (rubberband, pitch kept)
import numpy as np,wave,json,subprocess
TEMPO=1.06
w=wave.open('rawB.wav');sr=w.getframerate();a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
hop=int(0.005*sr);n=len(a)//hop;db=20*np.log10(np.array([np.sqrt(np.mean(a[i*hop:(i+1)*hop]**2))+1e-9 for i in range(n)]))
sil=db<-42;runs=[];i=0
while i<n:
    if sil[i]:
        j=i
        while j<n and sil[j]: j+=1
        if (j-i)*hop/sr>=0.25: runs.append((i*hop/sr,j*hop/sr))
        i=j
    else: i+=1
PUNCH=[23.42,24.43,29.89,60.06,62.02]   # pauses before answers/punchlines: keep >=0.36
out=[];cur=0.0;tmap=[(0.0,0.0)];newt=0.0
segs=[]
for s,e in runs:
    p=e-s; keep=min(p,max(0.18,min(0.34,0.5*p)))
    if any(abs(s-x)<0.12 for x in PUNCH): keep=min(p,max(keep,0.38))
    if e>=len(a)/sr-0.01: keep=min(p,0.25)
    cut=p-keep
    if cut<0.02: continue
    c0=s+keep*0.4; c1=c0+cut   # remove middle part
    segs.append((c0,c1))
pieces=[];prev=0.0
for c0,c1 in segs:
    pieces.append((prev,c0)); prev=c1
pieces.append((prev,len(a)/sr))
fade=int(0.015*sr);res=[]
for k,(s,e) in enumerate(pieces):
    x=a[int(s*sr):int(e*sr)].copy()
    if k>0: x[:fade]*=np.linspace(0,1,fade)
    if k<len(pieces)-1: x[-fade:]*=np.linspace(1,0,fade)
    tmap.append((s,newt)) if k>0 else None
    newt+=len(x)/sr; tmap.append((e,newt)); res.append(x)
y=np.concatenate(res)
wave_out=wave.open('pre.wav','wb');wave_out.setnchannels(1);wave_out.setsampwidth(2);wave_out.setframerate(sr);wave_out.writeframes((np.clip(y,-1,1)*32767).astype(np.int16).tobytes());wave_out.close()
subprocess.run(['ffmpeg','-v','error','-y','-i','pre.wav','-af',f'rubberband=tempo={TEMPO}:transients=crisp:detector=compound:pitchq=quality','pre_fast.wav'],check=True)
json.dump({'tmap':tmap,'tempo':TEMPO},open('tmap.json','w'))
def T(t):
    xs=[p[0] for p in tmap];ys=[p[1] for p in tmap]
    return float(np.interp(t,xs,ys))/TEMPO
words=json.load(open('voB_words.json'))
nw=[(round(T(s),3),round(T(e),3),wd.strip()) for s,e,wd,_ in words]
json.dump(nw,open('words_new.json','w'),ensure_ascii=False)
print('pre',len(y)/sr,'fast',len(y)/sr/TEMPO)
