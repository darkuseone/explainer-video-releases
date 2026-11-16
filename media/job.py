# wh10 v2: download chosen NASA videos (public domain), 1080p, no audio, <=120 s, plus contact sheets.
# v2
import json, sys, os, subprocess, urllib.request
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
def get(u,t=600):
    with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=t) as r: return r.read()
B='https://images-assets.nasa.gov/video/%s/%s~%s.mp4'
CH=['JPL-20250409-NUSTARf-0001-Hunting_Hidden_Black_Holes_2160cc','GSFC_20100126_Nova_m10547_SuperNova','301_BlackHoles','GSFC_20181010_FERMI_m13058_Pulsar4K','GSFC_20080520_HST_m10223_COS','307_ISS-Finding-the-Invisible','GSFC_20181108_FERMI_m13042_Luck4K','GSFC_20181002_SMBH_m13043_Simulation']
for i,n in enumerate(CH):
    src=None
    for q in ('large','medium','orig'):
        try: open('/tmp/v.mp4','wb').write(get(B%(n,n,q))); src='/tmp/v.mp4'; break
        except Exception as e: print('miss',n,q,e)
    if not src: continue
    o=os.path.join(out,'nv%02d.mp4'%i)
    subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-t','120','-an','-vf','scale=-2:1080','-c:v','libx264','-crf','18','-preset','veryfast',o])
    subprocess.run(['ffmpeg','-v','error','-y','-i',o,'-vf','fps=1/2,scale=240:-2,tile=6x10','-frames:v','1',os.path.join(out,'nv%02d_sheet.jpg'%i)])
    print(i,n,os.path.getsize(o))
