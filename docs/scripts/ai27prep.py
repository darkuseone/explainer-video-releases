# shots for ai27a/ai27b from NASA public-domain footage. usage: python3 ai27prep.py <project b dir> name1 name2 ...
import subprocess,os,sys,glob,json
SRC='/tmp/claude-0/-home-user-explainer-video-releases/1daf0731-67b3-5928-83d9-53622580d33d/scratchpad/ai_src/'
SH={
 'racks':('nasa_sc.mp4',68.5,79.5,'v',0.5),'aisle':('nasa_sc.mp4',129.0,139.0,'v',0.5),'cables':('nasa_sc.mp4',104.5,111.5,'v',0.5),
 'cables2':('nasa_sc.mp4',112.5,119.5,'v',0.5),'board':('nasa_sc.mp4',176.5,187.5,'v',0.5),'board2':('nasa_sc.mp4',188.0,195.0,'v',0.6),
 'earth':('GSFC_20170412_Lights_m12573_EarthAtNight.mp4',23.0,33.0,'v',0.5),'nile':('GSFC_20170412_Lights_m12573_EarthAtNight.mp4',36.0,41.5,'v',0.45),
 'amer':('GSFC_20170412_Lights_m12573_EarthAtNight.mp4',42.5,48.0,'v',0.5),'robot':('ksc_082710_robonaut.mp4',32.0,40.0,'h',0.5),'robot2':('ksc_082710_robonaut.mp4',121.0,127.0,'h',0.5),
}
GR="eq=contrast=1.08:saturation=0.85:brightness=-0.02,colorbalance=rs=.05:bs=.12:gs=-.04:rm=.03:bm=.05,curves=r='0/0.03 1/0.97':b='0/0.05 1/0.96'"
out=sys.argv[1]; only=sys.argv[2:]; meta={}
for n,(f,a,b,m,cx) in SH.items():
    if only and n not in only: continue
    d=f'{out}/shots/{n}'; os.makedirs(d,exist_ok=True)
    for x in glob.glob(d+'/*.jpg'): os.remove(x)
    if m=='v': vf=f"fps=25,scale=-2:1920:flags=lanczos,crop=1080:1920:(iw-1080)*{cx}:0,{GR},unsharp=5:5:0.4"
    else: vf=f"fps=25,scale=1080:-2:flags=lanczos,{GR},unsharp=5:5:0.6"
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(a),'-i',SRC+f,'-t',str(b-a),'-vf',vf,'-q:v','3',d+'/f%04d.jpg'],check=True)
    meta[n]=len(glob.glob(d+'/*.jpg')); print(n,meta[n])
mp=f'{out}/shots/meta.json'; old=json.load(open(mp)) if os.path.exists(mp) else {}
old.update(meta); json.dump(old,open(mp,'w'))
