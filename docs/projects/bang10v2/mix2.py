import numpy as np,soundfile as sf,math
SR=48000; TOT=59.0; out=np.zeros(int(TOT*SR)); K='kit/'
def ld(n):
    y,sr=sf.read(K+n); y=y.mean(1) if y.ndim>1 else y; assert sr==SR; return y
def put(n,t,db):
    y=ld(n)*10**(db/20); i=int(t*SR); j=min(len(out),i+len(y)); out[i:j]+=y[:j-i]
TR=[2.30,12.64,20.66,25.49,34.93,42.47,48.52,56.12]  # rewind-tape transitions
for k,t in enumerate(TR): put('whoosh-short_%d.wav'%(k%3+1),t-0.05,-20); put('glitch_%d.wav'%(k%2+1),t,-28)
for t in (4.86,6.42,14.70,23.11,30.37,33.13,37.89,39.25,46.01,47.17,51.33,54.11): put('whoosh-short_%d.wav'%(int(t)%3+1),t-0.04,-26)
put('riser_1.wav',6.6,-22); put('drop_1.wav',8.62,-12); put('hit_1.wav',8.64,-15); put('swell_1.wav',52.4,-22)
put('hit_2.wav',13.08,-17)                       # stamp
# single counter 0 -> 13,8 over 0.95 s: picker-wheel ticks only (no tock)
a=10.40; d=0.95; last=-1; lt=-1; n=0
for f in np.arange(a,a+d+0.01,0.004):
    p=min(1,(f-a)/d); p=3*p*p-2*p**3; v=int(13.8*p*10)
    if v!=last and f-lt>=0.06: put('tick_%d.wav'%(n%3+1),f,-15); lt=f; n+=1
    last=v
put('bell_E6.wav',a+d,-17)
for t in (0.88,20.90,23.11,25.49,28.01,33.13,34.93,36.69,42.47,44.01,48.61,56.69): put('pop_%d.wav'%(1+int(t)%4),t,-21)
for t in (44.79,45.45,46.21,46.57): put('land-light_%d.wav'%(1+int(t*10)%3),t,-22)  # bounce/breath
put('bell_C6.wav',31.89,-22)
sf.write('audio/sfx2.wav',out,SR); print(n,'ticks')
