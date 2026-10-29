import os,subprocess
from shots import S,TOT
from concurrent.futures import ThreadPoolExecutor
jobs=[]
for k,(t0,src,ss,z0,z1) in enumerate(S):
    t1=S[k+1][0] if k+1<len(S) else TOT; d=t1-t0+0.3
    o=f'shots/{k:02d}_{src}'; os.makedirs(o,exist_ok=True)
    vf="scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=25"
    jobs.append(['ffmpeg','-v','error','-y','-ss',str(ss),'-t',str(d),'-i',f'raw/{src}.mp4','-vf',vf,'-q:v','2',f'{o}/f%04d.jpg'])
with ThreadPoolExecutor(6) as ex: list(ex.map(subprocess.run,jobs))
for d in sorted(os.listdir('shots')): print(d,len(os.listdir('shots/'+d)))
