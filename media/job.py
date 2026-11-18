# dim10: download both VO takes, word timestamps with faster-whisper medium (CPU int8).
import json, sys, os, subprocess, urllib.request
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
U={'voA.mp3':'https://elevenlabsusercontent.com/database/workspace/424067ba319c47ccbff0e28903f7041c/content_generation/ng1IgOHQ8joWSz2wvoXz/uKAtR4AIYCAXQJEQL1CC/content.mp3?Expires=1794970800&KeyName=assets-cdn-key-1&Signature=PTbnUHrSEI3gFLaQ1hZFrL1yXzE=',
   'voB.mp3':'https://elevenlabsusercontent.com/database/workspace/424067ba319c47ccbff0e28903f7041c/content_generation/GcdH7tPc5vn3NoAl17p1/7RtrLC53pNTpgEBoWpvI/content.mp3?Expires=1794970800&KeyName=assets-cdn-key-1&Signature=WM-G7LtgpwRDmFHbMnjMQ4B2f9U='}
for n,u in U.items():
    with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=300) as r: open(os.path.join(out,n),'wb').write(r.read())
subprocess.run([sys.executable,'-m','pip','install','-q','faster-whisper==1.1.1'],check=True)
from faster_whisper import WhisperModel
import numpy as np
m=WhisperModel("medium",device="cpu",compute_type="int8")
for n in U:
    raw=subprocess.run(["ffmpeg","-v","quiet","-i",os.path.join(out,n),"-f","f32le","-ac","1","-ar","16000","-"],capture_output=True).stdout
    a=np.frombuffer(raw,dtype=np.float32)
    segs,_=m.transcribe(a,language="ru",word_timestamps=True,beam_size=5,condition_on_previous_text=False)
    w=[(round(x.start,3),round(x.end,3),x.word,round(x.probability,3)) for s in segs for x in s.words]
    json.dump(w,open(os.path.join(out,n.replace('.mp3','_words.json')),'w'),ensure_ascii=False)
    print(n,' '.join(x[2] for x in w))
