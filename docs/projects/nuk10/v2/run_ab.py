import sys,glob,os,json;sys.path.insert(0,'/workspace/nuk10/v2')
from stress_eval import analyse
T=[('расколоть',2),('землю',0),('квинтиллиона',3),('хиросим',2),('энергия',1),('раскола',1),('земли',1),('дорога',1),('квадриллион',3),('астероид',2),('чиксулуб',2),('мощнее',1),('арсенала',2),('земля',1),('ядерная',0),('зима',1),('оставит',1),('еды',1),('больше',0),('пяти',1),('миллиардов',2),('человек',2),('атмосфера',2)]
text=open('A.txt').read()
res={}
for f in sorted(glob.glob('*.mp3')):
    k=f[:-4]; os.system(f'ffmpeg -v error -y -i {f} -ar 16000 -ac 1 {k}.wav')
    rows=analyse(k+'.wav',text,T); res[k]=rows
    ok=sum(1 for r in rows if r[2]==r[1]); val=sum(1 for r in rows if r[4])
    print(k,'acoustic_hit',ok,'/',len(rows),'vowelcount_ok',val)
    for r in rows: print('   ',r[0],r[1],r[2],'|',r[3])
json.dump(res,open('ab_res.json','w'),ensure_ascii=False,indent=0)
