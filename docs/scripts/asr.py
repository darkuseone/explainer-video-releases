import subprocess,json,numpy as np,sys
from faster_whisper import WhisperModel
m=WhisperModel("medium",device="cpu",compute_type="int8")
raw=subprocess.run(["ffmpeg","-v","quiet","-i",sys.argv[1],"-f","f32le","-ac","1","-ar","16000","-"],capture_output=True).stdout
a=np.frombuffer(raw,dtype=np.float32); out=[]
B=[float(x) for x in sys.argv[3].split(',')]+[len(a)/16000+1]; B=[0]+B
for k in range(len(B)-1):
    s=a[int(B[k]*16000):int(B[k+1]*16000)]
    segs,_=m.transcribe(s,language="ru",word_timestamps=True,beam_size=5,condition_on_previous_text=False)
    out+=[(round(w.start+B[k],2),round(w.end+B[k],2),w.word) for sg in segs for w in sg.words]
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False)
print(" ".join(f"{a}:{w}" for a,b,w in out))
