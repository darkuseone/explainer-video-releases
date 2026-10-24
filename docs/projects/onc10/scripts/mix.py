import json,subprocess
A='/workspace/onc10/audio/'; O='/workspace/onc10/out/'; TOT=59.67
def lufs(f):
    r=subprocess.run(['ffmpeg','-i',f,'-af','loudnorm=print_format=json','-f','null','-'],capture_output=True,text=True).stderr
    return float(json.loads(r[r.rindex('{'):r.rindex('}')+1])['input_i'])
vo=lufs('/workspace/onc10/v/vo.wav'); bd=lufs(A+'bed_onc10.wav'); BED=(vo-19)-bd
TR={2.40:'punch',4.80:'whip',7.36:'flash',9.40:'glitch',11.15:'punch',12.70:'whip',15.06:'flash',17.40:'dip',19.10:'whip',20.85:'glitch',24.34:'punch',26.50:'flash',28.20:'dip',30.10:'punch',32.35:'dip',34.65:'glitch',36.35:'flash',37.65:'punch',39.60:'whip',43.20:'glitch',45.15:'dip',47.80:'whip',49.40:'flash',51.35:'punch',52.60:'whip',54.75:'glitch',57.45:'flash'}
E=[]
def e(f,t,g): E.append((A+f,t,g))
for t,ty in TR.items():
    if ty=='glitch': e('sfx_glitch.wav',t,-20)
    elif ty in('whip','flash'): e('sfx_whoosh.wav',t-0.25,-22)
    elif ty=='punch': e('sfx_hit.wav',t,-20)
    else: e('sfx_hit.wav',t,-23)
e('sfx_hit.wav',0.0,-16)
for t0 in (17.40,45.15):
    for i in range(14): e('sfx_tick.wav',t0+i*0.05,-24)
    e('sfx_ding.wav',t0+0.7,-21)
e('sfx_ding.wav',32.35,-21)
for i in range(16): e('sfx_pop.wav',28.2+i*0.0375,-26)
e('sfx_ding.wav',29.0,-21)
for t in (21.43,24.34,37.68): e('sfx_stamp.wav',t,-18)
e('sfx_pop.wav',51.39,-20); e('sfx_pop.wav',54.82,-20)
cmd=['ffmpeg','-v','error','-y','-i','/workspace/onc10/v/vo.wav','-i',A+'bed_onc10.wav']
for x in E: cmd+=['-i',x[0]]
fc=[f"[0:a]aresample=48000,aformat=channel_layouts=mono,apad=whole_dur={TOT}[vo]",f"[1:a]aresample=48000,aformat=channel_layouts=mono,volume={BED:.2f}dB,atrim=0:{TOT}[m]"]
labs=['[vo]','[m]']
for i,(f,t,g) in enumerate(E):
    fc.append(f"[{i+2}:a]aresample=48000,aformat=channel_layouts=mono,volume={g}dB,adelay={int(max(0,t)*1000)}:all=1,apad=whole_dur={TOT}[s{i}]"); labs.append(f'[s{i}]')
fc.append(''.join(labs)+f"amix=inputs={len(labs)}:normalize=0:duration=longest,atrim=0:{TOT},alimiter=limit=0.95[mix]")
open(O+'fc.txt','w').write(';'.join(fc))
subprocess.run(cmd+['-filter_complex_script',O+'fc.txt','-map','[mix]','-ar','48000','-ac','2',O+'mix_pre.wav'],check=True)
r=subprocess.run(['ffmpeg','-i',O+'mix_pre.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(r[r.rindex('{'):r.rindex('}')+1])
af=f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-v','error','-y','-i',O+'mix_pre.wav','-af',af,'-ar','48000',O+'mix.wav'],check=True)
print('vo',vo,'bed',bd,'BEDgain',BED,'events',len(E),'final',lufs(O+'mix.wav'))
