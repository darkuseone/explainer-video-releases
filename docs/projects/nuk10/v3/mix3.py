import json,subprocess,os
S1='/workspace/halluc/sfx/'; S2='/workspace/halluc/v2/sfx2/'
import numpy as _np
_TM=json.load(open('/workspace/nuk10/v3/tmap.json'))['anc']; _O=_np.array([x[0] for x in _TM]); _N=_np.array([x[1] for x in _TM])
TOT=57.72; END=57.72; O='/workspace/nuk10/out/'; N='/workspace/nuk10/sfx/'
BED=float(os.environ.get('BED','-12'))
E=[]
def e(f,t,g=-16,md=0.6,fo=0.1,off=0.0): E.append((f,float(_np.interp(t,_O,_N)) if t>0 else t,off,g,md,fo))
WC=S2+'whoosh_fast_crisp.wav'; WH=S2+'whoosh_fast_heavy.wav'; SF=S2+'swipe_flick.wav'
SUB=S2+'pro_sub_drop_low.wav'; BH='/workspace/uran9/sfx/bass_hit_sub.wav'
POP1=S1+'pop1.wav'; POP2=S1+'pop2.wav'; ST1=S1+'stamp1.wav'; ST2=S1+'stamp2.wav'; GH=S2+'glitch_hit.wav'
def bh(t,g=-10): e(BH,t-0.02,g,1.0,0.4)
# transitions
TR={2.46:'punch',4.58:'glitch',6.86:'flash',8.58:'slice',9.98:'punch',11.42:'flash',12.9:'rgb',16.6:'whip',19.1:'dip',21.98:'punch',23.88:'whip',24.918:'rgb',27.08:'flash',29.98:'slice',33.08:'flash',35.8:'rgb',39.66:'dip',41.013:'glitch',44.04:'slice',47.5:'whip',50.758:'punch'}
for t,ty in TR.items():
    if ty in('glitch','rgb'): e(GH,t-0.02,-18,0.3,0.1)
    if ty in('whip','slice','dip'): e(WH,t-0.1,-19,0.5,0.2)
    else: e(WC,t-0.1,-19,0.45,0.2)
# hook
e(S1+'hook_hit.wav',0.0,-14,0.6,0.15); e(SUB,0.0,-12,1.0,0.4)
bh(2.46,-9); e(POP1,2.46,-16,0.3)
bh(3.36,-10); e(ST1,3.36,-15,0.5,0.2); bh(4.04,-8); e(S1+'ding1.wav',4.04,-17,0.36,0.1)
# 135 000
e(N+'count_roll.wav',5.0,-15,1.2,0.2); bh(5.66,-8); e(ST2,6.3,-15,0.5,0.2)
# hiroshima 15 kt
e(S1+'thock.wav',6.9,-15,0.4,0.2); e(ST1,7.44,-12,0.5,0.2); bh(7.46,-9)
# 1 hirosima card
e(POP1,8.62,-16,0.3); e(POP2,9.5,-16,0.3)
# gravity
e(N+'gravity_pull.wav',9.98,-14,1.8,0.4); e(POP1,10.3,-16,0.3)
e(N+'crack_split.wav',11.42,-9,1.8,0.4); bh(11.42,-8); e(ST1,11.9,-12,0.5,0.2)
# tsar
e(N+'nuke_boom.wav',12.9,-11,2.6,0.5); bh(13.02,-9); e(ST2,13.7,-15,0.5,0.2)
e(WC,14.1,-19,0.45,0.2); e(WC,15.3,-19,0.45,0.2)
# 2 Gt
e(SUB,16.6,-13,1.0,0.4); e(N+'nuke_boom.wav',17.2,-14,2.6,0.5); bh(17.56,-8); e(ST1,18.2,-13,0.5,0.2)
# sun line
e(N+'count_roll.wav',19.4,-16,1.2,0.2); e(POP1,19.5,-16,0.3)
for i in range(11): e(N+'count_tick.wav',19.4+i*0.18,-18,0.09,0.02)
bh(21.98,-10); e(ST2,22.65,-13,0.5,0.2); bh(22.66,-10)
# rice
e(POP2,23.9,-16,0.3); e(S1+'ding2.wav',23.95,-17,0.27,0.1)
# avatar B
bh(24.96,-9); e(ST1,25.0,-12,0.5,0.2); bh(25.62,-9)
# atmosphere
e(N+'air_peel.wav',27.74,-12,2.0,0.4); bh(28.62,-8); e(POP1,28.62,-16,0.3)
# log bars
e(N+'count_roll.wav',30.0,-17,1.2,0.2)
for t in (30.4,30.9,31.4): e(POP2,t,-16,0.3)
bh(31.58,-8); e(ST2,32.3,-14,0.5,0.2)
# sun
e(N+'sun_flare.wav',33.08,-11,1.4,0.4); e(N+'count_roll.wav',33.3,-16,1.2,0.2); bh(35.2,-10); e(S1+'ding1.wav',34.5,-17,0.36,0.1)
# chx
e(N+'nuke_boom.wav',35.82,-10,2.6,0.5); bh(37.22,-8); e(ST1,37.3,-13,0.5,0.2)
# alive
e(ST2,40.34,-11,0.5,0.2); bh(40.36,-10); e(S1+'ding1.wav',40.5,-16,0.36,0.1)
# winter
e(N+'winter_drone.wav',41.0,-14,3.0,0.5); e(POP1,41.6,-16,0.3); bh(42.34,-9); e(ST1,42.7,-13,0.5,0.2)
for i in range(30): e(N+'dot_pop.wav',44.1+i*0.07,-20,0.07,0.02)
e(SUB,44.78,-13,1.0,0.4); bh(46.1,-8); e(ST2,46.8,-14,0.5,0.2)
# bait
e(POP1,47.55,-15,0.3)
for i in range(18): e(N+'count_tick.wav',48.52+i*0.1,-19,0.09,0.02)
# end
bh(51.82,-9); e(ST2,51.84,-12,0.5,0.2); e(POP1,51.84,-14,0.3)
cmd=['ffmpeg','-v','error','-y','-i','/workspace/nuk10/v/vo.wav','-i',N+'bed_nuk10.wav']
for x in E: cmd+=['-i',x[0]]
fc=["[0:a]aresample=48000,aformat=channel_layouts=mono,apad=whole_dur=%.2f[vo]"%TOT]
fc.append(f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={BED}dB,atrim=0:{TOT:.2f}[m]")
labs=['[vo]','[m]']
for i,(f,t,off,g,md,fo) in enumerate(E):
    n=i+2; st=max(0,t-off)
    fc.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=mono,atrim=0:{md},afade=t=out:st={max(0,md-fo):.2f}:d={fo:.2f},volume={g}dB,adelay={int(round(st*1000))}:all=1,apad=whole_dur={TOT:.2f}[s{i}]")
    labs.append(f'[s{i}]')
fc.append(''.join(labs)+f"amix=inputs={len(labs)}:normalize=0:duration=longest,atrim=0:{TOT:.2f},alimiter=limit=0.95[mix]")
open(O+'fc.txt','w').write(';'.join(fc))
subprocess.run(cmd+['-filter_complex_script',O+'fc.txt','-map','[mix]','-ar','48000','-ac','2',O+'mix_pre.wav'],check=True)
r=subprocess.run(['ffmpeg','-i',O+'mix_pre.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(r[r.rindex('{'):r.rindex('}')+1])
af=f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-v','error','-y','-i',O+'mix_pre.wav','-af',af,'-ar','48000',O+'mix.wav'],check=True)
print('mix ok',len(E),j['input_i'])
