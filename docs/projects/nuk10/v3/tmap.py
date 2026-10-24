import json,numpy as np
m=json.load(open('meas.json')); W=json.load(open('../v2/full/wt.json')); b=W['v1']; c=json.load(open('cut.json'))
M=json.load(open('/workspace/nuk10/av/meta.json'))
zones=[(M[k]['t0']-0.3,M[k]['t1']+0.35,c['off'][k]) for k in M]
anc=[(0.0,0.0)]
PS={p['w'][0] for p in c['P']}
_s=open('/workspace/nuk10/b/r.py').read(); _CAP=eval(_s[_s.index('CAP=[')+4:_s.index('KEYW=')].strip())
for t,_ in _CAP:
    k=int(np.argmin([abs(w[1]-t) for w in b]))
    if abs(b[k][1]-t)<=0.15: PS.add(k)
for i in range(len(b)):
    if i not in PS: continue
    t=b[i][1]
    if any(z0<=t<=z1 for z0,z1,_ in zones): continue
    anc.append((t,m[i][1]))
for z0,z1,o in zones: anc+= [(max(0.0001,z0),max(0.0001,z0)+o),(z1,z1+o)]
anc.sort()
# old end: 53.72 -> last word end mapping + same tail
endo=53.72; ende=m[-1][2]+(endo-b[-1][2])
anc=[x for x in anc if x[0]<endo]+[(endo,ende)]
cl=[anc[0]]
for o,n in anc[1:]:
    if o>cl[-1][0]+1e-4 and n>cl[-1][1]+1e-4: cl.append((o,n))
    else: print('drop',o,n)
sl=[(cl[i+1][1]-cl[i][1])/(cl[i+1][0]-cl[i][0]) for i in range(len(cl)-1)]
print('anchors',len(cl),'end new',round(ende,3),'slope min/max',round(min(sl),2),round(max(sl),2))
for z0,z1,o in zones:
    inside=[s for i,s in enumerate(sl) if cl[i][0]>=z0-1e-6 and cl[i+1][0]<=z1+1e-6]; print('zone',z0,z1,'slopes',inside)
json.dump(dict(anc=cl,TOT=round(ende+0.0,3)),open('tmap.json','w'))

import sys; sys.path.insert(0,'/workspace/nuk10/b')
src=open('/workspace/nuk10/b/r.py').read(); i=src.index('CAP=['); j=src.index('KEYW=')
CAP=eval(src[i+4:j].strip())
O=np.array([x[0] for x in cl]); N=np.array([x[1] for x in cl])
errs=[]
for t,sx in CAP:
    k=int(np.argmin([abs(w[1]-t) for w in b]))
    if abs(b[k][1]-t)>0.15: continue
    errs.append((sx,round((np.interp(t,O,N)-(m[k][1]-(b[k][1]-t)))*1000)))
print('caption err ms max',max(abs(e) for _,e in errs),[e for e in errs if abs(e[1])>60])
