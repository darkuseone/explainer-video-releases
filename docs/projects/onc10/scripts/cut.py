import json,numpy as np,soundfile as sf,subprocess,sys,re
T=float(sys.argv[1])  # tempo factor
subprocess.run(f'rubberband -q --fine -F -T {T} raw.wav rawT.wav',shell=True,check=True,stderr=subprocess.DEVNULL)
y,sr=sf.read('rawT.wav'); y=y.mean(1) if y.ndim>1 else y
a=[(w,s/T,e/T) for w,s,e in json.load(open('wt.json'))]
txt=open('../voice.txt').read().replace('\n',' ')
# sentence-end flags per word (punctuation after word)
toks=re.findall(r"[\w\u0301ё\-]+[^\w\u0301\s]*",txt)
punct=[]
for t in toks:
    p=re.sub(r"[\w\u0301ё]","",t.split('-')[-1])
    n=len([x for x in re.split(r'-',re.sub(r'[^\w\u0301ё\-]','',t)) if x])
    punct+=['']*(n-1)+[p]
assert len(punct)==len(a),(len(punct),len(a))
H=int(.005*sr)/sr; fr=int(.02*sr); hop=int(round(H*sr))
db=20*np.log10(np.array([np.sqrt(np.mean(y[i:i+fr]**2)+1e-12) for i in range(0,len(y)-fr,hop)]))
gaps=[]
for i in range(1,len(a)):
    s,e=int(a[i-1][2]/H),int(a[i][1]/H)
    if e>s: gaps.append(db[s:e])
NF=float(np.percentile(np.concatenate(gaps),10)); TH=NF+6
ph=[[0]]
for i in range(1,len(a)):
    s,e=int(a[i-1][2]/H),int(a[i][1]/H); run=best=0
    for v in db[s:e]<TH: run=run+1 if v else 0; best=max(best,run)
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
L=len(y)/sr; pieces=[]
for k,c in enumerate(ph):
    we=a[c[-1]][2]; ws=a[c[0]][1]
    prevend=a[ph[k-1][-1]][2] if k else 0
    nxt=a[ph[k+1][0]][1] if k+1<len(ph) else L
    on=max(head_start(ws,prevend)-0.08,0)
    on=max(on,prevend+0.0)
    te=tail_end(we,nxt)
    ck=min(te+0.10,(head_start(nxt,we)-0.08) if k+1<len(ph) else L)
    ck=max(ck,we+0.03)
    pieces.append(dict(w=c,hs=on,ce=ck,tail=te-we,lead=ws-on,end=punct[c[-1]],txt=' '.join(a[i][0] for i in c),nat=(nxt-we) if k+1<len(ph) else 0))
def tg(e): return 0.42 if any(ch in e for ch in '.?') else 0.30 if ':' in e else 0.20 if ',' in e else 0.12
def sm(j):
    P,Q=pieces[j],pieces[j+1]
    return abs(P['ce']-Q['hs'])<1e-4 and (P['ce']-a[P['w'][-1]][2])+Q['lead']>=tg(P['end'])-1e-6
out=[];t=0.0;neww=[None]*len(a);rows=[]
for k,p in enumerate(pieces):
    z=y[int(p['hs']*sr):int(p['ce']*sr)].copy()
    fi=int(.02*sr);fo=int(.03*sr)
    cin = k>0 and sm(k-1)
    cout= k+1<len(pieces) and abs(p['ce']-pieces[k+1]['hs'])<1e-4 and p['nat']<=0.12+1e-6
    p['seam']=cin
    if not cin: z[:fi]*=np.linspace(0,1,fi)
    if not (k+1<len(pieces) and sm(k)): z[-fo:]*=np.linspace(1,0,fo)
    if k:
        prev=pieces[k-1]; e=prev['end']
        tgt=0.42 if any(ch in e for ch in '.?') else 0.30 if ':' in e else 0.20 if ',' in e else 0.12
        tgt=min(tgt,prev['nat'])
        used=(prev['ce']-a[prev['w'][-1]][2])+p['lead']
        sil=max(0.0,tgt-used); out.append(np.zeros(int(sil*sr))); t+=sil
        rows.append(dict(k=k,prev=prev['txt'][-20:],next=p['txt'][:20],nat=round(prev['nat'],3),new=round(used+sil,3),tail=round(prev['tail'],3),seam=p['seam'],cut_db=round(float(db[min(int(prev['ce']/H),len(db)-1)]-NF),1),head_db=round(float(db[int(p['hs']/H)]-NF),1)))
    p0=t
    for i in p['w']: neww[i]=[a[i][0],p0+a[i][1]-p['hs'],p0+a[i][2]-p['hs']]
    out.append(z); t+=len(z)/sr
v=np.concatenate(out+[np.zeros(int(.05*sr))]); sf.write('pre_w.wav',v,sr)
json.dump(dict(words=neww,joins=rows,NF=NF,T=T,pieces=[{k:p[k] for k in ('txt','hs','ce','tail','end')} for p in pieces]),open('cut.json','w'),ensure_ascii=False,indent=0)
print('NF',round(NF,1),'phrases',len(pieces),'dur',round(len(v)/sr,2))
for r in rows: print(r)
