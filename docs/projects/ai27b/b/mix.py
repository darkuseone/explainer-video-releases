import sys,json; sys.path.insert(0,'/home/user/explainer-video-releases/docs/scripts')
from ai27mix import mix
R='/home/user/explainer-video-releases/audio/'; S=R+'sfx/'; E=S+'earshot/onc10v2/'
TL=json.load(open('timeline.json')); WD=TL['words']; PH=TL['phrases']
def wt(w,k=0):
    n=0
    for x in WD:
        if x[2].lower().strip('.,!?…—:«»').startswith(w.lower()):
            if n==k: return x[0]
            n+=1
    raise KeyError(w)
cues=[(0,S+'impact/hook_hit.wav',0.55),(0,E+'whoosh-short_1.wav',0.45),(wt('концовки'),S+'ui/tick2.wav',0.4),(wt('один'),S+'impact/stamp1.wav',0.55),
 (PH[1][0]-0.1,S+'whoosh/whoosh_cinematic.wav',0.4),(wt('умнее'),S+'ui/ui_glitch_04.ogg',0.3),(wt('выясняется'),E+'whoosh-short_2.wav',0.35),(wt('скрывает'),S+'impact/stamp_0.mp3',0.5),
 (PH[2][0]-0.1,S+'whoosh/whoosh_soft.wav',0.35),(wt('голосует'),S+'nuk10/count_tick.wav',0.4),(wt('6'),S+'bolt9/bass_hit_sub.wav',0.6),
 (PH[3][0]-0.1,S+'impact/twist_hit.wav',0.45),(wt('новый'),E+'whoosh-short_3.wav',0.35),(wt('400'),S+'bolt9/bass_hit_sub.wav',0.6),
 (PH[4][0]-0.1,S+'whoosh/whoosh_sharp.wav',0.35),(wt('особые'),S+'ui/picker_tick_1.wav',0.4),(wt('миллион'),S+'nuk10/count_roll.wav',0.45),
 (PH[5][0]-0.15,S+'riser/riser_tension.wav',0.3),(wt('мешают'),S+'nuk10/winter_drone.wav',0.35),(wt('финал'),S+'impact/hit_thud.wav',0.45),
 (PH[6][0]-0.1,S+'warm/reveal_slide_thud_1.wav',0.5),(wt('старый'),S+'impact/stamp1.wav',0.5),(wt('новые'),S+'ui/pro_typing_key_soft.wav',0.3),
 (PH[7][0]-0.1,S+'whoosh/whoosh_soft.wav',0.35),(wt('полмиллиона'),S+'bolt9/bass_hit_sub.wav',0.55),(wt('роботы'),E+'whoosh-short_1.wav',0.3),(wt('базовый'),S+'impact/stamp_0.mp3',0.5),
 (PH[8][0]-0.1,S+'warm/reveal_slide_thud_2.wav',0.45),(wt('власть'),S+'impact/hit_thud.wav',0.45),(wt('одобряют'),S+'ui/tick3.wav',0.4),
 (PH[9][0]-0.1,S+'impact/stamp_0.mp3',0.45),(wt('сдвинули'),S+'warm/reveal_slide_thud_3.wav',0.45),(PH[10][0]-0.1,S+'impact/hook_hit.wav',0.4),(wt('подпишись'),S+'ui/sub_click.wav',0.6)]
mix(cues,R+'beds/bed_nuk10.flac',m_start=0.0,m_loop=(20.0,50.0),m_gain=0.32)
