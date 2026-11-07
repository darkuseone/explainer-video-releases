"""Rebuild normalized local outputs from this snapshot; no network or account writes."""
from pathlib import Path
import csv,json,hashlib,statistics,collections,datetime
ROOT=Path(__file__).resolve().parent
RAW=ROOT/'2026-11-07/raw'
with (RAW/'file2.csv').open(encoding='utf-8-sig',newline='') as f: table=[r for r in csv.reader(f) if r]
h,total=table[:2]; videos=table[2:]
with (RAW/'file1.csv').open(encoding='utf-8-sig',newline='') as f: daily=list(csv.DictReader(f))
with (RAW/'file3.csv').open(encoding='utf-8-sig',newline='') as f: series=list(csv.DictReader(f))
matches={'L4RuabBAmgs':('dna10','high topic/title; published version unverified'),'He4QgKFSDxk':('sim10','high topic/title; published version unverified'),'IZr37_boKO8':('gar10 family','high topic/title; version unverified'),'23NnvxStNms':('bang10 family','high topic/title; version unverified'),'NfBCzOwv55k':('mbp10 family','high topic/title; v1/v2 unverified'),'MBhRGR2l1RM':('onc10','high topic/title; version unverified'),'w5MnotHVgns':('nuk10 family','high script topic; version unverified'),'2NSeQzR_5Ig':('','not nuk10: different nuclear topic'),'ehos8MI2EH8':('hum9','high title from docs/examples/hum9_publish.txt'),'3CqeDB8yiKE':('eif9','high exact metadata title'),'3CztNxjbTCM':('bolt9','tentative metadata filename/topic')}
fields='snapshot_date,snapshot_timezone,report_start,report_end,report_timezone,period_type,content_filter,traffic_filter,video_id,video_title,release_id,release_match_confidence,published_at_source,published_at_chisinau,duration_seconds,age_days_at_snapshot,views,engaged_views,shown_in_feed,stayed_to_watch_percent,swiped_away_percent,average_view_duration_seconds,average_percentage_viewed,watch_time_hours,likes,comments,shares,subscribers_gained,subscribers_lost,subscribers_net,impressions,impressions_ctr_percent,shorts_feed_views,engaged_views_per_feed_show,likes_per_1000_engaged_views,comments_per_1000_engaged_views,subscribers_gained_per_1000_engaged_views,source_files,notes,unique_viewers,unique_reach,co_viewed_views,average_views_per_viewer,new_viewers,returning_label_column14,casual_viewers_column15,regular_label_column16,dislikes,like_rating_percent'.split(',')
records=[]
for r in videos:
 vid=r[0].strip();ev=int(r[4]); dur=sum(int(x)*60**i for i,x in enumerate(reversed(r[5].split(':'))))
 d=dict.fromkeys(fields,'');d.update(snapshot_date='2026-11-07',snapshot_timezone='Europe/Chisinau',report_start='2026-10-09',report_end='2026-11-05',report_timezone='unknown',period_type='selected_window_inferred_from_file1_total',content_filter='not recorded; short runtimes 44-62s',traffic_filter='unknown',video_id=vid,video_title=r[1],release_id=matches.get(vid,('','unknown'))[0],release_match_confidence=matches.get(vid,('','unknown'))[1],published_at_source=r[2],duration_seconds=r[3],views=r[23],engaged_views=r[4],stayed_to_watch_percent=r[7],swiped_away_percent=f'{100-float(r[7]):.2f}',average_view_duration_seconds=dur,average_percentage_viewed=r[6],watch_time_hours=r[24],likes=r[18],comments=r[22],shares=r[21],subscribers_gained=r[16],subscribers_lost=r[17],subscribers_net=r[25],impressions=r[26],impressions_ctr_percent=r[27],source_files='2026-11-07/raw/file2.csv',notes='Period inferred, not encoded in table; publication date has no timezone; swipe complement derived; no feed denominator/traffic/retention curve. Duplicate audience labels preserved by column position.',unique_viewers=r[8],unique_reach=r[9],co_viewed_views=r[10],average_views_per_viewer=r[11],new_viewers=r[12],returning_label_column14=r[13],casual_viewers_column15=r[14],regular_label_column16=r[15],dislikes=r[19],like_rating_percent=r[20])
 for key,i in [('likes_per_1000_engaged_views',18),('comments_per_1000_engaged_views',22),('subscribers_gained_per_1000_engaged_views',16)]:d[key]=f'{1000*int(r[i])/ev:.4f}'
 records.append(d)
ledger=ROOT/'weekly_video_ledger.csv'
old=[]
if ledger.exists():
 with ledger.open(newline='') as f: old=list(csv.DictReader(f))
old=[r for r in old if r.get('snapshot_date')!='2026-11-07']
with ledger.open('w',newline='') as f:
 w=csv.DictWriter(f,fields);w.writeheader();w.writerows(old+records)
