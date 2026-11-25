# Map display text (voice_final.txt, paragraphs = phrases) onto ASR word timings (words_asr.json) by char-level alignment.
# usage: python3 align_disp.py voice_final.txt words_asr.json vo.wav timeline.json
import sys,json,re,wave,difflib
NUM={'0':'ноль'}
def norm(s): return re.sub(r'[^0-9a-zа-яё]','',s.lower().replace('ё','е'))
txt,asr,wav,out=sys.argv[1:5]
paras=[p.split() for p in open(txt).read().split('\n\n') if p.strip()]
A=json.load(open(asr))
# drop zero-length hallucinated tail
while A and A[-1][1]-A[-1][0]<0.03: A.pop()
ac=[];at=[]
for a,b,w,*_ in A:
    n=norm(w)
    for k,c in enumerate(n): ac.append(c); at.append(a+(b-a)*k/max(1,len(n)))
dw=[];dc=[];own=[]
for pi,p in enumerate(paras):
    for w in p:
        n=norm(w); dw.append([w,pi,len(dc),len(dc)+len(n)]); dc+=list(n)
sm=difflib.SequenceMatcher(None,dc,ac,autojunk=False)
mp={}
for i,j,n in sm.get_matching_blocks():
    for k in range(n): mp[i+k]=at[j+k]
idx=sorted(mp)
def tat(i):
    if i in mp: return mp[i]
    lo=max([x for x in idx if x<i],default=None); hi=min([x for x in idx if x>i],default=None)
    if lo is None: return mp[hi]
    if hi is None: return mp[lo]
    return mp[lo]+(mp[hi]-mp[lo])*(i-lo)/(hi-lo)
words=[]
for w,pi,s,e in dw:
    t0=tat(s); t1=tat(e-1)+0.08 if e>s else t0+0.2
    words.append([round(t0,3),round(max(t1,t0+0.06),3),w,pi])
for k in range(len(words)-1):
    words[k][1]=min(words[k][1],max(words[k][0]+0.05,words[k+1][0]))
words[-1][1]=max(words[-1][1],A[-1][1])
ph=[[min(w[0] for w in words if w[3]==k),max(w[1] for w in words if w[3]==k)] for k in range(len(paras))]
v=wave.open(wav); tot=v.getnframes()/v.getframerate()
json.dump({'phrases':ph,'words':words,'tot':round(tot,3)},open(out,'w'),ensure_ascii=False)
for k,(a,b) in enumerate(ph): print(k,round(a,2),round(b,2),' '.join(w[2] for w in words if w[3]==k)[:90])
