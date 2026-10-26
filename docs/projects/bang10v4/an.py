import numpy as np,soundfile as sf,sys
def an(p):
    y,sr=sf.read(p); y=y.mean(1) if y.ndim>1 else y
    S=np.abs(np.fft.rfft(y*np.hanning(len(y))))**2; f=np.fft.rfftfreq(len(y),1/sr)
    tot=S[f>40].sum(); h=S[(f>2000)&(f<6000)].sum()/tot; hi=S[f>6000].sum()/tot; lo=S[(f>40)&(f<500)].sum()/tot
    c=(f*S).sum()/S.sum(); m=S[(f>60)&(f<12000)]; fl=np.exp(np.mean(np.log(m+1e-20)))/m.mean()
    pk=m.max()/m.mean()
    return f'{p:40s} lo<500 {lo:.2f}  2-6k {h:.2f}  >6k {hi:.2f}  centroid {c:6.0f}  flat {fl:.3f}  peak/mean {pk:7.0f}'
for p in sys.argv[1:]: print(an(p))
