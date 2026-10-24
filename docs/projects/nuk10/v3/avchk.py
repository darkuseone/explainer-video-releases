import json,numpy as np
m=json.load(open('meas.json')); c=json.load(open('cut.json')); W=json.load(open('../v2/full/wt.json')); b=W['v1']
M=json.load(open('/workspace/nuk10/av/meta.json')); R={}
for k in M:
    t0,t1=M[k]['t0'],M[k]['t1']; o=c['off'][k]
    d=[(b[i][0],round((m[i][1]-(b[i][1]+o))*1000)) for i in range(len(b)) if t0<=b[i][1]<=t1]
    R[k]=dict(off=o,max=max(abs(x[1]) for x in d),mean=round(sum(abs(x[1]) for x in d)/len(d)),big=[x for x in d if abs(x[1])>60])
    print(k,R[k])
json.dump(R,open('avsync.json','w'),ensure_ascii=False)
e=[m[i][1]-c['outw'][i][1] for i in range(len(m))]; print('plan vs meas mean',round(np.mean(np.abs(e))*1000),'max',round(np.max(np.abs(e))*1000))
