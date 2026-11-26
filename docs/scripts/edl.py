# Audio EDL on an existing voice take: cuts and word replacements (natural length), energy-refined boundaries.
# usage: python3 edl.py vo_in.wav ops.json vo_out.wav map.json [patch.wav]
# ops: [{"a":s,"b":e,"cut":true} | {"a":s,"b":e,"pa":s,"pb":e}] in vo_in time; map.json: [[orig_t,new_t],...] breakpoints (piecewise linear, cuts collapse)
import sys,json,wave,numpy as np
def rd(p):
    w=wave.open(p); sr=w.getframerate(); return np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32),sr
def wr(p,x,sr):
    o=wave.open(p,'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes(np.clip(x,-32768,32767).astype(np.int16).tobytes()); o.close()
vin,ops_p,vout,mapp=sys.argv[1:5]; x,sr=rd(vin); P=None
if len(sys.argv)>5: P,sr2=rd(sys.argv[5]); assert sr2==sr
ops=sorted(json.load(open(ops_p)),key=lambda o:o['a'])
def refine(sig,b,win=0.06):
    h=int(0.005*sr); a0=int((b-win)*sr); a1=int((b+win)*sr); best=None
    for s in range(max(0,a0),min(len(sig)-h,a1),h):
        e=float(np.sqrt(np.mean(sig[s:s+h]**2)))
        if best is None or e<best[0]: best=(e,s+h//2)
    return best[1]/sr
f=int(0.010*sr); out=[]; mp=[[0.0,0.0]]; pos=0.0; newt=0.0
def emit(seg):
    global newt
    out.append(seg); newt+=len(seg)/sr
for o in ops:
    a=refine(x,o['a'],0.1 if o.get('cut') else 0.06); b=refine(x,o['b'],0.1 if o.get('cut') else 0.06)
    keep=x[int(pos*sr):int(a*sr)].copy()
    if len(keep)>2*f: keep[-f:]*=np.linspace(1,0,f)
    if out and len(keep)>2*f: keep[:f]*=np.linspace(0,1,f)
    emit(keep); mp.append([a,newt])
    if o.get('cut'):
        mp.append([b,newt])
    else:
        pa=refine(P,o['pa']); pb=refine(P,o['pb']); seg=P[int(pa*sr):int(pb*sr)].copy()
        orig=x[int(a*sr):int(b*sr)]; g=np.sqrt(np.mean(orig**2))/max(1e-6,np.sqrt(np.mean(seg**2))); seg*=g
        seg[:f]*=np.linspace(0,1,f); seg[-f:]*=np.linspace(1,0,f)
        emit(seg); mp.append([b,newt]); print('repl',round(a,3),round(b,3),'->',round(pb-pa,3),'s gain',round(float(g),2))
    pos=b
tail=x[int(pos*sr):].copy()
if len(tail)>2*f: tail[:f]*=np.linspace(0,1,f)
emit(tail); mp.append([len(x)/sr,newt])
wr(vout,np.concatenate(out),sr); json.dump(mp,open(mapp,'w')); print('dur',round(len(x)/sr,3),'->',round(newt,3))
