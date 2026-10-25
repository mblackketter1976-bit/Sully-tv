/* TVmaze schedule data: CC BY-SA 4.0. See data/TV_GUIDE_LICENSE.md.
   Browser refresh avoids a paid backend or unattended website deployments. */
(function(global){
'use strict';
const SOURCE='tvmaze-us',LICENSE='https://creativecommons.org/licenses/by-sa/4.0/';
const NETWORKS={'40':{name:'CNN',channel:'CNN.us'},'201':{name:'MS NOW',channel:'MSNOW.us'},'467':{name:'BYUtv',channel:'BYUTV.us'}};
function normalize(episodes,now=Date.now()){
 const channels={};
 for(const episode of episodes){
  const show=episode?.show,network=show?.network,map=NETWORKS[String(network?.id)];
  if(!map||network.name!==map.name||network.country?.code!=='US')continue;
  if(typeof show.name!=='string'||!show.name.trim()||show.name.length>220)continue;
  if(typeof episode.runtime!=='number'||!Number.isFinite(episode.runtime)||episode.runtime<=0||episode.runtime>720)continue;
  if(typeof episode.airstamp!=='string'||!/(?:Z|[+-]\d\d:\d\d)$/.test(episode.airstamp))continue;
  const start=Date.parse(episode.airstamp),end=start+episode.runtime*60000;
  if(!Number.isFinite(start)||end<=now||start>now+3*86400000)continue;
  let title=show.name;
  if(typeof episode.name==='string'&&episode.name.trim()&&episode.name.length<150)title+=' · '+episode.name.trim();
  const programme={title,start:new Date(start).toISOString().replace('.000Z','Z'),end:new Date(end).toISOString().replace('.000Z','Z'),source:SOURCE};
  if(typeof episode.url==='string'&&/^https:\/\/www\.tvmaze\.com\//.test(episode.url))programme.url=episode.url;
  (channels[map.channel]??=[]).push(programme);
 }
 let count=0;
 for(const [channel,entries] of Object.entries(channels)){
  const kept=[];
  for(const entry of entries.sort((a,b)=>a.start.localeCompare(b.start))){
   if(!kept.some(p=>Date.parse(p.start)<Date.parse(entry.end)&&Date.parse(p.end)>Date.parse(entry.start)))kept.push(entry);
  }
  channels[channel]=kept;count+=kept.length;
 }
 return {updated:new Date(now).toISOString(),channels,sourceCounts:{[SOURCE]:count},sources:{[SOURCE]:{
  name:'TVmaze',url:'https://www.tvmaze.com/api#licensing',license:LICENSE,
  attribution:'TVmaze schedule data. Filtered to reviewed networks, converted to UTC and Sully JSON. Adapted data: CC BY-SA 4.0.',
  coverage:'Partial episode listings; not a complete channel schedule. Stream feeds may differ.'}}};
}
function fresh(data,now=Date.now(),maxAge=3600000){
 const age=now-Date.parse(data?.updated);
 return Number.isFinite(age)&&age>=-300000&&age<maxAge&&Object.values(data?.channels||{}).some(p=>Array.isArray(p)&&p.length);
}
async function readResponse(response){
 let raw='';
 if(response.body?.getReader){
  const reader=response.body.getReader(),decoder=new TextDecoder();let total=0;
  try{while(true){const {done,value}=await reader.read();if(done)break;total+=value.byteLength;if(total>5000000)throw Error('Schedule exceeds size cap');raw+=decoder.decode(value,{stream:true});}raw+=decoder.decode();}
  catch(error){await reader.cancel().catch(()=>{});throw error}finally{reader.releaseLock()}
 }else raw=await response.text();
 if(raw.length>5000000)throw Error('Schedule exceeds size cap');
 const data=JSON.parse(raw);if(!Array.isArray(data)||data.length>10000)throw Error('Unexpected schedule response');return data;
}
async function request(url,fetcher=fetch,pause=ms=>new Promise(resolve=>setTimeout(resolve,ms))){
 for(let attempt=0;attempt<3;attempt++){
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);
  let response;
  try{
   response=await fetcher(url,{signal:controller.signal,headers:{Accept:'application/json'}});
   if(response.ok)return await readResponse(response);
  }finally{clearTimeout(timer)}
  if(![429,500,502,503,504].includes(response.status)||attempt===2)throw Error('Schedule temporarily unavailable');
  await pause(1000*2**attempt);
 }
}
async function refresh({fetcher=fetch,now=Date.now(),pause}={}){
 const episodes=[];
 for(let offset=-1;offset<3;offset++){
  const date=new Date(now+offset*86400000).toISOString().slice(0,10);
  episodes.push(...await request('https://api.tvmaze.com/schedule?country=US&date='+date,fetcher,pause));
 }
 const data=normalize(episodes,now);
 if(!Object.keys(data.channels).length)throw Error('No current matched listings');
 return data;
}
const api={normalize,fresh,refresh,request};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else global.SullyGuideSource=api;
})(globalThis);
