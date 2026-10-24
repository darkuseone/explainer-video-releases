import sys,re,json,unicodedata,numpy as np,soundfile as sf
sys.path.insert(0,'/workspace/nuk10/v2'); sys.path.insert(0,'/workspace/nuk10/v')
from stress_eval import words_times, plain
txt=open('/workspace/nuk10/script.md').read()
t=re.sub(r'[^\w\s\-]',' ',plain(txt).lower()).replace('-',' ')
# 1) splice P3 in place of sentence 1 of F1
import subprocess
for k in ['F1','P3']: subprocess.run(f'ffmpeg -v error -y -i {k}.mp3 -ar 44100 -ac 1 {k}_44.wav',shell=True)
wF=words_times('F1.wav',t)
i=[j for j,w in enumerate(wF) if w[0]=='хиросима'][0]
cutF=wF[i][1]-0.06
p3,sr=sf.read('P3_44.wav'); f1,_=sf.read('F1_44.wav')
# trim P3 tail silence
e=np.where(np.abs(p3)>0.01)[0][-1]+int(0.05*sr)
gap=np.zeros(int(0.35*sr))
y=np.concatenate([p3[:e],gap,f1[int(cutF*sr):]])
sf.write('new_raw.wav',y,sr); print('spliced',len(y)/sr, 'cut F1 at',cutF)
