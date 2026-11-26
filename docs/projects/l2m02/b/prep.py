# shots: name -> (clip id tail, start, end, mode). mode 'v' = vertical fill 1080x1920, 'h' = horizontal window (crop non-black, width 1080)
import subprocess,os,sys,glob,json
SRC='/tmp/claude-0/-home-user-explainer-video-releases/1daf0731-67b3-5928-83d9-53622580d33d/scratchpad/l2hq/'
SH={
 'hook':('525460',0.0,4.9,'v'),'hook2':('525460',26.5,29.8,'v'),'tail':('525460',46.0,53.5,'v'),
 'pc_field':('440724',0.0,3.0,'h'),'pc_castle':('440724',11.5,14.8,'h'),'pc_gate':('440724',38.0,41.0,'h'),
 'pc_raid':('728833',3.0,9.6,'h'),'pc_raid2':('728833',18.0,24.8,'h'),
 'mon_phone':('019413',0.0,8.0,'v'),'inv':('019413',8.0,11.0,'v'),'fight':('019413',31.0,38.0,'v'),'crowd':('019413',38.0,44.5,'v'),
 'giran':('341525',7.0,16.0,'h'),'giran2':('341525',28.0,33.5,'h'),
 'same':('262741',20.0,29.5,'v'),'laptop':('094418',0.0,16.5,'v'),
 'andr':('300609',13.0,19.0,'v'),'crit':('300609',26.0,31.5,'v'),'load':('719509',19.5,24.0,'v'),
 'srv':('810706',11.92,12.95,'hc'),'obt':('810706',7.55,8.5,'hc'),'charsel':('810706',0.6,4.8,'hc'),
}
GR="eq=contrast=1.06:saturation=0.95:brightness=-0.01,colorbalance=rs=.02:bs=.05:gs=-.02"
def bbox(f,t):
    out=subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',f,'-t','2','-vf','cropdetect=24:2:0','-f','null','-'],capture_output=True,text=True).stderr
    out=subprocess.run(['ffmpeg','-ss',str(t),'-i',f,'-t','2','-vf','cropdetect=24:2:0','-f','null','-'],capture_output=True,text=True).stderr
    c=[l.split('crop=')[1].strip() for l in out.splitlines() if 'crop=' in l]
    return c[-1] if c else None
only=sys.argv[1:]
meta={}
for n,(cid,a,b,m) in SH.items():
    if only and n not in only: continue
    f=glob.glob(SRC+f'tt_*{cid}.mp4')[0]; d=f'shots/{n}'; os.makedirs(d,exist_ok=True)
    for x in glob.glob(d+'/*.jpg'): os.remove(x)
    if m=='v': vf=f"fps=25,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,{GR},unsharp=5:5:0.5"
    else:
        cr=''
        if m=='hc': cr='crop='+bbox(f,a+0.3)+','
        vf=f"fps=25,{cr}scale=1080:-2:flags=lanczos,{GR},unsharp=5:5:0.7"
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(a),'-i',f,'-t',str(b-a),'-vf',vf,'-q:v','2',d+'/f%04d.jpg'],check=True)
    k=len(glob.glob(d+'/*.jpg')); meta[n]=k; print(n,k,m)
old=json.load(open('shots/meta.json')) if os.path.exists('shots/meta.json') else {}
old.update(meta); json.dump(old,open('shots/meta.json','w'))
