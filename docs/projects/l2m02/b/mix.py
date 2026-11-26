# l2m02 mix: voice + library music (space_cinematic_electronica_120bpm, sidechain duck) + SFX at scene events; shifted by cover 0.12 s
import json,subprocess
R='/home/user/explainer-video-releases/audio/'; S=R+'sfx/'
TL=json.load(open('timeline.json')); WD=TL['words']; PH=TL['phrases']; TOT=TL['tot']; OFF=3/25
def wt(word,k=0):
    n=0
    for w in WD:
        if w[2].lower().strip('.,!?…—:«»').startswith(word.lower()):
            if n==k: return w[0]
            n+=1
    raise KeyError(word)
E='earshot/onc10v2/'
cues=[(0.0,S+'impact/hook_hit.wav',0.55),(0.0,S+E+'whoosh-short_1.wav',0.5),(wt('айфоне'),S+'impact/stamp1.wav',0.55),(wt('двухтысячных'),S+'ui/tick2.wav',0.4),
 (PH[1][0]-0.1,S+'whoosh/whoosh_cinematic.wav',0.4),(wt('утра'),S+'ui/picker_tick_1.wav',0.4),(wt('осады'),S+E+'hit_1.wav',0.45),(wt('сотни'),S+'ui/tick3.wav',0.35),
 (wt('рейды'),S+'impact/boom.wav',0.35),(PH[2][0]-0.1,S+E+'whoosh-short_2.wav',0.45),(PH[2][0]+0.05,S+'warm/reveal_slide_thud_1.wav',0.45),(PH[2][0]+0.5,S+'warm/reveal_slide_thud_2.wav',0.45),
 (wt('другие'),S+'impact/stamp_0.mp3',0.55),(PH[3][0]-0.1,S+'whoosh/whoosh_sharp.wav',0.4),(wt('гиран'),S+E+'snap_1.wav',0.4),(wt('скиллы'),S+E+'snap_2.wav',0.35),
 (wt('интерфейс'),S+E+'whoosh-short_3.wav',0.35),(wt('только'),S+'ui/fit_land.light_finger_phone.wav',0.6),(wt('пальцы'),S+'ui/fit_land.light_finger_phone.wav',0.6),
 (PH[4][0]-0.1,S+'whoosh/whoosh_soft.wav',0.4),(wt('телефона'),S+'riser/swell_0.mp3',0.3),(wt('мир'),S+'impact/stamp1.wav',0.5),(wt('компьютеров')-0.5,S+E+'whoosh-short_1.wav',0.35),
 (PH[5][0]-0.1,S+'whoosh/whoosh_double.wav',0.35),(wt('63'),S+'bolt9/bass_hit_sub.wav',0.7),(wt('хватит'),S+'warm/counter_land_latch.wav',0.5),
 (wt('айфона'),S+'bolt9/bass_hit_sub.wav',0.6),(PH[6][0]-0.1,S+'impact/hook_hit.wav',0.4),(wt('подпишись'),S+'ui/sub_click.wav',0.6)]
D=TOT+OFF+0.25
inp=['-i','../v/vo.wav','-i',R+'music/space_cinematic_electronica_120bpm.mp3']
fl=[];lab=[]
for i,(tt,f,v) in enumerate(cues):
    inp+=['-i',f]; d=int((tt+OFF)*1000)
    fl.append(f'[{i+2}:a]aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={d}|{d}[s{i}]'); lab.append(f'[s{i}]')
fl.append(f'[0:a]aresample=48000,aformat=channel_layouts=stereo,adelay={int(OFF*1000)}|{int(OFF*1000)},apad=whole_dur={D},asplit[v][vk]')
# music: start at 3.0 s of the track (drop lands ~4.8 s); second copy from 20 s crossfaded to cover the tail
fl.append('[1:a]aresample=48000,aformat=channel_layouts=stereo,asplit[ma][mb]')
fl.append('[ma]atrim=3.0:56.0,asetpts=PTS-STARTPTS[m1]'); fl.append('[mb]atrim=20.0:40.0,asetpts=PTS-STARTPTS[m2]')
fl.append(f'[m1][m2]acrossfade=d=3,volume=0.22,afade=t=in:d=0.2,apad=whole_dur={D},atrim=0:{D}[m0]')
fl.append('[m0][vk]sidechaincompress=threshold=0.04:ratio=4:attack=30:release=320[m]')
fl.append(f'[v][m]{"".join(lab)}amix=inputs={2+len(lab)}:normalize=0:duration=first,atrim=0:{D}[o]')
subprocess.run(['ffmpeg','-v','error','-y']+inp+['-filter_complex',';'.join(fl),'-map','[o]','-ar','48000','-c:a','pcm_s16le','mix_pre.wav'],check=True)
# two-pass loudnorm to -14 LUFS, TP -1.5
o=subprocess.run(['ffmpeg','-i','mix_pre.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(o[o.rindex('{'):o.rindex('}')+1])
subprocess.run(['ffmpeg','-v','error','-y','-i','mix_pre.wav','-af',f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true",'-ar','48000','mix.wav'],check=True)
print('ok',round(D,2),len(cues))
