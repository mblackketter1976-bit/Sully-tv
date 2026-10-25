const fs=require('fs');
const assert=require('assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const html=fs.readFileSync('index.html','utf8');
 const source=html.slice(html.indexOf('let sullyGuideData=null;'),html.indexOf('\nfunction remember(c)'));
 for(const width of [1280,390]){
  const page=await browser.newPage({viewport:{width,height:900}});
  const styles=[...html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)].map(m=>m[1]).join('\n');
  await page.setContent('<style>'+styles+'</style><div id="status"></div><div id="content"></div>');
  await page.evaluate(({source})=>{
   window.$=id=>document.getElementById(id);
   window.channels=[{id:'news',name:'Fixture News',country:'US',categories:['news']},{id:'sports',name:'Fixture Sports',country:'ES',categories:['sports']}];
   window.streams=new Map(channels.map(c=>[c.id,['https://example.invalid/stream']]));
   window.unavailable=new Set();window.sullyFailed=()=>false;
   window.sullyEnglishOnly=false;window.sullySelectedLanguage='all';
   window.sullyDetectLanguage=c=>({confidence:'known',codes:[c.id==='news'?'en':'es']});
   window.tab='📋 TV Guide';window.watchChannel=c=>window.chosen=c.id;
   window.fetch=async()=>({ok:true,json:async()=>window.fixture});
   window.fixture={updated:new Date().toISOString(),channels:{}};
   (0,eval)(source+';window.renderGuide=renderGuide;window.setGuide=d=>{sullyGuideData=d;document.getElementById("content").replaceChildren();renderGuide()};');
   renderGuide();
  },{source});
  await page.waitForTimeout(50);
  assert.equal(await page.locator('.sullyRetroGuideStationButton').count(),2);
  assert.equal(await page.locator('.sullyRetroGuideProgram').count(),0);
  await page.getByRole('button',{name:'Show English-language channels only'}).click();
  assert.equal(await page.locator('.sullyRetroGuideStationButton').count(),1);
  await page.getByRole('button',{name:'Show English-language channels only'}).click();
  await page.getByRole('searchbox').fill('Sports');
  assert.equal(await page.locator('.sullyRetroGuideStationButton').count(),1);
  await page.getByRole('searchbox').fill('');
  await page.evaluate(()=>{
   const base=new Date();base.setMinutes(Math.floor(base.getMinutes()/30)*30,0,0);
   window.fixture={updated:new Date().toISOString(),channels:{news:[{title:'Fixture mid-slot programme',source:'offline-fixture',start:new Date(+base+300000).toISOString(),end:new Date(+base+1200000).toISOString()}]}};
   setGuide(fixture);
  });
  await page.waitForTimeout(50);
  assert.equal(await page.locator('.sullyRetroGuideProgram').count(),1);
  await page.locator('.sullyRetroGuideProgram').click();
  assert.equal(await page.evaluate(()=>chosen),'news');
  await page.getByRole('button',{name:'Later ▶'}).click();
  assert.equal(await page.locator('.sullyRetroGuideProgram').count(),0);
  await page.getByRole('button',{name:'NOW',exact:true}).click();
  assert.equal(await page.locator('.sullyRetroGuideProgram').count(),1);
  await page.evaluate(()=>{
   const p=fixture.channels.news[0];
   fixture.sources={"tvmaze-us":{name:"TVmaze"}};
   fixture.channels.news.push({...p,title:"Second short programme",start:new Date(Date.parse(p.end)+60000).toISOString(),end:new Date(Date.parse(p.end)+240000).toISOString()});
   setGuide(fixture);
  });
  await page.waitForTimeout(50);
  assert.equal(await page.locator('.sullyRetroGuideProgram').count(),2);
  assert.equal(await page.getByRole('link',{name:'TVmaze',exact:true}).count(),1);
  assert.equal(await page.getByRole('link',{name:'CC BY-SA 4.0',exact:true}).count(),1);
  await page.screenshot({path:'guide-'+width+'.png',fullPage:true});
  await page.evaluate(()=>{fixture.updated=new Date(Date.now()-48*3600000).toISOString();setGuide(fixture)});
  await page.waitForTimeout(50);
  assert.equal(await page.locator('.sullyRetroGuideProgram').count(),0);
  assert.match(await page.getByRole('status').textContent(),/Stale schedule/);
  assert.equal(await page.locator('.sullyRetroGuideStationButton').count(),2);
  console.log('PASS guide browser checks at '+width+'px: empty data, language, search, mid-slot listing, watch, time navigation, stale data');
  await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
