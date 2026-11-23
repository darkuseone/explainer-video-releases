import json,re
txt=open('/home/user/explainer-video-releases/docs/projects/cd10/voice.txt').read().replace('́','')
txt=re.sub(r'\[[a-z]+\]\s*','',txt)
paras=[p.strip() for p in txt.split('\n\n') if p.strip()]
cps=17.5; gap=0.35; t=0.0; ph=[]; wd=[]
for i,p in enumerate(paras):
    ws=p.split(); t0=t
    for w in ws:
        d=max(0.18,len(w)/cps); wd.append([round(t,3),round(t+d*0.9,3),w,i]); t+=d+0.04
        if w[-1] in '.?…': t+=0.18
    ph.append([round(t0,3),round(t,3)]); t+=gap
json.dump({'phrases':ph,'words':wd,'tot':round(t,2),'avatar':None},open('timeline.json','w'),ensure_ascii=False)
print(ph,t)
