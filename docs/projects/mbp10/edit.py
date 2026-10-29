import numpy as np,soundfile as sf,subprocess,re
y,sr=sf.read('audio/vo_raw.wav')
cuts=[(16.80,19.40),(32.10,34.70),(48.55,53.90),(59.55,61.80)]
def xf(parts,n=int(0.01*48000)):
    out=parts[0]
    for p in parts[1:]:
        r=np.linspace(1,0,n); out=np.concatenate([out[:-n],out[-n:]*r+p[:n]*(1-r),p[n:]])
    return out
keep=[];a=0
for c0,c1 in cuts: keep.append(y[int(a*sr):int(c0*sr)]); a=c1
keep.append(y[int(a*sr):]); z=xf(keep); sf.write('/tmp/z.wav',z,sr)
o=subprocess.run(['ffmpeg','-i','/tmp/z.wav','-af','silencedetect=n=-40dB:d=0.3','-f','null','-'],capture_output=True,text=True).stderr
S=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',o)]; E=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',o)]
parts=[];a=0
for s,e in zip(S,E):
    if e-s>0.32: m=(s+e)/2; parts.append(z[int(a*sr):int((s+0.16)*sr)]); a=e-0.12
parts.append(z[int(a*sr):]); z=xf(parts)
# trim lead/tail
nz=np.where(np.abs(z)>10**(-45/20))[0]; z=z[max(0,nz[0]-int(0.04*sr)):nz[-1]+int(0.35*sr)]
sf.write('audio/vo_edit.wav',z,sr); print(len(z)/sr)
