const fs = require('fs');
const path = require('path');
const cp = require('child_process');
const {chromium} = require('C:/Users/LOQ/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..','Bo_nop_De10_MPL');
const shots=path.join(root,'minh_chung','anh_demo');fs.mkdirSync(shots,{recursive:true});
const python='C:/Users/LOQ/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const docker='C:/Users/LOQ/AppData/Local/Programs/DockerDesktop/resources/bin/docker.exe';
const child=cp.spawn(python,['demo.py','--engine','docker','--docker-bin',docker,'--interactive'],{cwd:path.join(root,'demo'),env:{...process.env,PYTHONIOENCODING:'utf-8'},windowsHide:true});
let output='';let ended=false;child.stdout.on('data',d=>{output+=d.toString();});child.stderr.on('data',d=>{output+=d.toString();});child.on('close',()=>ended=true);
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function until(s){const deadline=Date.now()+45000;while(!output.includes(s)){if(ended||Date.now()>deadline)throw new Error('Waiting for '+s+' '+output);await delay(100);}}
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1});let meta=[];
 async function shot(name,url){await page.goto(url,{waitUntil:'networkidle'});await page.screenshot({path:path.join(shots,name+'.png')});meta.push({name,url,captured_utc:new Date().toISOString()});}
 await until('KT1: Open');
 await shot('01_nguon','http://127.0.0.1:18080');
 await shot('02_du_lieu_nguon','http://127.0.0.1:18080/data/shipments.json');
 child.stdin.write('\n');await until('KT2: Refresh');
 await shot('03_dich','http://127.0.0.1:18080');
 await shot('04_health_dich','http://127.0.0.1:18080/health');
 child.stdin.write('\n');
 await until('failure_detected');
 try {await page.goto('http://127.0.0.1:18080/health',{waitUntil:'domcontentloaded'});await page.screenshot({path:path.join(shots,'05_loi_503.png')});meta.push({name:'05_loi_503',url:page.url(),captured_utc:new Date().toISOString()});}catch(e){meta.push({error:String(e)});}
 await until('KT3: Show');await shot('06_quay_ve_nguon','http://127.0.0.1:18080');
 child.stdin.write('\n');await browser.close();
 while(!ended)await delay(100);
 fs.writeFileSync(path.join(shots,'capture_metadata.json'),JSON.stringify(meta,null,2));
 fs.writeFileSync(path.join(shots,'console_capture.txt'),output);
 const latest=JSON.parse(fs.readFileSync(path.join(root,'demo','runs','latest.json'),'utf8'));
 fs.cpSync(latest.evidence_dir,path.join(root,'minh_chung','demo_video'),{recursive:true});
 console.log(output);console.log('CAPTURED',meta.length);
})().catch(e=>{console.error(e);child.stdin.write('\n\n\n');process.exitCode=1;});
