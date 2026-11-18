# br10 job 2: avatar audio to release; download chosen Commons footage/photos; stress check of VO by phoneme CTC.
import json, sys, os, subprocess, urllib.request, time, shutil
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
UA={'User-Agent':'explainer-video-bot/1.0 (media research; github actions)'}
def get(u,t=600,tries=7,fatal=True):
    u=u.split('?')[0] if 'wikimedia' in u else u
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t) as r: return r.read()
        except Exception as e: print('retry',k,u[-60:],e); time.sleep(30*(k+1))
    if fatal: raise SystemExit('fail '+u)
    return None
time.sleep(60)
shutil.copy('media/br10_av_audio.mp3',os.path.join(out,'br10_av_audio.mp3'))
os.makedirs('tmp',exist_ok=True)
for r in json.load(open('media/pick.json')):
    k=r['k']; ext=r['url'].rsplit('.',1)[1].lower(); src=f'tmp/c{k}.{ext}'
    b=get(r['url'],fatal=False); time.sleep(10)
    if b is None: print('SKIP',k); continue
    open(src,'wb').write(b)
    if r['kind']=='img':
        subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-vf',"scale='min(2400,iw)':-2",'-q:v','2',os.path.join(out,f'c{k}.jpg')],check=True)
    else:
        args=['ffmpeg','-v','error','-y','-i',src,'-vf',"scale=-2:'min(1080,ih)'",'-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p']
        args+=(['-c:a','aac','-b:a','192k'] if k==233 else ['-an'])
        subprocess.run(args+[os.path.join(out,f'c{k}.mp4')],check=True)
json.dump(json.load(open('media/pick.json')),open(os.path.join(out,'pick.json'),'w'),ensure_ascii=False,indent=1)
# ---- stress check
subprocess.run([sys.executable,'-m','pip','install','-q','--user','torch==2.5.1','--index-url','https://download.pytorch.org/whl/cpu'],check=True)
subprocess.run([sys.executable,'-m','pip','install','-q','--user','transformers==4.46.3','soundfile','huggingface_hub'],check=True)
import site,importlib; site.addsitedir(site.getusersitepackages()); importlib.invalidate_caches()
import numpy as np, torch
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForCTC
from huggingface_hub import hf_hub_download
M='facebook/wav2vec2-xlsr-53-espeak-cv-ft'
fe=Wav2Vec2FeatureExtractor.from_pretrained(M); pm=Wav2Vec2ForCTC.from_pretrained(M).eval()
voc={v:k for k,v in json.load(open(hf_hub_download(M,'vocab.json'))).items()}
open('tmp/vo.mp3','wb').write(get('https://github.com/darkuseone/explainer-video-releases/releases/download/media-br10/vo_raw.mp3'))
words=json.loads(get('https://github.com/darkuseone/explainer-video-releases/releases/download/media-br10/vo_words.json'))
raw=subprocess.run(["ffmpeg","-v","quiet","-i",'tmp/vo.mp3',"-f","f32le","-ac","1","-ar","16000","-"],capture_output=True).stdout
a=np.frombuffer(raw,dtype=np.float32)
lines=[]
for i,(s,e,w,p) in enumerate(words):
    s0=max(0,s-0.04); e0=e+0.05
    y=a[int(s0*16000):int(e0*16000)]
    if len(y)<1600: y=np.pad(y,(0,1600-len(y)))
    x=fe(y,sampling_rate=16000,return_tensors='pt').input_values
    with torch.no_grad(): ids=pm(x).logits[0].argmax(-1).numpy()
    ph=[];prev=-1
    for t in ids:
        if t!=prev and t!=0: ph.append(voc[int(t)])
        prev=t
    lines.append(f'{s:6.2f} {w.strip():18s} {" ".join(ph)}')
open(os.path.join(out,'stress_phones.txt'),'w').write('\n'.join(lines)); print('\n'.join(lines))
