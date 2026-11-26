# cd10 mix: voice + music bed (library) + SFX from audio/sfx, all shifted by cover offset
import json,subprocess,sys
R='/home/user/explainer-video-releases/audio/'
TL=json.load(open('timeline.json')); WD=TL['words']; TOT=TL['tot']; OFF=3/25
def wt(word,ph,k=0,end=False):
    n=0
    for w in WD:
        if w[3]==ph and w[2].lower().strip('.,!?…—:«»').startswith(word.lower()):
            if n==k: return w[1] if end else w[0]
            n+=1
    raise KeyError(word)
S=R+'sfx/'
cues=[(0.0,S+'earshot/onc10v2/whoosh-short_1.wav',0.55),(0.05,S+'ui/pro_glitch_standard.wav',0.35),
 (wt('зуме',0),S+'eif10/arrow_swish.wav',0.45),(wt('каша',1),S+'impact/thock.wav',0.5),
 (TL['phrases'][2][0],S+'riser/swell_0.mp3',0.25),(wt('картинка',2),S+'ui/pop1.wav',0.4),
 (wt('билборд',3),S+'impact/drop1.wav',0.4),(wt('голубую',4),S+'ui/ui_glitch_04.ogg',0.3),
 (wt('одну',4),S+'ui/click1.wav',0.5),(wt('ожила',5),S+'earshot/onc10v2/whoosh-short_1.wav',0.4),
 (wt('фотограф',6),S+'ui/tick2.wav',0.45),(wt('чертёжник',6),S+'ui/tick3.wav',0.45),
 (wt('наверн',7),S+'ui/glitch_0.mp3',0.35),(wt('подпиш',8),S+'ui/pop2.wav',0.45)]
# typing during the code scene
t=TL['phrases'][3][0]+0.1; te=wt('жёлтый',3,end=True)
while t<te: cues.append((t,S+'ui/pro_typing_key_soft.wav',0.18)); t+=0.16
inp=['-i','../v/vo.wav','-i',R+'music/UwUT4EHqjTdgbYIRgFA8.mp3']
fl=[]; lab=[]
for i,(tt,f,v) in enumerate(cues):
    inp+=['-i',f]; d=int((tt+OFF)*1000)
    fl.append(f'[{i+2}:a]aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={d}|{d}[s{i}]'); lab.append(f'[s{i}]')
D=TOT+OFF+0.3
fl.append(f'[0:a]aresample=48000,aformat=channel_layouts=stereo,adelay={int(OFF*1000)}|{int(OFF*1000)},apad=whole_dur={D},asplit[v][vk]')
fl.append(f'[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.2,afade=t=in:d=0.3,apad=whole_dur={D},afade=t=out:st={D-1.2}:d=1.2[m0]')
fl.append('[m0][vk]sidechaincompress=threshold=0.05:ratio=3:attack=40:release=350[m]')
fl.append(f'[v][m]{"".join(lab)}amix=inputs={2+len(lab)}:normalize=0:duration=first,alimiter=limit=0.95,atrim=0:{D}[o]')
cmd=['ffmpeg','-v','error','-y']+inp+['-filter_complex',';'.join(fl),'-map','[o]','-ar','48000','-c:a','pcm_s16le','mix.wav']
subprocess.run(cmd,check=True); print('ok',D,len(cues))
