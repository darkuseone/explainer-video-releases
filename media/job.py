# dim10 v2: fetch re-voiced phrase "куда не показывает ни одна стрелка" + word timestamps.
import json, sys, os, subprocess, urllib.request
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
u='https://elevenlabsusercontent.com/database/workspace/424067ba319c47ccbff0e28903f7041c/content_generation/AlkZ4INAAvCE2c1Ybcrn/EvXZ3yppGdXqMWzMcTKb/content.mp3?Expires=1794978000&KeyName=assets-cdn-key-1&Signature=gwDDvMjbfT0-OxNTd_eeDtFxdM8='
with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=300) as r: open(os.path.join(out,'strelka.mp3'),'wb').write(r.read())
subprocess.run([sys.executable,'-m','pip','install','-q','--user','faster-whisper==1.1.1'],check=True)
import site,importlib; site.addsitedir(site.getusersitepackages()); importlib.invalidate_caches()
from faster_whisper import WhisperModel
import numpy as np
m=WhisperModel("medium",device="cpu",compute_type="int8")
raw=subprocess.run(["ffmpeg","-v","quiet","-i",os.path.join(out,'strelka.mp3'),"-f","f32le","-ac","1","-ar","16000","-"],capture_output=True).stdout
a=np.frombuffer(raw,dtype=np.float32)
segs,_=m.transcribe(a,language="ru",word_timestamps=True,beam_size=5,condition_on_previous_text=False)
w=[(round(x.start,3),round(x.end,3),x.word,round(x.probability,3)) for s in segs for x in s.words]
json.dump(w,open(os.path.join(out,'strelka_words.json'),'w'),ensure_ascii=False); print(w)
