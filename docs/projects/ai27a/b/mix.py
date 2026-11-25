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
cues=[(0,S+'impact/hook_hit.wav',0.55),(0,E+'whoosh-short_1.wav',0.45),(wt('21-м'),S+'ui/tick2.wav',0.4),(wt('26-й'),S+'warm/counter_land_latch.wav',0.5),
 (wt('угадал'),S+'impact/stamp1.wav',0.55),(PH[1][0]-0.1,S+'whoosh/whoosh_soft.wav',0.4),(wt('позже'),S+'ui/picker_tick_1.wav',0.4),(wt('писал'),E+'whoosh-short_2.wav',0.35),
 (wt('миллиарды'),S+'impact/stamp_0.mp3',0.5),(PH[2][0]-0.1,S+'whoosh/whoosh_sharp.wav',0.35),(wt('19'),S+'nuk10/count_roll.wav',0.45),(wt('полностью'),S+'bolt9/bass_hit_sub.wav',0.55),
 (PH[3][0]-0.1,E+'whoosh-short_3.wav',0.35),(wt('ai'),S+'warm/reveal_slide_thud_1.wav',0.5),(wt('месяцам'),S+'riser/swell_0.mp3',0.3),
 (PH[4][0]-0.1,S+'impact/hit_thud.wav',0.5),(wt('программирует'),S+'ui/ui_glitch_04.ogg',0.3),(wt('200'),S+'bolt9/bass_hit_sub.wav',0.6),(wt('50'),S+'ui/tick3.wav',0.4),(wt('30'),S+'bolt9/bass_hit_sub.wav',0.55),
 (PH[5][0]-0.1,S+'whoosh/whoosh_cinematic.wav',0.35),(wt('300'),S+'bolt9/bass_hit_sub.wav',0.55),(wt('неделю'),S+'nuk10/count_tick.wav',0.4),(wt('год'),S+'impact/stamp1.wav',0.5),
 (PH[6][0]-0.2,S+'riser/riser_tension.wav',0.3),(wt('перестаёт'),S+'ui/pro_glitch_standard.wav',0.4),(wt('чисел'),S+'impact/glitch_hit.wav',0.45),(wt('прочитать'),S+'ui/glitch_0.mp3',0.3),
 (PH[7][0]-0.1,S+'impact/stamp_0.mp3',0.45),(wt('ждут'),S+'warm/reveal_slide_thud_2.wav',0.45),(PH[8][0]-0.1,S+'impact/hook_hit.wav',0.4),(wt('подпишись'),S+'ui/sub_click.wav',0.6)]
mix(cues,R+'music/CuIAqvgYvYSIBrRdLAub.mp3',m_start=0.0,m_loop=(12.0,40.0),m_gain=0.2)