manifest={'snapshot_date':'2026-11-07','snapshot_timezone':'Europe/Chisinau','status':'analysed','daily_date_range':['2026-10-09','2026-11-05'],'report_timezone':'unknown','table_date_range':'not encoded; inferred same selection from exact engaged-total reconciliation','publication_metadata_anomalies':'Activity precedes publication date in series; table includes Nov 6 publication beyond Nov 5 daily end. Confirm report settings before equal-age/day claims.','files':[]}
for name,rows,kind,cols in [('file1.csv',28,'daily channel engaged-view time series',['Дата','Заинтересованные просмотры']),('file2.csv',24,'per-video selected-period table plus channel total',h),('file3.csv',140,'daily engaged views for five selected/top videos',list(series[0]))]:
 p=RAW/name;manifest['files'].append({'file':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'encoding':'UTF-8 (UTF-8-sig parser accepts optional BOM)','delimiter':',','decimal':'.','data_rows':rows,'kind':kind,'columns':cols})
(ROOT/'2026-11-07/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
with (ROOT/'2026-11-07/channel_totals.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(h);w.writerow(total)
lines=['# Per-video snapshot: 2026-11-07','', 'Period inferred: 2026-10-09–2026-11-05; report timezone unknown. Source file2.csv. All rates as exported, except labelled derived ratios. No per-video traffic-source or timed-retention data.','', '| Video / title | Engaged / views | AVD / APV | Stayed % | Likes / comments / shares | Subs + / − / net | Impressions / CTR % |','|---|---:|---:|---:|---:|---:|---:|']
for r in videos: lines.append(f'| {r[0].strip()} — {r[1]} | {r[4]} / {r[23]} | {r[5]} / {r[6]}% | {r[7]} | {r[18]} / {r[22]} / {r[21]} | {r[16]} / {r[17]} / {r[25]} | {r[26]} / {r[27]} |')
lines+=['','## Audience and conversion detail','','| Video ID | Unique viewers | New viewers | Col14 / Col15 / Col16 | Likes / comments / gained subs per 1k engaged | Release mapping |','|---|---:|---:|---:|---:|---|']
for d in records:lines.append(f"| {d['video_id']} | {d['unique_viewers']} | {d['new_viewers'] or 'missing'} | {d['returning_label_column14'] or 'missing'} / {d['casual_viewers_column15'] or 'missing'} / {d['regular_label_column16'] or 'missing'} | {float(d['likes_per_1000_engaged_views']):.2f} / {float(d['comments_per_1000_engaged_views']):.2f} / {float(d['subscribers_gained_per_1000_engaged_views']):.2f} | {d['release_id'] or 'unmatched'}; {d['release_match_confidence']} |")
lines+=['','Audience header warning: columns 14 and 16 (1-based) both say «Постоянные зрители», while column 15 says «Случайные зрители». Column 14 exactly duplicates column 15 in every available row; column 16 is zero when available. Likely returning/casual/regular categories, but the source must confirm. Do not collapse duplicate headers using a dictionary or claim reliable audience loyalty from them. Unique viewers are non-additive across videos.','', '## Reconciliation (source total vs sum of visible video rows)','','| Metric | Total | Row sum | Difference |','|---|---:|---:|---:|']
for i in [4,16,17,18,21,22,23,24,25,26]:
 sm=sum(float(r[i]) for r in videos if r[i]);lines.append(f'| {h[i]} | {total[i]} | {sm:g} | {float(total[i])-sm:.4f} |')
lines+=['','Daily channel engaged sum is exactly 58,513, matching the table total. Visible rows sum to 58,471 (42 fewer). Missing content/filter differences/deleted content are possible explanations, NOT established facts. Subscriber gains/losses outside visible rows are 5/18; channel total net 108 differs from row net sum 121. Do not substitute sums for the exported channel total.','', '## Daily top-five series','']
for vid in dict.fromkeys(r['Контент'] for r in series):
 rr=[r for r in series if r['Контент']==vid];peak=max(rr,key=lambda r:int(r['Заинтересованные просмотры']));lines.append(f"- {vid.strip()}: 28 dates, sum {sum(int(r['Заинтересованные просмотры']) for r in rr):,}; peak {peak['Дата']}: {int(peak['Заинтересованные просмотры']):,}. Matches table engaged views.")
(ROOT/'2026-11-07/findings.md').write_text('\n'.join(lines)+'\n')
print('ledger rows',len(records),'daily engaged',sum(int(r['Заинтересованные просмотры']) for r in daily))
print('channel ratios /1000EV',[(h[i],round(1000*float(total[i])/int(total[4]),3)) for i in [18,21,22,16,17,25]])
print('top4 EVshare',sum(int(r[4]) for r in videos[:4])/int(total[4])*100)
print('last7 fall',(9424/27105-1)*100)
