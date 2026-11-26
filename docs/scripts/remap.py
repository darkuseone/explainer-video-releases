# Remap timeline.json words and av_meta.json through an EDL map. usage: python3 remap.py map.json tl_in tl_out av_in av_out vo_out.wav [ИИ=AI ...]
import sys,json,wave
mp=json.load(open(sys.argv[1])); tl=json.load(open(sys.argv[2])); av=json.load(open(sys.argv[4]))
subs=dict(s.split('=',1) for s in sys.argv[7:])
def M(t):
    for (o0,n0),(o1,n1) in zip(mp,mp[1:]):
        if o0<=t<=o1: return n0 if o1==o0 else n0+(n1-n0)*(t-o0)/(o1-o0)
    return mp[-1][1]
def incut(t):
    return any(o0<t<o1 and n0==n1 for (o0,n0),(o1,n1) in zip(mp,mp[1:]))
words=[]
for a,b,w,p in tl['words']:
    if incut((a+b)/2): continue
    for k,v in subs.items(): w=w.replace(k,v)
    words.append([round(M(a),3),round(M(b),3),w,p])
paras=sorted(set(w[3] for w in words)); ren={p:i for i,p in enumerate(paras)}
words=[[a,b,w,ren[p]] for a,b,w,p in words]
ph=[[min(w[0] for w in words if w[3]==k),max(w[1] for w in words if w[3]==k)] for k in range(len(paras))]
v=wave.open(sys.argv[6]); tot=v.getnframes()/v.getframerate()
json.dump({'phrases':ph,'words':words,'tot':round(tot,3)},open(sys.argv[3],'w'),ensure_ascii=False)
nav=[]
cuts=[(o0,o1) for (o0,n0),(o1,n1) in zip(mp,mp[1:]) if n0==n1 and o1>o0]
for s in av:
    pieces=[(s['t0'],s['t1'])]
    for c0,c1 in cuts:
        nxt=[]
        for a,b in pieces:
            if c1<=a or c0>=b: nxt.append((a,b)); continue
            if a<c0: nxt.append((a,c0))
            if c1<b: nxt.append((c1,b))
        pieces=nxt
    for a,b in pieces:
        if b-a<0.25: continue
        nav.append({'t0':round(M(a),4),'t1':round(M(b),4),'src0':round(s['src0']+(a-s['t0']),4)})
json.dump(nav,open(sys.argv[5],'w')); print('paras kept',paras,'tot',round(tot,3)); print('av',nav)
