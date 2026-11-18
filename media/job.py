# br10 job 5: clips still needed (typing, modem LEDs + sound), then Netscape/IE/Mosaic images; stress check last.
# each file uploaded to the media-br10 pre-release as soon as it is ready.
import json, sys, os, subprocess, urllib.request, urllib.parse, time
out=sys.argv[1]; os.makedirs(out,exist_ok=True); os.makedirs('tmp',exist_ok=True)
UA={'User-Agent':'explainer-video-bot/1.0 (educational shorts; github actions) python-urllib'}
def get(u,t=600,tries=5):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t) as r: return r.read()
        except Exception as e: print('retry',k,u[-70:],e,flush=True); time.sleep(20*(k+1))
    return None
def up(p): subprocess.run(['gh','release','upload','media-br10',p,'--clobber'],check=False)
# ---- Commons media through the API (thumbnail of an image, 720p/1080p transcode of a video)
for r in json.load(open('media/pick.json')):
    k=r['k']; title=r['title']; dst=os.path.join(out,f'c{k}.'+('jpg' if r['kind']=='img' else 'mp4'))
    q=dict(action='query',titles=title,prop='imageinfo|videoinfo',iiprop='url',iiurlwidth=1800,viprop='derivatives',format='json')
    d=json.loads(get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(q)) or b'{}')
    pg=next(iter(d.get('query',{}).get('pages',{}).values()),{})
    if r['kind']=='img':
        u=(pg.get('imageinfo') or [{}])[0].get('thumburl') or r['url']
    else:
        der=(pg.get('videoinfo') or [{}])[0].get('derivatives',[])
        der=[x for x in der if x.get('height',0) and x['height']<=1080 and 'webm' in x.get('type','')]
        der.sort(key=lambda x:-x['height'])
        u=der[0]['src'] if der else r['url']
    print(k,u,flush=True)
    b=get(u); time.sleep(8)
    if b is None: print('SKIP',k,flush=True); continue
    src=f'tmp/c{k}.'+u.split('?')[0].rsplit('.',1)[1]
    open(src,'wb').write(b)
    if r['kind']=='img':
        subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-q:v','2',dst],check=False)
    else:
        args=['ffmpeg','-v','error','-y','-i',src,'-vf',"scale=-2:'min(1080,ih)'",'-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p']
        args+=(['-c:a','aac','-b:a','192k'] if k==233 else ['-an'])
        subprocess.run(args+[dst],check=False)
    if os.path.exists(dst): up(dst)

def stress():
    # ---- stress check first (independent of Commons)
    subprocess.run([sys.executable,'-m','pip','install','-q','--user','torch','--index-url','https://download.pytorch.org/whl/cpu'],check=False)
    subprocess.run([sys.executable,'-m','pip','install','-q','--user','transformers','huggingface_hub'],check=False)
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
    a=np.frombuffer(raw,dtype=np.float32); lines=[]
    for s,e,w,p in words:
        y=a[int(max(0,s-0.04)*16000):int((e+0.05)*16000)]
        if len(y)<1600: y=np.pad(y,(0,1600-len(y)))
        with torch.no_grad(): ids=pm(fe(y,sampling_rate=16000,return_tensors='pt').input_values).logits[0].argmax(-1).numpy()
        ph=[];prev=-1
        for t in ids:
            if t!=prev and t!=0: ph.append(voc[int(t)])
            prev=t
        lines.append(f'{s:6.2f} {w.strip():18s} {" ".join(ph)}')
    open(os.path.join(out,'stress_phones.txt'),'w').write('\n'.join(lines)); up(os.path.join(out,'stress_phones.txt'))
try: stress()
except Exception as ex: print("stress check failed",ex)
