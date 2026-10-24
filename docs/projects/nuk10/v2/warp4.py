import json,numpy as np,soundfile as sf,subprocess,os
W=json.load(open('wt.json')); a=W['new']; b=W['v1']
sr=44100; y,_=sf.read('new_raw.wav'); n=len(a)
PRE,POST=0.03,0.05
chunks=[[0]]
for i in range(1,n):
    if a[i][1]-a[i-1][2]>0.12: chunks.append([i])
    else: chunks[-1].append(i)
total=sf.info('/workspace/nuk10/v/vo.wav').duration+0.3
out=np.zeros(int(total*sr)+sr); os.makedirs('ch',exist_ok=True); rep=[]
for k,c in enumerate(chunks):
    i0,i1=c[0],c[-1]
    s=a[i0][1]-PRE; e=a[i1][2]+POST
    ts=b[i0][1]-PRE; te=b[i1][2]+POST
    if k+1<len(chunks):
        tmax=b[chunks[k+1][0]][1]-PRE-0.02
        te=max(te,min(tmax,ts+(e-s)*0.85))
    seg=y[int(max(0,s)*sr):int(e*sr)]
    # fades
    f=int(0.008*sr); seg=seg.copy(); seg[:f]*=np.linspace(0,1,f); seg[-f:]*=np.linspace(1,0,f)
    sf.write(f'ch/{k}.wav',seg,sr)
    ratio=(te-ts)/(e-s)
    subprocess.run(f'rubberband -q --fine -F -D {te-ts} ch/{k}.wav ch/{k}s.wav',shell=True,check=True,stderr=subprocess.DEVNULL)
    z,_=sf.read(f'ch/{k}s.wav'); p=int(max(0,ts)*sr); out[p:p+len(z)]+=z
    rep.append((k,' '.join(a[j][0] for j in c)[:40],round(ratio,2)))
for r in rep: print(r)
L=int((b[-1][2]+0.35)*sr); sf.write('vo_v2_pre.wav',out[:L],sr); print('dur',L/sr)
