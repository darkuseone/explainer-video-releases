# Search NASA Image & Video Library + NASA SVS for footage; save index + thumbnails.
# rerun
import json, sys, os, urllib.request, urllib.parse, zipfile, io
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
def get(u,t=60):
    with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=t) as r: return r.read()
Q=['black hole visualization','black hole accretion disk','black hole simulation','gamma ray burst','big bang','universe expansion','galaxy zoom','very large array','radio telescope','nebula flythrough','hubble deep field','star field','supernova','neutron star','event horizon','wormhole','time lapse milky way','james webb']
res=[]; zf=zipfile.ZipFile(os.path.join(out,'thumbs.zip'),'w')
seen=set()
for q in Q:
    try: d=json.loads(get('https://images-api.nasa.gov/search?media_type=video&q='+urllib.parse.quote(q)))
    except Exception as e: print('ERR',q,e); continue
    for it in d['collection']['items'][:10]:
        dd=it['data'][0]; nid=dd['nasa_id']
        if nid in seen: continue
        seen.add(nid)
        try: man=json.loads(get(it['href']))
        except Exception: man=[]
        mp4=[u for u in man if u.endswith('.mp4')]
        thumbs=[l['href'] for l in it.get('links',[]) if l.get('render')=='image']
        rec={'src':'nasa','q':q,'id':nid,'title':dd.get('title'),'desc':(dd.get('description') or '')[:300],'center':dd.get('center'),'date':dd.get('date_created'),'mp4':mp4[:6],'thumb':thumbs[:1]}
        res.append(rec)
        if thumbs:
            try: zf.writestr('nasa_%s.jpg'%nid.replace('/','_'),get(thumbs[0]))
            except Exception as e: print('thumb',nid,e)
# NASA SVS
for q in ['black hole','gamma-ray burst','big bang','accretion disk','wormhole','starfield','galaxy']:
    try: d=json.loads(get('https://svs.gsfc.nasa.gov/api/search/?search='+urllib.parse.quote(q)+'&limit=15'))
    except Exception as e: print('SVS ERR',q,e); continue
    for it in d.get('results',[])[:15]:
        sid=it.get('id'); 
        if ('svs',sid) in seen: continue
        seen.add(('svs',sid))
        rec={'src':'svs','q':q,'id':sid,'title':it.get('title'),'desc':(it.get('description') or '')[:300],'url':it.get('url'),'date':it.get('release_date')}
        try:
            full=json.loads(get('https://svs.gsfc.nasa.gov/api/%s'%sid))
            media=[]
            for g in full.get('media_groups',[]):
                for m in g.get('items',[]):
                    mi=m.get('instance') or {}
                    u=mi.get('url'); 
                    if u: media.append({'url':u,'w':mi.get('width'),'h':mi.get('height'),'type':mi.get('media_type'),'alt':(mi.get('alt_text') or '')[:120]})
            rec['media']=media[:40]
            th=[m['url'] for m in media if m['type']=='Image' and (m['w'] or 0)<=1200]
            if th: zf.writestr('svs_%s.jpg'%sid,get(th[0]))
        except Exception as e: print('svs item',sid,e)
        res.append(rec)
zf.close()
json.dump(res,open(os.path.join(out,'index.json'),'w'),ensure_ascii=False,indent=1)
print(len(res))
