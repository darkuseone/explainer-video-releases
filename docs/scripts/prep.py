import os,subprocess
from concurrent.futures import ThreadPoolExecutor
F='/workspace/nuke/footage/'; OUT='/workspace/nuke/b/shots/'
GR="eq=contrast=1.1:saturation={sat}:brightness=-0.02,colorbalance=rs=.07:bs=.13:gs=-.05:rm=.04:bm=.05:rh=.04:bh=0,curves=r='0/0.03 1/0.97':b='0/0.05 1/0.96',unsharp=5:5:0.4"
J=[('bill','px_6253877.mp4',0.5,3.0,.8),('clips','px_6176561.mp4',1.0,3.0,.8),('match','px_8618706.mp4',4.0,3.0,.85)]
def ex(j):
    sid,src,ss,dur,sat=j; d=OUT+sid+'/'; os.makedirs(d,exist_ok=True)
    vf="framerate=fps=25:interp_start=0:interp_end=255:scene=100,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,"+GR.format(sat=sat)
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(ss),'-i',F+src,'-t',str(dur),'-vf',vf,'-q:v','2',d+'f%04d.jpg'],check=True); print(sid,len(os.listdir(d)))
with ThreadPoolExecutor(4) as p: list(p.map(ex,J))
