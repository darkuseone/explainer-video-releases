# words_asr.json -> timeline.json {phrases, words[t0,t1,display,para], tot}
import json,wave,sys
W=json.load(open('../v/words_asr.json'))
cut=next(i for i,w in enumerate(W) if w[2].startswith('древнее'))
W=W[:cut+1]
FIX={'геран':'Гиран','гиран':'Гиран','скилы':'скиллы','ncsoft':'NCSoft','2m.':'2M.','интерлюд':'Интерлюд','нее':'неё','еще':'ещё','2000х,':'2000-х,'}
starts=['Это','В','Официальные','А','И','Сколько','Но','Мобильный','Напиши']
words=[];p=-1;si=0
for i,(a,b,w,pr) in enumerate(W):
    if si<len(starts) and w.strip(',.')==starts[si] and (si==0 or a-W[i-1][1]>0.15 or W[i-1][2][-1] in '.?!'):
        p=si; si+=1
    k=w.lower()
    w=FIX.get(k,FIX.get(k.strip(',.'),w.strip(',.'))+(w[len(w.rstrip(',.!?')):] if k.strip(',.') in FIX else '')) if (k in FIX or k.strip(',.') in FIX) else w
    words.append([a,b,w,p])
# merge "2 ,8"
out=[]
for w in words:
    if w[2].startswith(',') and out and out[-1][2].isdigit(): out[-1][2]+=w[2]; out[-1][1]=w[1]; continue
    out.append(w)
words=out
assert si==len(starts),si
ph=[[min(w[0] for w in words if w[3]==k),max(w[1] for w in words if w[3]==k)] for k in range(len(starts))]
wv=wave.open('../v/vo.wav'); tot=wv.getnframes()/wv.getframerate()
json.dump({'phrases':ph,'words':words,'tot':round(tot,3)},open('timeline.json','w'),ensure_ascii=False)
for k,(a,b) in enumerate(ph): print(k,round(a,2),round(b,2),' '.join(w[2] for w in words if w[3]==k))
