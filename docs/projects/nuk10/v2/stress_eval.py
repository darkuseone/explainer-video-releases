# Objective stress check: word windows from forced alignment (ru char CTC),
# vowel nuclei from espeak phoneme CTC (vowel quality shows reduction),
# prominence = vowel duration * RMS * F0 from parselmouth.
import sys, json, re, unicodedata, numpy as np, soundfile as sf, torch, torchaudio, parselmouth
sys.path.insert(0,'/workspace/nuk10/v')
from align import align
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForCTC
M='facebook/wav2vec2-xlsr-53-espeak-cv-ft'
fe=Wav2Vec2FeatureExtractor.from_pretrained(M); pm=Wav2Vec2ForCTC.from_pretrained(M).eval()
from huggingface_hub import hf_hub_download
voc={v:k for k,v in json.load(open(hf_hub_download(M,'vocab.json'))).items()}
VOW=set('aeiouyɪəɐɨʊɛɔæɑʉøœɵ')
RUV='аеёиоуыэюя'
def load(w):
    y,sr=sf.read(w)
    if y.ndim>1:y=y.mean(1)
    if sr!=16000:y=torchaudio.functional.resample(torch.tensor(y,dtype=torch.float32),sr,16000).numpy()
    return y
def phones(y):
    x=fe(y,sampling_rate=16000,return_tensors='pt').input_values
    with torch.no_grad(): lg=pm(x).logits[0]
    ids=lg.argmax(-1).numpy(); r=len(y)/16000/len(ids)
    out=[];prev=-1
    for i,t in enumerate(ids):
        if t!=prev and t!=0: out.append([voc[int(t)],i*r,(i+1)*r])
        elif t==prev and t!=0: out[-1][2]=(i+1)*r
        prev=t
    return out
def plain(s): return unicodedata.normalize('NFC',s.replace('\u0301',''))
def words_times(wav,text):
    al=align(wav,text); ws=[];cur=[]
    for ch,s,e in al:
        if ch==' ':
            if cur: ws.append(cur);cur=[]
        else: cur.append((ch,s,e))
    if cur: ws.append(cur)
    return [(''.join(c for c,_,_ in w),w[0][1],w[-1][2]) for w in ws]
def analyse(wav,text,targets):
    """targets: list of (word_lower, expected_vowel_index). Returns rows."""
    y=load(wav); ph=phones(y)
    t=re.sub(r'[^\w\s\-]',' ',plain(text).lower()).replace('-',' ')
    wt=words_times(wav,t)
    snd=parselmouth.Sound(y,16000); I=snd.to_intensity(); P=snd.to_pitch()
    rows=[];used=set()
    for tw,exp in targets:
        idx=[i for i,(w,_,_) in enumerate(wt) if w==tw and i not in used]
        if not idx: rows.append((tw,exp,None,'',None));continue
        i=idx[0];used.add(i);_,s,e=wt[i]
        e=wt[i+1][1] if i+1<len(wt) else e
        s=max(0,s-0.03)
        seg=[p for p in ph if p[1]>=s-0.01 and p[1]<e]
        nuc=[];
        for j,p in enumerate(seg):
            if any(c in VOW for c in p[0]):
                end=seg[j+1][1] if j+1<len(seg) else min(e,p[2]+0.08)
                st=p[1];d=max(0.02,end-st)
                ts=np.linspace(st,st+d,8)
                inten=np.nanmean([I.get_value(x) or np.nan for x in ts])
                f0=[P.get_value_at_time(x) for x in ts]; f0=np.nanmax(f0) if not np.all(np.isnan(f0)) else np.nan
                nuc.append(dict(v=p[0],d=d,i=inten,f=f0))
        nv=sum(c in RUV for c in tw)
        if len(nuc)>=2:
            D=np.array([n['d'] for n in nuc]);In=np.array([n['i'] for n in nuc]);F=np.array([n['f'] for n in nuc])
            F=np.where(np.isnan(F),np.nanmin(F) if not np.all(np.isnan(F)) else 100,F)
            z=lambda a:(a-a.mean())/(a.std()+1e-9)
            sc=z(D)+z(In)+0.7*z(np.log(F))
            got=int(np.argmax(sc))
        else: got=0 if nuc else None
        rows.append((tw,exp,got,' '.join(p[0] for p in seg),len(nuc)==nv))
    return rows
