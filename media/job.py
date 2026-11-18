# dim10: search NASA Image & Video Library + Wikimedia Commons video for footage; index + thumbnails.
import json, sys, os, urllib.request, urllib.parse, zipfile
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
def get(u,t=60):
    with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'dim10-footage-search/1.0'}),timeout=t) as r: return r.read()
Q=['earth from space station','earth timelapse','spacetime','gravity warps space','gravitational waves','galaxy zoom','hubble deep field','universe expansion','cosmic web','time lapse milky way','space station crew','astronaut window','large hadron collider','particle collision','eye','rings saturn','stars flythrough','nebula flythrough']
res=[]; zf=zipfile.ZipFile(os.path.join(out,'thumbs.zip'),'w'); seen=set()
for q in Q:
    try: d=json.loads(get('https://images-api.nasa.gov/search?media_type=video&q='+urllib.parse.quote(q)))
    except Exception as e: print('ERR',q,e); continue
    for it in d['collection']['items'][:12]:
        dd=it['data'][0]; nid=dd['nasa_id']
        if nid in seen: continue
        seen.add(nid)
        thumbs=[l['href'] for l in it.get('links',[]) if l.get('render')=='image']
        res.append({'src':'nasa','q':q,'id':nid,'title':dd.get('title'),'desc':(dd.get('description') or '')[:200],'center':dd.get('center'),'date':dd.get('date_created')})
        if thumbs:
            try: zf.writestr('nasa_%s.jpg'%nid.replace('/','_')[:80],get(thumbs[0]))
            except Exception as e: print('thumb',nid,e)
# Wikimedia Commons videos
for q in ['human eye macro','eye pupil close up','CERN LHC tunnel','tesseract rotation','hypercube','spacetime curvature animation','garden hose']:
    try:
        d=json.loads(get('https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=15&gsrsearch='+urllib.parse.quote(q+' filetype:video')+'&prop=imageinfo&iiprop=url|size|mime|extmetadata&iiurlwidth=320'))
    except Exception as e: print('C ERR',q,e); continue
    for p in (d.get('query') or {}).get('pages',{}).values():
        ii=(p.get('imageinfo') or [{}])[0]; t=p['title']
        if t in seen: continue
        seen.add(t); md=ii.get('extmetadata',{})
        res.append({'src':'commons','q':q,'id':t,'url':ii.get('url'),'w':ii.get('width'),'h':ii.get('height'),'dur':ii.get('duration'),'lic':(md.get('LicenseShortName') or {}).get('value'),'artist':(md.get('Artist') or {}).get('value','')[:120]})
        if ii.get('thumburl'):
            try: zf.writestr('com_%s.jpg'%str(p['pageid']),get(ii['thumburl']))
            except Exception as e: print('cthumb',t,e)
zf.close()
json.dump(res,open(os.path.join(out,'index.json'),'w'),ensure_ascii=False,indent=1)
print(len(res))
