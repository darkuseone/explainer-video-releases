# Text-to-audio alignment without ASR: speech runs (by RMS) <-> breath groups (by punctuation), DP on syllable rate;
# words inside a run spread by syllable count. Output: timeline.json (phrases, words) in the time base of the given wav.
import sys,re,json,wave,numpy as np
wav=sys.argv[1]; out=sys.argv[2]
w=wave.open(wav); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
hop=int(0.01*sr); n=len(a)//hop
db=20*np.log10(np.array([np.sqrt(np.mean(a[i*hop:(i+1)*hop]**2))+1e-9 for i in range(n)]))
floor=np.percentile(db,8); thr=max(floor+12,-45)
sp=db>thr
# close tiny gaps (<0.12 s) inside speech
runs=[];i=0
while i<n:
    if sp[i]:
        j=i
        while j<n and sp[j]: j+=1
        runs.append([i,j]); i=j
    else: i+=1
merged=[runs[0]]
for r in runs[1:]:
    if (r[0]-merged[-1][1])*0.01<0.16: merged[-1][1]=r[1]
    else: merged.append(r)
runs=[(s*0.01,e*0.01) for s,e in merged if (e-s)*0.01>0.06]
txt=open(sys.argv[3]).read().replace('́','')
txt=re.sub(r'\[[a-z]+\]\s*','',txt)
paras=[p.strip() for p in txt.split('\n\n') if p.strip()]
V='аеёиоуыэюяАЕЁИОУЫЭЮЯ'
def syl(wd):
    k=sum(c in V for c in wd)
    if re.search('[A-Za-z]',wd): k=max(1,len(re.findall('[aeiouy]+',wd.lower())))
    if wd.lower()=='эс-вэ-гэ': k=3
    return max(1,k)
groups=[]  # breath groups: list of (para, words)
for pi,p in enumerate(paras):
    cur=[]
    for wd in p.split():
        cur.append(wd)
        if wd[-1] in '.,?!…:' or wd=='—':
            groups.append((pi,cur)); cur=[]
    if cur: groups.append((pi,cur))
G=len(groups); R=len(runs)
gs=[sum(syl(x) for x in g[1] if x!='—') for g in groups]
rd=[e-s for s,e in runs]
rate=sum(gs)/sum(rd)
# DP: cover runs in order by groups; each step joins k groups with m runs (k,m in 1..3)
INF=1e18; D=np.full((G+1,R+1),INF); B={}
D[0,0]=0
for gi in range(G+1):
    for ri in range(R+1):
        if D[gi,ri]>=INF: continue
        for k in range(1,4):
            for m in range(1,4):
                g2,r2=gi+k,ri+m
                if g2>G or r2>R: continue
                if k>1 and m>1: continue
                s=sum(gs[gi:g2]); dur=runs[r2-1][1]-runs[ri][0]
                c=(np.log((s/rate+0.05)/(dur+0.05)))**2*10+(k-1)*0.6+(m-1)*0.9
                if D[gi,ri]+c<D[g2,r2]: D[g2,r2]=D[gi,ri]+c; B[(g2,r2)]=(gi,ri)
path=[];cur=(G,R)
while cur!=(0,0):
    p=B[cur]; path.append((p,cur)); cur=p
path.reverse()
words=[]
for (gi,ri),(g2,r2) in path:
    ws=[(groups[g][0],x) for g in range(gi,g2) for x in groups[g][1] if x!='—']
    segs=runs[ri:r2]; tot_sp=sum(e-s for s,e in segs)
    wts=[syl(x)+0.35 for _,x in ws]; S=sum(wts)
    # map cumulative syllable position -> time over the concatenated speech of the runs
    def tmap(f):
        x=f*tot_sp
        for s,e in segs:
            if x<=e-s+1e-9: return s+x
            x-=e-s
        return segs[-1][1]
    c=0
    for (pi,x),wt_ in zip(ws,wts):
        t0=tmap(c/S); c+=wt_; t1=tmap(c/S)
        words.append([round(t0,3),round(t1,3),x,pi])
ph=[]
for pi in range(len(paras)):
    ww=[w_ for w_ in words if w_[3]==pi]; ph.append([ww[0][0],ww[-1][1]])
json.dump({'phrases':ph,'words':words,'tot':round(len(a)/sr,3)},open(out,'w'),ensure_ascii=False)
print('runs',R,'groups',G,'rate %.2f syl/s'%rate); print(ph)
