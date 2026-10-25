/* Full HTML startup/navigation with controlled metadata and the real candidate guide.
   This does not test stream decoding, device hardware or broadcaster accuracy. */
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const root=process.cwd(),guide=JSON.parse(fs.readFileSync('data/tv-guide.json','utf8'));
 const channelIds=Object.keys(guide.channels);
 assert(channelIds.length>0,'This integration check requires a real sourced candidate');
 const start=Math.min(...Object.values(guide.channels).flat().map(p=>Date.parse(p.start)));
 const server=http.createServer((req,res)=>{
  const name=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  const file=path.resolve(root,'.'+(name==='/'?'/index.html':name));
  if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
  fs.readFile(file,(error,data)=>{
   if(error){res.writeHead(404);res.end();return}
   const type=file.endsWith('.html')?'text/html':file.endsWith('.json')?'application/json':file.endsWith('.js')?'application/javascript':'application/octet-stream';
   res.writeHead(200,{'Content-Type':type});res.end(data);
  });
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const origin='http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [1280,390]){
   const page=await browser.newPage({viewport:{width,height:1000},serviceWorkers:'block'});
   await page.clock.setFixedTime(new Date(start+5*60000));
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   const names={'CNN.us':'CNN','MSNOW.us':'MS NOW','BYUTV.us':'BYU TV'};
   await page.route('**/*',async route=>{
    const url=new URL(route.request().url());
    if(url.origin===origin){await route.continue();return}
    if(url.hostname==='iptv-org.github.io'){
     const file=url.pathname.split('/').pop();let data=[];
     if(file==='channels.json')data=channelIds.map(id=>({id,name:names[id]||id,country:'US',categories:[id==='BYUTV.us'?'entertainment':'news'],is_nsfw:false,closed:null}));
     if(file==='streams.json')data=channelIds.map(id=>({channel:id,url:'https://fixture.invalid/'+id+'.m3u8'}));
     if(file==='countries.json')data=[{code:'US',name:'United States'}];
     if(file==='feeds.json')data=channelIds.map(channel=>({channel,languages:['eng']}));
     await route.fulfill({json:data});return;
    }
    if(url.hostname==='fixture.invalid'){
     await route.fulfill({contentType:'application/vnd.apple.mpegurl',body:'#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:6\n#EXTINF:6,\nfixture.ts\n'});return;
    }
    await route.abort();
   });
   await page.goto(origin,{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>typeof channels!=='undefined'&&channels.length===3);
   await page.locator('.quickGuide').click();
   await page.getByRole('link',{name:'TVmaze',exact:true}).waitFor();
   assert.equal(await page.locator('.sullyRetroGuideStationButton').count(),3);
   assert((await page.locator('.sullyRetroGuideProgram').count())>=1);
   await page.getByRole('searchbox',{name:'Search stations',exact:true}).fill('BYU');
   assert.equal(await page.locator('.sullyRetroGuideStationButton').count(),1);
   await page.getByRole('searchbox',{name:'Search stations',exact:true}).fill('');
   assert.equal(await page.locator('.sullyRetroGuideStationButton').count(),3);
   assert.equal(await page.getByRole('link',{name:'CC BY-SA 4.0',exact:true}).count(),1);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'Document should not overflow horizontally');
   await page.screenshot({path:'guide-full-app-'+width+'.png',fullPage:true});
   assert.deepEqual(errors,[],'Full application raised JavaScript errors');
   console.log('PASS full-app guide startup/navigation/source credit/search at '+width+'px (controlled channel metadata; real candidate data)');
   await page.close();
  }
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
})().catch(error=>{console.error(error);process.exit(1)});
