# dim10: download chosen NASA videos (public domain) + Commons hose clip; 1080p, no audio, <=120 s, contact sheets.
import json, sys, os, subprocess, urllib.request, urllib.parse
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
def get(u,t=900):
    with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'dim10-footage/1.0'}),timeout=t) as r: return r.read()
CH=['Earth Views from the International Space Station','NHQ_2019_0626_Earth Views from the ISS','jsc2022m000270_Orion_First_Imagery_Timelapse_and_Original_221117','lunarflyby_1min_2160p30','GSFC_20181002_SMBH_m13043_Simulation','GSFC_20181108_FERMI_m13042_Luck4K','20190530-SPITZRf-0001-Stars of Cephus','jsc2026m000120_How_Does_NASA_Study_Vision_and_Cognitive_Changes_in_Space_260611','GSFC_20181129_FERMI_m13104_Starlight']
src={}
for n in CH:
    try:
        man=json.loads(get('https://images-api.nasa.gov/asset/'+urllib.parse.quote(n)))['collection']['items']
        mp=[i['href'] for i in man if i['href'].endswith('.mp4')]
        pick=next((u for k in ('~large','~medium','~orig') for u in mp if k in u),mp[0] if mp else None)
        print(n,'->',pick); src[n]=pick.replace('http://','https://').replace(' ','%20')
    except Exception as e: print('ERR',n,e)
src['hose']='https://upload.wikimedia.org/wikipedia/commons/b/bb/Hose_filling_Pool_1_2017-07-24.webm'
meta={}
for i,(n,u) in enumerate(src.items()):
    try: open('/tmp/v.bin','wb').write(get(u))
    except Exception as e: print('miss',n,e); continue
    o=os.path.join(out,'nv%02d.mp4'%i); meta['nv%02d'%i]={'id':n,'url':u}
    subprocess.run(['ffmpeg','-v','error','-y','-i','/tmp/v.bin','-t','150','-an','-vf','scale=-2:1080','-c:v','libx264','-crf','17','-preset','veryfast',o])
    subprocess.run(['ffmpeg','-v','error','-y','-i',o,'-vf','fps=1/2,scale=240:-2,tile=6x13','-frames:v','1',os.path.join(out,'nv%02d_sheet.jpg'%i)])
    print(i,n,os.path.getsize(o))
json.dump(meta,open(os.path.join(out,'footage_meta.json'),'w'),indent=1)
