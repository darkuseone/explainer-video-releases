import os,sys,json,requests
k=os.environ['PEXELS_API_KEY']
qs=sys.argv[1:]
for q in qs:
    r=requests.get('https://api.pexels.com/videos/search',params={'query':q,'per_page':8,'size':'medium'},headers={'Authorization':k},timeout=30).json()
    print('##',q)
    for v in r.get('videos',[]):
        print(v['id'],v['width'],v['height'],v['duration'],v['url'].split('/video/')[-1][:60],'|',v['user']['name'])
