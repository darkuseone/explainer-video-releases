import json,numpy as np,soundfile as sf,subprocess,sys,os
R=float(sys.argv[1]); GAPMAX=float(sys.argv[2]); GAPMIN=0.06
W=json.load(open('../v2/full/wt.json')); a=W['new']; b=W['v1']
y,sr=sf.read('../v2/full/new_raw.wav'); y=y.mean(1) if y.ndim>1 else y
H=int(.005*sr)/sr; fr=int(.02*sr)
db=20*np.log10(np.array([np.sqrt(np.mean(y[i:i+fr]**2)+1e-12) for i in range(0,len(y)-fr,int(round(H*sr)))]))
NF=json.load(open('chunks.json'))['NF']; TH=NF+6
M=json.load(open('/workspace/nuk10/av/meta.json')); AV=[(k,M[k]['t0'],M[k]['t1']) for k in M]
def inav(i):
    for k,t0,t1 in AV:
        if t0-0.25<=b[i][1]<=t1+0.1: return k
n=len(a)
# true pauses: gap reaches TH
ph=[[0]]
for i in range(1,n):
    s,e=int(a[i-1][2]/H),int(a[i][1]/H)
    q=db[s:e]<TH; run=best=0
    for v in q: run=run+1 if v else 0; best=max(best,run)
    if best>=12: ph.append([i])
    else: ph[-1].append(i)
mg=[]
for c in ph:
    if mg and (a[mg[-1][-1]][2]-a[mg[-1][0]][1]<0.25): mg[-1]+=c
    else: mg.append(c)
ph=mg
def tail_end(e,lim):
    j=int(e/H)
    while j<int(lim/H) and not all(db[j:j+8]<TH): j+=1
    return j*H
def head_start(s,lim):
    j=int(s/H)
    while j>int(lim/H) and db[j]>=TH: j-=1
    return j*H
P=[]; L=len(y)/sr
C=[];Hs=[0.0]
for k,c in enumerate(ph):
    we=a[c[-1]][2]
    if k+1<len(ph):
        ns=a[ph[k+1][0]][1]; on=head_start(ns,we)-0.08
        te=tail_end(we,ns)
        if te+0.06<=on:
            ck=min(te+0.10,on); hn=max(ck,on)
        else:
            j0,j1=int((we-0.1)/H),int(ns/H); q=db[j0:j1]<TH; best=(0,0); st=None
            for j,v in enumerate(list(q)+[False]):
                if v and st is None: st=j
                if not v and st is not None:
                    if j-st>best[1]-best[0]: best=(st,j)
                    st=None
            jm=j0+(best[0]+best[1])//2 if best[1]>best[0] else j0+int(np.argmin(db[j0:j1])); ck=hn=jm*H
        C.append(ck); Hs.append(hn)
    else:
        te=tail_end(we,L); C.append(min(te+0.10,L))
    P.append(dict(w=c,src=(Hs[k],C[k]),tail=te-we,av=inav(c[0]) or inav(c[-1])))
# plan placement
outw=[None]*n; off={}; t=0.0; prev_end_word=None
os.makedirs('pc',exist_ok=True); mix=np.zeros(int(70*sr)); rows=[]
for k,p in enumerate(P):
    c=p['w']; hs,ce=p['src']; av=p['av']
    lead=a[c[0]][1]-hs
    if k==0: start_word=a[c[0]][1]
    else:
        pe=outw[P[k-1]['w'][-1]][2]; ng=a[c[0]][1]-a[P[k-1]['w'][-1]][2]
        start_word=pe+max(GAPMIN, min(ng*R, max(GAPMAX, P[k-1]['tail']+0.10)))
    if av:
        if av not in off: off[av]=start_word-b[c[0]][1]
        start_word=b[c[0]][1]+off[av]
        # timemap: word starts -> v1 + off, relative to piece
        tm=[(0,0)]; T=[b[i][1]+off[av]-start_word+lead for i in c]
        for q,i in enumerate(c):
            ss=a[i][1]-hs; d=a[i][2]-a[i][1]
            if q==0: tm[0]=(0,max(0,T[0]-ss))  # lead keeps natural length
            tm.append((ss,T[q]))
            room=(T[q+1]-T[q]) if q+1<len(c) else 9
            gap_src=(a[c[q+1]][1]-a[i][2]) if q+1<len(c) else 9
            dd=min(d*R, room-0.02) if gap_src>0.02 else min(d*R,room)
            if q+1<len(c) and gap_src>0.02: tm.append((a[i][2]-hs, T[q]+dd))
        last=c[-1]; tm.append((a[last][2]-hs, T[-1]+(a[last][2]-a[last][1])*R))
        tm.append((ce-hs, tm[-1][1]+(ce-a[last][2])*R))
        tm=[(int(s*sr),int(d*sr)) for s,d in tm]
        cl=[tm[0]]
        for s,d in tm[1:]:
            if s>cl[-1][0] and d>cl[-1][1]: cl.append((s,d))
        open(f'pc/{k}.tm','w').write('\n'.join(f'{s} {d}' for s,d in cl))
        sf.write(f'pc/{k}.wav',y[int(hs*sr):int(ce*sr)],sr)
        subprocess.run(f'rubberband -q -F --timemap pc/{k}.tm -D {cl[-1][1]/sr} pc/{k}.wav pc/{k}s.wav',shell=True,check=True,stderr=subprocess.DEVNULL)
        for i in c: outw[i]=[a[i][0],b[i][1]+off[av],b[i][2]+off[av]]  # target; measured later
        rat=[(cl[j+1][1]-cl[j][1])/(cl[j+1][0]-cl[j][0]) for j in range(len(cl)-1)]
    else:
        sf.write(f'pc/{k}.wav',y[int(hs*sr):int(ce*sr)],sr)
        if abs(R-1)>1e-3: subprocess.run(f'rubberband -q --fine -F -T {1/R} pc/{k}.wav pc/{k}s.wav',shell=True,check=True,stderr=subprocess.DEVNULL)
        else: os.system(f'cp pc/{k}.wav pc/{k}s.wav')
        for i in c: outw[i]=[a[i][0],start_word+(a[i][1]-a[c[0]][1])*R,start_word+(a[i][2]-a[c[0]][1])*R]
        rat=[R]
    z,_=sf.read(f'pc/{k}s.wav'); z=z.mean(1) if z.ndim>1 else z
    if len(z)<int(.06*sr): print("SHORT",k,p["src"],[a[i] for i in c]); continue
    fi=int(.02*sr); fo=int(.03*sr); z=z.copy(); z[:fi]*=np.linspace(0,1,fi); z[-fo:]*=np.linspace(1,0,fo)
    p0=int((start_word-lead*(R if not av else 1))*sr)
    if av: p0=int((start_word-lead)*sr)
    mix[p0:p0+len(z)]+=z
    p.update(out=(p0/sr,(p0+len(z))/sr),rmin=round(min(rat),2),rmax=round(max(rat),2),txt=' '.join(a[i][0] for i in c))
end=max(p['out'][1] for p in P)+0.05
sf.write('vo3_pre.wav',mix[:int(end*sr)],sr)
json.dump(dict(P=P,outw=outw,off=off,R=R,NF=NF),open('cut.json','w'),ensure_ascii=False)
print('phrases',len(P),'end',round(end,2),'off',{k:round(v,3) for k,v in off.items()})
print('ratios',sorted(set((p['rmin'],p['rmax']) for p in P)))
