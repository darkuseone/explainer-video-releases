import sys,json
from faster_whisper import WhisperModel
m=WhisperModel('medium',device='cpu',compute_type='int8')
import soundfile as sf,numpy as np,scipy.signal as ss
y,sr=sf.read(sys.argv[1]); y=y.mean(1) if y.ndim>1 else y; y=ss.resample_poly(y,16000,sr).astype(np.float32)
seg,_=m.transcribe(y,language='ru',word_timestamps=True,beam_size=5,condition_on_previous_text=False)
W=[]
for s in seg:
    for w in s.words: W.append((round(w.start,2),round(w.end,2),w.word.strip()))
json.dump(W,open(sys.argv[2],'w'),ensure_ascii=False)
print(' '.join(f'{a}:{w}' for a,b,w in W))
