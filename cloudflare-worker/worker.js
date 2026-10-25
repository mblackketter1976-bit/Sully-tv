// Sully TV watch availability API. Deploy as a free Cloudflare Worker.
// Set TMDB_TOKEN as an encrypted Worker secret, never in public GitHub Pages.
const headers={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET, OPTIONS","Access-Control-Allow-Headers":"Content-Type","Content-Type":"application/json"};
const respond=(obj,status=200)=>new Response(JSON.stringify(obj),{status,headers});
export default {async fetch(request,env){
 if(request.method==="OPTIONS")return new Response(null,{headers});
 const u=new URL(request.url);
 if(u.pathname!=="/availability")return respond({error:"Not found"},404);
 const query=(u.searchParams.get("q")||"").trim().slice(0,100);
 if(query.length<2)return respond({error:"Enter at least two characters"},400);
 if(!env.TMDB_TOKEN)return respond({error:"Service not configured"},503);
 const call=async(path)=>{const r=await fetch("https://api.themoviedb.org/3"+path,{headers:{Authorization:"Bearer "+env.TMDB_TOKEN,accept:"application/json"}});if(!r.ok)throw Error("TMDB error "+r.status);return r.json()};
 try{
 const search=await call("/search/multi?query="+encodeURIComponent(query)+"&include_adult=false&language=en-US&page=1");
 const candidates=(search.results||[]).filter(x=>x.media_type==="movie"||x.media_type==="tv").slice(0,5);
 const titles=await Promise.all(candidates.map(async x=>{
  const providers=await call("/"+x.media_type+"/"+x.id+"/watch/providers");
  const us=providers.results?.US||{};
  const pick=key=>(us[key]||[]).map(p=>({name:p.provider_name,logo:p.logo_path?"https://image.tmdb.org/t/p/w92"+p.logo_path:null}));
  return {id:x.id,type:x.media_type,title:x.title||x.name,year:(x.release_date||x.first_air_date||"").slice(0,4),poster:x.poster_path?"https://image.tmdb.org/t/p/w185"+x.poster_path:null,overview:x.overview||"",providers:{subscription:pick("flatrate"),free:pick("free"),ads:pick("ads"),rent:pick("rent"),buy:pick("buy")},providerLink:us.link||null}
 }));
 return respond({query,country:"US",titles,attribution:"Watch provider data from JustWatch via TMDB. Availability may change."})
 }catch(e){return respond({error:"Availability lookup failed"},502)}
}};