import json,subprocess,sys,numpy as np,soundfile as sf
sys.path.insert(0,'/home/box/tools/earshot')
from earshot.forge import kit
A='/workspace/onc10/audio/';O='/workspace/onc10v2/';TOT=59.67;SR=48000
def lufs(f):
    r=subprocess.run(['ffmpeg','-i',f,'-af','loudnorm=print_format=json','-f','null','-'],capture_output=True,text=True).stderr
    return float(json.loads(r[r.rindex('{'):r.rindex('}')+1])['input_i'])
def load(f):
    subprocess.run(['ffmpeg','-v','error','-y','-i',f,'-ar','48000','-ac','2','/tmp/_l.wav'],check=True)
    y,_=sf.read('/tmp/_l.wav');return y
N=int(TOT*SR)
vo=load('/workspace/onc10/v/vo.wav')[:N];vo=np.pad(vo,((0,N-len(vo)),(0,0)))
bd=load(A+'bed_onc10.wav')[:N];bd=np.pad(bd,((0,N-len(bd)),(0,0)))
BED=(lufs('/workspace/onc10/v/vo.wav')-19)-lufs(A+'bed_onc10.wav')
bd*=10**(BED/20)
lock=json.load(open(O+'kit/kit.lock.json'));R=lock['roles']
def vlev(t):  # voice loudest 50ms K-weighted around the cue
    b,e=int(max(0,t-0.1)*SR),int((t+0.3)*SR);s=vo[b:e];k=len(s)//2400
    if k<1: return None
    p=kit._kpower(s)[:k*2400].reshape(k,2400).mean(1);return -0.691+10*np.log10(p.max()+1e-24)
cnt={}
EV=[]
def ev(role,t,extra=0,take=None,label=''):
    r=R[role];i=cnt.get(role,0);cnt[role]=i+1
    tk=take or r['takes'][i%len(r['takes'])]
    st=kit.place(tk,r,t);bl=kit.bed_level(bd,max(t,0.06),sr=SR)
    g=kit.gain_db(tk,r,bl)+extra
    v=vlev(t)
    if v is not None and v>-50: g=min(g,v-9-tk['l50_lufs'])   # never closer than 9 dB to the voice
    EV.append(dict(role=role,sound=r['sound'],file=tk['file'],cue=round(t,3),start=st,gain=round(g,2),label=label))
TR={2.40:'punch',4.80:'whip',7.36:'flash',9.40:'glitch',11.15:'punch',12.70:'whip',15.06:'flash',17.40:'dip',19.10:'whip',20.85:'glitch',24.34:'punch',26.50:'flash',28.20:'dip',30.10:'punch',32.35:'dip',34.65:'glitch',36.35:'flash',37.65:'punch',39.60:'whip',43.20:'glitch',45.15:'dip',47.80:'whip',49.40:'flash',51.35:'punch',52.60:'whip',54.75:'glitch',57.45:'flash'}
M={'punch':'hit','whip':'whoosh.short','flash':'snap','glitch':'glitch','dip':'land'}
ev('drop',0.0,label='hook')
for t,ty in TR.items(): ev(M[ty],t,label='cut '+ty)
for t0 in (17.40,45.15):
    for t in kit.space_run([t0+i*0.05 for i in range(10)],R['tick']['min_gap_ms']): ev('tick',t,label='counter')
    ev('bell',t0+0.7,take=R['bell']['takes'][4],label='number lands')
ev('bell',32.35,take=R['bell']['takes'][2],label='3 years')
for t in kit.space_run([28.2+i*0.0375 for i in range(8)],R['pop']['min_gap_ms']): ev('pop',t,label='8 of 16 dots')
ev('click.confirm',29.0+0.0,label='8/16 done')
for t in (21.43,24.34,37.68): ev('tock',t,label='stamp')
ev('pop',51.39,label='CTA');ev('pop',54.82,label='CTA')
ev('riser',57.45,label='loop end')
ev('whoosh.short',6.20,label='cut (critique fix)')
ev('tock',47.96,label='cut (critique fix)')
for t in (18.10,29.0,45.85): ev('drop',t,extra=-3,label='sub under number reveal')
sfx=np.zeros((N,2));PAN=[-0.35,0.3,-0.2,0.4,0.15,-0.4];PANU=[]
for e in EV:
    y,_=sf.read(O+'kit/'+e['file']);y=y if y.ndim==2 else np.stack([y,y],1)
    s=int(round(e['start']*SR))
    if s<0: y=y[-s:];s=0
    y=y[:max(0,N-s)]*10**(e['gain']/20);p=PAN[len(PANU)%len(PAN)] if e['role'] not in('drop','hit','land') else 0;PANU.append(p);e['pan']=p;y=y*np.array([np.sqrt(0.5*(1-p)),np.sqrt(0.5*(1+p))])*np.sqrt(2);sfx[s:s+len(y)]+=y
sf.write(O+'sfx_stem.wav',sfx,SR,subtype='PCM_24')
mix=vo+bd+sfx;sf.write(O+'mix_pre.wav',mix,SR,subtype='FLOAT')
r=subprocess.run(['ffmpeg','-i',O+'mix_pre.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(r[r.rindex('{'):r.rindex('}')+1])
af=f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-v','error','-y','-i',O+'mix_pre.wav','-af',af,'-ar','48000','-c:a','pcm_s24le',O+'mix.wav'],check=True)
json.dump(EV,open(O+'cues.json','w'),indent=1)
print(len(EV),'events final',lufs(O+'mix.wav'))
