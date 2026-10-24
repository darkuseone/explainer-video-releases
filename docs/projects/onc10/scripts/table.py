import json,re
R=json.load(open('vo_res.json'))
txt=open('../voice.txt').read()
norm={}
for w in re.findall(r"[\w\u0301]+",txt.replace('-',' ')):
    p=w.lower().replace('\u0301','')
    norm.setdefault(p,[]).append(w.lower())
RUV='аеёиоуыэюя'
cnt={};rows=[];bad=[];unk=[]
for tw,exp,got,ph,ok in R:
    i=cnt.get(tw,0);cnt[tw]=i+1
    nm=norm[tw][min(i,len(norm[tw])-1)]
    vow=[c for c in tw if c in RUV]; sv=vow[exp]
    P=ph.split(); no=sum(1 for x in P if x.startswith('o')); ne=sum(1 for x in P if x.startswith('e') or x=='ɛ')
    uo=sum(1 for j,c in enumerate(vow) if c=='о' and j!=exp)
    if not ph: v='не выровнено';
    elif sv in 'оё' and no==0: v='ПРОВЕРИТЬ (ударной о не видно)'
    elif sv not in 'оё' and uo and no>0: v='ПРОВЕРИТЬ (безударная о не редуцирована)'
    elif sv in 'оё' and uo and no>1: v='OK (вероятн. артефакт: лишняя о)'
    elif sv=='е' and ne==0: v='ПРОВЕРИТЬ (ударной е не видно)'
    elif sv in 'оёе' or uo: v='OK'
    else: v='по качеству гласных не проверяемо'
    rows.append((nm,ph,v))
    if v.startswith('ПРОВ'): bad.append(nm)
    if v.startswith('по кач'): unk.append(nm)
with open('../stress_table.md','w') as f:
    f.write('# onc10: ударения по словам (финальная дорожка vo.wav)\n\nМетод: forced alignment jonatasgrosman/wav2vec2-large-xlsr-53-russian (окна слов) + фонемный CTC facebook/wav2vec2-xlsr-53-espeak-cv-ft (редукция гласных). Разметка ruaccent + ручная правка, U+0301, ё везде.\n\n| # | Норма | Фонемы | Вердикт |\n|---|---|---|---|\n')
    for k,(a,b,c) in enumerate(rows,1): f.write(f'| {k} | {a} | {b} | {c} |\n')
    f.write(f'\nИтого слов: {len(rows)}; OK: {sum(r[2].startswith("OK") for r in rows)}; на слух: {len(bad)}; не проверяемо по гласным: {len(unk)}\n')
print(len(rows),'check:',bad); print('unk',unk)
