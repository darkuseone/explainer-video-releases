import os,sys,json,requests
k=os.environ['PEXELS_API_KEY']; ids=sys.argv[1:]
meta=json.load(open('meta.json')) if os.path.exists('meta.json') else {}
for i in ids:
    r=requests.get(f'https://api.pexels.com/videos/videos/{i}',headers={'Authorization':k},timeout=30).json()
    fs=[f for f in r['video_files'] if f['file_type']=='video/mp4' and f.get('width')]
    fs.sort(key=lambda f:abs(min(f['width'],f['height'])-1080)+ (0 if min(f['width'],f['height'])>=1080 else 500))
    f=fs[0]; p=f'px_{i}.mp4'
    if not os.path.exists(p):
        open(p,'wb').write(requests.get(f['link'],timeout=120).content)
    meta[p]={'source':r['url'],'author':r['user']['name'],'author_url':r['user']['url'],'license':'Pexels License (free commercial use, no attribution required)','w':f['width'],'h':f['height']}
    print(p,f['width'],f['height'])
json.dump(meta,open('meta.json','w'),indent=1)
