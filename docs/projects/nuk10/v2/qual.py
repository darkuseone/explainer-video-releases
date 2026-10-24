import json,sys
R=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'ab_res.json'))
RUV='аеёиоуыэюя'
def vq(ph):
    vs=[p for p in ph.split() if any(c in 'aeiouyɪəɐɨʊɛɔæɑʌ' for c in p)]
    return vs
def judge(word,exp,ph):
    lv=[c for c in word if c in RUV]; pv=vq(ph)
    if len(lv)!=len(pv): return None,'count'
    verdicts=[]
    for i,(l,p) in enumerate(zip(lv,pv)):
        st=(i==exp)
        if l=='о': verdicts.append(('o' in p)==st)
        elif (l=='е' and not word.startswith('е')) or (l=='я' and i>0):
            if st: verdicts.append(p[0] in 'eɛaæ')
            else: verdicts.append(p[0] in 'iɪəɨ' or (l=='я' and p[0] in 'aə' and i==len(lv)-1))
    if not verdicts: return None,'nodiag'
    return all(verdicts),''
tot={}
for k,rows in R.items():
    g=b=n=0;bad=[]
    for w,exp,got,ph,ok in rows:
        r,why=judge(w,exp,ph)
        if r is None: n+=1
        elif r: g+=1
        else: b+=1;bad.append(w+':'+ph.replace(' ',''))
    print(f'{k:4} good {g} bad {b} undiag {n}  ',' '.join(bad))
