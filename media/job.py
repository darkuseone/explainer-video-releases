# br10 job 1: fetch VO + word timestamps; search Commons/NASA for footage (metadata + thumbs only).
import json, sys, os, subprocess, urllib.request, urllib.parse, time, zipfile
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
UA={'User-Agent':'explainer-video-bot/1.0 (media research; github actions)'}
def get(u,t=120):
    with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t) as r: return r.read()
VO='https://elevenlabsusercontent.com/database/workspace/424067ba319c47ccbff0e28903f7041c/content_generation/XjuAG7SEdAm46R6kjz15/x4yjbdv7qQiHZi7Q3WKY/content.mp3?Expires=1795039200&KeyName=assets-cdn-key-1&Signature=-sko9Z8LChy2Li0sxJx45wQt1GI='
open(os.path.join(out,'vo_raw.mp3'),'wb').write(get(VO,300))
# --- search
idx=[]; thumbs=os.path.join(out,'th'); os.makedirs(thumbs,exist_ok=True)
def commons(q,video=False,n=12):
    s=q+(' filetype:video' if video else ' filetype:bitmap')
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(dict(action='query',generator='search',gsrnamespace=6,gsrsearch=s,gsrlimit=n,prop='imageinfo',iiprop='url|size|mime|extmetadata',iiurlwidth=480,format='json'))
    try: d=json.loads(get(u))
    except Exception as e: print('ERR',q,e); return
    for p in (d.get('query',{}).get('pages',{}) or {}).values():
        ii=p['imageinfo'][0]; m=ii.get('extmetadata',{})
        r=dict(src='commons',q=q,title=p['title'],url=ii['url'],w=ii.get('width'),h=ii.get('height'),mime=ii.get('mime'),dur=ii.get('duration'),
               lic=m.get('LicenseShortName',{}).get('value'),artist=(m.get('Artist',{}).get('value') or '')[:200],thumb=ii.get('thumburl'))
        k=len(idx); r['k']=k; idx.append(r)
        try: open(os.path.join(thumbs,f'c{k:03d}.jpg'),'wb').write(get(r['thumb'],60))
        except Exception as e: print('thumb err',e)
        time.sleep(0.5)
for q in ['Tim Berners-Lee','First Web Server NeXT CERN','NeXTcube computer','WorldWideWeb browser screenshot','NCSA Mosaic browser','Marc Andreessen','Netscape Navigator','Internet Explorer 1.0','CERN Meyrin aerial','Windows 95 desktop','dial-up modem','CERN Computer Centre','Berners-Lee proposal information management']:
    commons(q)
for q in ['data center','server room','fiber optic','CERN','internet','typing keyboard','computer network','stock exchange trading floor','Earth night city lights','hard disk','modem','globe rotating']:
    commons(q,True,10)
def nasa(q,n=8):
    u='https://images-api.nasa.gov/search?'+urllib.parse.urlencode(dict(q=q,media_type='video'))
    try: d=json.loads(get(u))
    except Exception as e: print('ERR',q,e); return
    for it in d['collection']['items'][:n]:
        dd=it['data'][0]; th=[l['href'] for l in it.get('links',[]) if l.get('render')=='image']
        r=dict(src='nasa',q=q,id=dd['nasa_id'],title=dd.get('title'),desc=(dd.get('description') or '')[:200],thumb=th[0] if th else None)
        k=len(idx); r['k']=k; idx.append(r)
        if r['thumb']:
            try: open(os.path.join(thumbs,f'c{k:03d}.jpg'),'wb').write(get(r['thumb'].replace(' ','%20'),60))
            except Exception as e: print('thumb err',e)
for q in ['city lights night ISS timelapse','Earth at night','supercomputer','Pleiades supercomputer','data visualization network']:
    nasa(q)
json.dump(idx,open(os.path.join(out,'index.json'),'w'),ensure_ascii=False,indent=1)
with zipfile.ZipFile(os.path.join(out,'thumbs.zip'),'w') as z:
    for f in sorted(os.listdir(thumbs)): z.write(os.path.join(thumbs,f),f)
import shutil; shutil.rmtree(thumbs)
# --- words
subprocess.run([sys.executable,'-m','pip','install','-q','--user','faster-whisper==1.1.1'],check=True)
import site,importlib; site.addsitedir(site.getusersitepackages()); importlib.invalidate_caches()
from faster_whisper import WhisperModel
import numpy as np
m=WhisperModel("medium",device="cpu",compute_type="int8")
raw=subprocess.run(["ffmpeg","-v","quiet","-i",os.path.join(out,'vo_raw.mp3'),"-f","f32le","-ac","1","-ar","16000","-"],capture_output=True).stdout
a=np.frombuffer(raw,dtype=np.float32)
segs,_=m.transcribe(a,language="ru",word_timestamps=True,beam_size=5,condition_on_previous_text=False)
w=[(round(x.start,3),round(x.end,3),x.word,round(x.probability,3)) for s in segs for x in s.words]
json.dump(w,open(os.path.join(out,'vo_words.json'),'w'),ensure_ascii=False)
