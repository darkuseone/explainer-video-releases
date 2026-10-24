import sys,re,unicodedata,json
sys.path.insert(0,'/workspace/nuk10/v2')
from stress_eval import analyse
wav,txt=sys.argv[1],open(sys.argv[2]).read()
RUV='аеёиоуыэюя'
tg=[]
for w in re.findall(r"[\w\u0301]+",txt.replace('-',' ')):
    lw=w.lower(); p=lw.replace('\u0301','')
    if sum(c in RUV for c in p)<2: continue
    if '\u0301' in lw: k=lw.index('\u0301'); exp=sum(c in RUV for c in lw[:k])-1
    elif 'ё' in p: exp=sum(c in RUV for c in p[:p.index('ё')])
    else: continue
    tg.append((p,exp))
rows=analyse(wav,txt,tg)
json.dump(rows,open(sys.argv[3],'w'),ensure_ascii=False)
for r in rows: print(r)
