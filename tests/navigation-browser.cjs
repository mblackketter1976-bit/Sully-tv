const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const root=process.cwd();
 const server=http.createServer((req,res)=>{
  const name=new URL(req.url,'http://local').pathname;
  const file=path.resolve(root,'.'+(name==='/'?'/index.html':name));
  if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
  fs.readFile(file,(error,data)=>{if(error){res.writeHead(404);res.end();return}res.setHeader('Content-Type',file.endsWith('.html')?'text/html':file.endsWith('.js')?'application/javascript':file.endsWith('.json')?'application/json':'application/octet-stream');res.end(data)});
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const origin='http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [320,390,768,1920]){
   const page=await browser.newPage({viewport:{width,height:900},serviceWorkers:'block'}),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',async route=>{
    const url=new URL(route.request().url());
    if(url.origin===origin)return route.continue();
    if(url.hostname==='iptv-org.github.io'){
     const file=url.pathname.split('/').pop();let data=[];
     if(file==='channels.json')data=[{id:'CNN.us',name:'CNN',country:'US',categories:['news'],is_nsfw:false,closed:null}];
     if(file==='streams.json')data=[{channel:'CNN.us',url:'https://fixture.invalid/cnn.m3u8'}];
     if(file==='countries.json')data=[{code:'US',name:'United States'}];
     if(file==='feeds.json')data=[{channel:'CNN.us',languages:['eng']}];
     return route.fulfill({json:data});
    }
    return route.abort();
   });
   await page.goto(origin,{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>typeof channels!=='undefined'&&channels.length===1);
   for(const theme of ['classic','space','christmas']){
    await page.evaluate(theme=>sullyApplyTheme(theme),theme);
    for(const position of ['top','bottom']){
     await page.evaluate(position=>scrollTo(0,position==='top'?0:document.documentElement.scrollHeight),position);
     await page.waitForTimeout(80);
     const layout=await page.locator('#sullyNavigationDock').evaluate(dock=>{
      const rect=dock.getBoundingClientRect(),buttons=[...dock.querySelectorAll('button')],boxes=buttons.map(b=>b.getBoundingClientRect());
      return {fixed:getComputedStyle(dock).position,bottom:rect.bottom,height:rect.height,viewport:innerHeight,
       hits:buttons.every((b,i)=>{const r=boxes[i];return r.height>=44&&document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)?.closest('button')===b}),
       overlap:boxes.some((a,i)=>boxes.some((b,j)=>i<j&&a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top)),
       overflow:document.documentElement.scrollWidth>innerWidth,
       reserved:parseFloat(getComputedStyle(document.body).paddingBottom)>=rect.height};
     });
     assert.equal(layout.fixed,'fixed');assert(Math.abs(layout.bottom-layout.viewport)<1,JSON.stringify(layout));
     if(layout.overflow){console.log('OVERFLOW',width,theme,await page.evaluate(()=>[...document.querySelectorAll('body *')].filter(el=>{const r=el.getBoundingClientRect();return r.width&&r.right>innerWidth+1}).map(el=>({tag:el.tagName,id:el.id,cls:el.className,left:el.getBoundingClientRect().left,right:el.getBoundingClientRect().right})).slice(0,20)));await page.screenshot({path:'navigation-'+width+'.png',fullPage:true})}
     assert(layout.hits,JSON.stringify(layout));assert(!layout.overlap);assert(!layout.overflow);assert(layout.reserved);
    }
    await page.locator('#sullyCategories').click();
    assert.equal(await page.locator('#sullyCategories').getAttribute('aria-expanded'),'true');
    const menu=await page.locator('#sullyMenu').boundingBox(),dock=await page.locator('#sullyNavigationDock').boundingBox();
    assert(menu.y>=0&&menu.y+menu.height<=dock.y,'Category menu must stay above navigation');
    await page.keyboard.press('Escape');assert.equal(await page.locator('#sullyMenu').isVisible(),false);
    await page.locator('#sullyNavigationDock').getByRole('button',{name:'Find channels'}).click();
    assert.equal(await page.locator('#search').evaluate(el=>el===document.activeElement),true);
    // Use the exact registered category to preserve spelling and existing routing.
    await page.evaluate(()=>sullyCategory(tabs.find(t=>t.includes('Murder Mystery'))));
    assert.equal(await page.locator('#sullyBack').isEnabled(),true);
    await page.locator('#sullyBack').click();
    await page.locator('#sullyHome').click();
    assert.equal(await page.evaluate(()=>tab),'🏠 Home');
    await page.locator('.quickGuide').click();
    assert.equal(await page.evaluate(()=>tab),'📋 TV Guide');
    await page.locator('#sullyHome').click();
    await page.evaluate(()=>{scrollTo(0,document.documentElement.scrollHeight)});
    if(theme==='space')await page.screenshot({path:'navigation-'+width+'.png',fullPage:true});
   }
   const quick=await page.locator('.sullyQuickBar button').evaluateAll(buttons=>buttons.map(b=>{const r=b.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}}));
   assert.equal(quick.length,7);assert(quick.every(r=>r.h>=44));
   assert(!quick.some((a,i)=>quick.some((b,j)=>i<j&&a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y)));
   await page.evaluate(()=>openSullyThemes());
   await page.locator('#sullyThemeExitFixed').click();
   assert.equal(await page.locator('#sullyQuickPanel').isVisible(),false,'Theme Done must close panel');
   assert.deepEqual(errors,[]);
   console.log('PASS navigation, themes, category menu, search, back/home, guide and quick-control layout at '+width+'px');
   await page.close();
  }
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
})().catch(error=>{console.error(error);process.exit(1)});
