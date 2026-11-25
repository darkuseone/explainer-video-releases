# shared mixer: voice + music (looped with crossfade, sidechain duck) + SFX cues -> mix.wav (-14 LUFS, TP -1.5)
import json,subprocess
def mix(cues,music,m_start=0.0,m_loop=(10.0,40.0),m_gain=0.2,vo='../v/vo.wav',tl='timeline.json',out='mix.wav',off=3/25):
    TOT=json.load(open(tl))['tot']; D=TOT+off+0.25
    inp=['-i',vo,'-i',music]; fl=[]; lab=[]
    for i,(tt,f,v) in enumerate(cues):
        inp+=['-i',f]; d=max(0,int((tt+off)*1000))
        fl.append(f'[{i+2}:a]aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={d}|{d}[s{i}]'); lab.append(f'[s{i}]')
    fl.append(f'[0:a]aresample=48000,aformat=channel_layouts=stereo,adelay={int(off*1000)}|{int(off*1000)},apad=whole_dur={D},asplit[v][vk]')
    fl.append('[1:a]aresample=48000,aformat=channel_layouts=stereo,asplit[ma][mb]')
    fl.append(f'[ma]atrim={m_start},asetpts=PTS-STARTPTS[m1]'); fl.append(f'[mb]atrim={m_loop[0]}:{m_loop[1]},asetpts=PTS-STARTPTS[m2]')
    fl.append(f'[m1][m2]acrossfade=d=3,volume={m_gain},afade=t=in:d=0.2,apad=whole_dur={D},atrim=0:{D}[m0]')
    fl.append('[m0][vk]sidechaincompress=threshold=0.04:ratio=4:attack=30:release=320[m]')
    fl.append(f'[v][m]{"".join(lab)}amix=inputs={2+len(lab)}:normalize=0:duration=first,atrim=0:{D}[o]')
    subprocess.run(['ffmpeg','-v','error','-y']+inp+['-filter_complex',';'.join(fl),'-map','[o]','-ar','48000','-c:a','pcm_s16le','mix_pre.wav'],check=True)
    o=subprocess.run(['ffmpeg','-i','mix_pre.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
    j=json.loads(o[o.rindex('{'):o.rindex('}')+1])
    subprocess.run(['ffmpeg','-v','error','-y','-i','mix_pre.wav','-af',f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true",'-ar','48000',out],check=True)
    print('ok',round(D,2),len(cues))
