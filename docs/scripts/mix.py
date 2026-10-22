import json,subprocess
S1='/workspace/halluc/sfx/'; S2='/workspace/halluc/v2/sfx2/'; L='/workspace/exoplanet_explainer/sfx_library/'
TOT=50.28; TW=22.3; O='/workspace/nuke/b/'
E=[]
def e(f,t,g=-16,md=0.6,fo=0.1,off=0.0): E.append((f,t,off,g,md,fo))
WC=S2+'whoosh_fast_crisp.wav'; WH=S2+'whoosh_fast_heavy.wav'; SF=S2+'swipe_flick.wav'; SP=S2+'swipe_paper.wav'
e(S1+'hook_hit.wav',0.04,-15,0.6,0.15); e(WH,2.02,-17,0.6,0.2,0.13)
e(S1+'stamp1.wav',3.35,-12,0.6,0.25); e(S2+'pro_hover_tick_ping.wav',4.5,-16,0.3)
e(SF,5.42,-18,0.4); e(S2+'fit_whoosh.short_bamboo_swish.wav',5.6,-16,0.4); e(S2+'pro_impact_deep.wav',6.52,-13,0.6,0.3); e(S2+'glitch_hit.wav',6.53,-18,0.4)
e(WC,9.06,-17,0.6,0.2,0.13); e(S2+'fit_hit_bamboo_tok.wav',9.2,-14,0.3)
e(SP,10.7,-17,0.4); e(S1+'pop1.wav',11.6,-16,0.3)
e(SF,12.84,-18,0.4)
for k,tt in enumerate([13.76,14.02,14.64,15.4,16.0,16.6]): e(S1+'pop%d.wav'%(1+k%2),tt,-15,0.3)
e(S2+'riser_tension.wav',15.3,-19,2.0,0.3); e(S1+'stamp2.wav',17.4,-12,0.6,0.25)
e(SP,18.5,-16,0.5); e(S2+'downlifter_sub_sink.wav',19.2,-18,0.6,0.2)
e(S1+'stamp1.wav',20.8,-13,0.6,0.25)
e(S2+'pro_sub_drop_low.wav',TW,-9,1.2,0.5); e(S1+'twist_hit.wav',TW,-11,0.9,0.5,0.005)
e(S2+'pro_impact_deep.wav',24.4,-12,0.6,0.3)
e(SP,25.36,-18,0.4)
e(S2+'fit_land.light_finger_wood.wav',27.9,-14,0.3)
e(WC,29.2,-18,0.6,0.2,0.13); e(S1+'ding1.wav',30.1,-16,0.4,0.2)
e(SF,31.56,-18,0.4)
for i in range(10): e(S1+'tick%d.wav'%(1+i%4),31.7+i*0.14,-19,0.08,0.03)
e(S1+'ding2.wav',33.1,-16,0.5,0.2)
e(S2+'fit_snap_switch_flip.wav',34.1,-14,0.3)
e(WC,35.7,-18,0.6,0.2,0.13); e(S2+'pro_impact_short.wav',37.1,-14,0.5,0.2)
e(SP,37.7,-16,0.5); e(S2+'riser_tension.wav',38.9,-18,1.7,0.3); e(S2+'pro_impact_deep.wav',40.6,-12,0.6,0.3)
e(S2+'swipe_paper.wav',45.34,-17,0.5)
e(S1+'sub_click.wav',49.7,-10,0.2,0.05,0.03); e(S1+'ding1.wav',49.76,-18,0.36,0.2)
cmd=['ffmpeg','-v','error','-y','-i','/workspace/nuke/v/vo.wav','-ss','2.0','-i',L+'music/cyberpunk_04_144bpm.mp3']
for x in E: cmd+=['-i',x[0]]
fc=["[0:a]aresample=48000,aformat=channel_layouts=mono,apad=whole_dur=%.2f[vo]"%TOT]
fc.append("[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=-19dB,afade=t=in:d=0.3,"
     f"afade=t=out:st={TOT-0.4:.2f}:d=0.4,atrim=0:{TOT:.2f},"
     f"volume='if(lt(t,21.9),1,if(lt(t,{TW:.2f}),0.03,if(lt(t,{TW+0.6:.2f}),1.3,if(lt(t,41.6),1.1,if(lt(t,45.3),0.35,1.0)))))':eval=frame[m]")
labs=['[vo]','[m]']
for i,(f,t,off,g,md,fo) in enumerate(E):
    n=i+2; st=max(0,t-off)
    fc.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=mono,atrim=0:{md},afade=t=out:st={max(0,md-fo):.2f}:d={fo:.2f},volume={g}dB,adelay={int(round(st*1000))}:all=1,apad=whole_dur={TOT:.2f}[s{i}]")
    labs.append(f'[s{i}]')
fc.append(''.join(labs)+f"amix=inputs={len(labs)}:normalize=0:duration=longest,atrim=0:{TOT:.2f},afade=t=out:st={TOT-0.08:.2f}:d=0.08,alimiter=limit=0.95[mix]")
subprocess.run(cmd+['-filter_complex',';'.join(fc),'-map','[mix]','-ar','48000','-ac','2',O+'mix_pre.wav'],check=True)
r=subprocess.run(['ffmpeg','-i',O+'mix_pre.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(r[r.rindex('{'):r.rindex('}')+1])
af=f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-v','error','-y','-i',O+'mix_pre.wav','-af',af,'-ar','48000',O+'mix.wav'],check=True)
print('mix ok',len(E),j['input_i'])
