// usage: node drive.mjs job.json   job=[{scene,params,t0,n,fps,out}]
import puppeteer from 'puppeteer-core';import fs from 'fs';
const jobs=JSON.parse(fs.readFileSync(process.argv[2]));
const b=await puppeteer.launch({executablePath:process.env.HOME+'/.cache/puppeteer/chrome-headless-shell/linux-157.0.8103.78/chrome-headless-shell-linux64/chrome-headless-shell',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage();await p.setViewport({width:1080,height:1920});
p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>console.log('PAGE',m.text()));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForFunction('window.ready',{timeout:20000});
for(const j of jobs){fs.mkdirSync(j.out,{recursive:true});
  for(let i=0;i<j.n;i++){const t=(j.t0||0)+i/(j.fps||25);
    const d=await p.evaluate((s,t,pp)=>window.render(s,t,pp),j.scene,t,j.params);
    fs.writeFileSync(`${j.out}/f${String(i+1).padStart(4,'0')}.png`,Buffer.from(d.split(',')[1],'base64'));}
  console.log('done',j.scene,j.n);}
await b.close();
