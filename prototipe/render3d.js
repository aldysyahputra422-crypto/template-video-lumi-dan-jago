// Render uji3d.html frame demi frame (deterministik). Pakai: node render3d.js <folder_frame> [fps]
const http=require('http'),fs=require('fs'),path=require('path');const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..'),OUT=process.argv[2],FPS=+(process.argv[3]||30);
const MIME={'.html':'text/html','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml','.woff2':'font/woff2'};
const srv=http.createServer((q,s)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);s.end();return}s.writeHead(200,{'Content-Type':MIME[path.extname(f)]||'application/octet-stream'});s.end(d)})});
srv.listen(0,'127.0.0.1',async()=>{const port=srv.address().port;fs.mkdirSync(OUT,{recursive:true});
 const b=await chromium.launch({args:['--enable-unsafe-swiftshader','--use-angle=swiftshader','--ignore-gpu-blocklist']});
 const p=await b.newPage({viewport:{width:720,height:1280}});p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto(`http://127.0.0.1:${port}/prototipe/uji3d.html`);await p.waitForFunction(()=>window.READY===true,null,{timeout:60000});
 await p.evaluate(()=>document.fonts.ready);
 const dur=JSON.parse(fs.readFileSync(path.join(__dirname,'timeline.json'))).durasi;const n=Math.round(dur*FPS);const t0=Date.now();
 for(let i=0;i<n;i++){await p.evaluate(t=>window.render(t),i/FPS);await p.screenshot({path:path.join(OUT,`f${String(i).padStart(5,'0')}.png`)});}
 console.log(n,'frame',((Date.now()-t0)/1000).toFixed(0),'dtk');await b.close();srv.close();});
