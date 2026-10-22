import sys,json,requests,os,urllib.parse
H={'User-Agent':'moonbot/1.0 (markus explainer)'}
meta=json.load(open('meta.json'))
for t in sys.argv[1:]:
    t,name=t.split('=>')
    r=requests.get('https://commons.wikimedia.org/w/api.php',params={'action':'query','titles':t,'prop':'imageinfo','iiprop':'url|extmetadata|size','iiurlwidth':2400,'format':'json'},headers=H).json()
    p=list(r['query']['pages'].values())[0]['imageinfo'][0]; m=p['extmetadata']
    lic=m.get('LicenseShortName',{}).get('value'); art=m.get('Artist',{}).get('value','')
    u=p.get('thumburl') or p['url']
    open(name,'wb').write(requests.get(u,headers=H).content)
    meta[name]={'source':p['descriptionurl'],'license':lic,'author':art[:150],'w':p['width'],'h':p['height']}
    print(name,lic,'|',art[:80])
json.dump(meta,open('meta.json','w'),indent=1,ensure_ascii=False)
