import os,subprocess
from shots import S,TOT
from concurrent.futures import ThreadPoolExecutor
jobs=[]
for k,(t0,key,f,ss,cx,z0,z1) in enumerate(S):
    if f is None or f.endswith('.jpg'): continue
    t1=S[k+1][0] if k+1<len(S) else TOT; d=t1-t0+0.3
    o=f'shots/{k:02d}_{key}'; os.makedirs(o,exist_ok=True)
    vf=f"crop=ih*9/16:ih:(iw-ih*9/16)*{cx}:0,scale=1080:1920:flags=lanczos,fps=25"
    jobs.append(['ffmpeg','-v','error','-y','-ss',str(ss),'-t',str(d),'-i',f,'-vf',vf,'-q:v','2',f'{o}/f%04d.jpg'])
with ThreadPoolExecutor(4) as ex: list(ex.map(subprocess.run,jobs))
for d in sorted(os.listdir('shots')): print(d,len(os.listdir('shots/'+d)))
