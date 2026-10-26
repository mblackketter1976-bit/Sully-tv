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
   let sourceCalls=0,failSource=false;
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
    if(url.hostname==='api.tvmaze.com'){
     sourceCalls++;
     if(failSource){await route.abort();return}
     await route.fulfill({json:[{name:'Episode',runtime:60,airstamp:new Date(start).toISOString(),show:{name:'Browser refresh fixture',network:{id:40,name:'CNN',country:{code:'US'}}}}]});return;
    }
    if(url.hostname==='fixture.invalid'){
     await route.fulfill({contentType:'application/vnd.apple.mpegurl',body:'#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:6\n#EXTINF:6,\nfixture.ts\n'});return;
    }
    await route.abort();
   });
   await page.addInitScript(data=>localStorage.setItem('sully-guide-cache-v1',JSON.stringify(data)),{...guide,updated:new Date(start+5*60000).toISOString()});
   await page.goto(origin,{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>typeof channels!=='undefined'&&channels.length===3);
   await page.locator('.quickGuide').click();
   await page.getByRole('link',{name:'TVmaze',exact:true}).waitFor();
   assert.equal(await page.locator('body.sullyGuideMode').count(),1);
   assert.equal(await page.locator('.sullyFloat').isVisible(),false,'Guide should not have overlapping floating controls');
   assert.equal(await page.getByRole('button',{name:'Back to top',exact:true}).count(),1);
   assert.equal(await page.locator('#content .sullyRoomLanguages').count(),0);
   const sizes=await page.locator('.sullyGuideActions button').evaluateAll(buttons=>buttons.map(button=>button.getBoundingClientRect().height));
   assert(sizes.every(height=>height>=44),'Guide action targets should be at least 44px tall');
   assert.equal(await page.locator('.sullyRetroGuideStationButton').count(),3);
   assert((await page.locator('.sullyRetroGuideProgram').count())>=1);
   await page.getByRole('searchbox',{name:'Search stations',exact:true}).fill('BYU');
   assert.equal(await page.locator('.sullyRetroGuideStationButton').count(),1);
   await page.getByRole('searchbox',{name:'Search stations',exact:true}).fill('');
   assert.equal(await page.locator('.sullyRetroGuideStationButton').count(),3);
   assert.equal(await page.getByRole('link',{name:'CC BY-SA 4.0',exact:true}).count(),1);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'Document should not overflow horizontally');
   await page.locator('.sullyRetroGuideScroll').scrollIntoViewIfNeeded();
   const clear=await page.locator('.sullyRetroGuideProgram').first().evaluate(button=>{
    const bounds=button.getBoundingClientRect(),scroll=button.closest('.sullyRetroGuideScroll').getBoundingClientRect();
    const station=button.closest('.sullyRetroGuideRow').firstElementChild.getBoundingClientRect();
    const x=Math.max(bounds.left,scroll.left,station.right)+10;
    const y=Math.max(0,Math.min(innerHeight-5,bounds.top+bounds.height/2));
    return document.elementFromPoint(x,y)?.closest('.sullyRetroGuideProgram')===button;
   });
   assert.equal(clear,true,'Visible guide programme must not be covered by navigation');
   await page.screenshot({path:'guide-full-app-'+width+'.png',fullPage:true});
   await page.evaluate(async()=>{sullyGuideData.updated=new Date(Date.now()-2*3600000).toISOString();await sullyRefreshGuideData()});
   assert.equal(sourceCalls,4,'Refresh should make exactly four bounded schedule requests');
   await page.locator('.quickGuide').click();
   await page.getByRole('button',{name:/Browser refresh fixture/}).first().waitFor();
   const downloadPromise=page.waitForEvent('download');
   await page.getByRole('link',{name:'Download current listings',exact:true}).click();
   const download=await downloadPromise;
   const exported=JSON.parse(fs.readFileSync(await download.path(),'utf8'));
   assert.match(exported.channels['CNN.us'][0].title,/Browser refresh fixture/,'Downloaded data must reflect refreshed listings');
   const callsBefore=sourceCalls;
   await page.evaluate(()=>sullyRefreshGuideData());
   assert.equal(sourceCalls,callsBefore,'Fresh cache should avoid more requests');
   failSource=true;
   const preserved=await page.evaluate(async()=>{const before=JSON.stringify(sullyGuideData.channels);sullyGuideData.updated=new Date(Date.now()-2*3600000).toISOString();await sullyRefreshGuideData();return JSON.stringify(sullyGuideData.channels)===before});
   assert.equal(preserved,true,'Network failure should preserve last usable channel data');
   assert.deepEqual(errors,[],'Full application raised JavaScript errors');
   console.log('PASS full-app guide startup/navigation/source credit/search at '+width+'px (controlled channel metadata; real candidate data)');
   await page.close();
  }
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
})().catch(error=>{console.error(error);process.exit(1)});
