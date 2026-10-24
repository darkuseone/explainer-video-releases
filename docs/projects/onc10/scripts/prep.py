import os,subprocess
from concurrent.futures import ThreadPoolExecutor
F='/workspace/onc10/footage/'; OUT='/workspace/onc10/b/shots/'
GR="eq=contrast=1.07:saturation=0.85:brightness=-0.03,colorbalance=rs=-.02:bs=.06:gs=.0:rh=.03:bh=.02,unsharp=5:5:0.3"
ids=['5453585','5722113','5883925','6236757','8326121','8460389','8670930','8852383','8852657','8852695']
def ex(i):
    d=OUT+i+'/'; os.makedirs(d,exist_ok=True)
    vf="fps=25,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,"+GR
    subprocess.run(['ffmpeg','-v','error','-y','-ss','0.3','-i',F+'px_'+i+'.mp4','-t','10','-vf',vf,'-q:v','2',d+'f%04d.jpg'],check=True); print(i,len(os.listdir(d)),flush=True)
with ThreadPoolExecutor(5) as p: list(p.map(ex,ids))
