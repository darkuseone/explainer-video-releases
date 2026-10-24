import sys,json; sys.path.insert(0,'/workspace/nuk10/v')
from align import align
W=json.load(open('/workspace/nuk10/v2/full/wt.json'))
words=[w[0] for w in W['new']]; res=align(sys.argv[1],' '.join(words))
out=[];cur=[]
for ch,s,e in res+[(' ',0,0)]:
    if ch==' ':
        if cur: out.append([''.join(c for c,_,_ in cur),cur[0][1],cur[-1][2]]); cur=[]
    else: cur.append((ch,s,e))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False); print(len(out),len(words))
