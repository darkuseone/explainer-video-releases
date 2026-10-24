import json,numpy as np,soundfile as sf
c=json.load(open('cut.json')); W=json.load(open('../v2/full/wt.json')); a=W['new']; NF=c['NF']
y,sr=sf.read('../v2/full/new_raw.wav'); y=y.mean(1) if y.ndim>1 else y
def lev(t0,t1):
    s=y[int(t0*sr):int(t1*sr)]; return 20*np.log10(np.sqrt(np.mean(s**2))+1e-12)-NF
m=json.load(open('meas.json'))
rows=[];bad=0
P=c['P']
for k,p in enumerate(P):
    hs,ce=p['src']; we=a[p['w'][-1]][2]
    tailkept=ce-we; cut_db=lev(ce-0.02,ce); head_db=lev(hs,hs+0.02); hs_ok=True
    nxt=P[k+1]['out'][0] if k+1<len(P) else None
    gap=(nxt-p['out'][1]) if nxt is not None else None  # negative=overlap
    ok=cut_db<6 and head_db<6
    full=tailkept>=p['tail']+0.06-1e-6
    bad+=not ok
    rows.append(dict(k=k,txt=p['txt'][-25:],tail_ms=round(p['tail']*1000),kept_ms=round(tailkept*1000),cut_dB_over_floor=round(cut_db,1),head_dB_over_floor=round(head_db,1),gap_or_overlap_ms=None if gap is None else round(gap*1000),verdict=('OK' if full else 'OK-tight') if ok else 'CHECK'))
json.dump(rows,open('joins.json','w'),ensure_ascii=False,indent=0)
for r in rows: print(r)
print('bad',bad,'/',len(rows))
