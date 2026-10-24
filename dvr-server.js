// Optional self-hosted DVR backend. Node.js 20+ and ffmpeg required.
// Start: SULLY_DVR_TOKEN=<long-random-secret> node dvr-server.js
// Keep this service private behind HTTPS and an authenticated reverse proxy.
const http=require("node:http"),fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),{spawn}=require("node:child_process");
const root=path.resolve(process.env.SULLY_DVR_DIR||"./dvr-recordings");
fs.mkdirSync(root,{recursive:true});
const jobs=new Map(),port=Number(process.env.PORT||8787),token=process.env.SULLY_DVR_TOKEN;
if(!token||token.length<24)throw Error("Set SULLY_DVR_TOKEN to a secret of at least 24 characters");
const send=(res,status,obj)=>{res.writeHead(status,{"content-type":"application/json","cache-control":"no-store"});res.end(JSON.stringify(obj))};
const auth=req=>{const v=req.headers.authorization||"";const a=Buffer.from(v),b=Buffer.from("Bearer "+token);return a.length===b.length&&crypto.timingSafeEqual(a,b)};
function entries(){return fs.readdirSync(root).filter(n=>/^[a-f0-9-]{36}\.ts$/.test(n)).map(n=>{const st=fs.statSync(path.join(root,n));return {id:n.slice(0,-3),bytes:st.size,created:st.birthtime.toISOString(),active:jobs.has(n.slice(0,-3))}})}
async function body(req){let raw="";for await(const chunk of req){raw+=chunk;if(raw.length>8192)throw Error("Request too large")}return JSON.parse(raw||"{}")}
const server=http.createServer(async(req,res)=>{
try{
if(!auth(req))return send(res,401,{error:"Unauthorized"});
const u=new URL(req.url,"http://localhost");
if(req.method==="GET"&&u.pathname==="/api/recordings")return send(res,200,entries());
if(req.method==="POST"&&u.pathname==="/api/recordings"){
const {url,durationMinutes=60}=await body(req);
if(typeof url!=="string"||!/^https:\/\//.test(url)||url.length>2048)return send(res,400,{error:"HTTPS stream URL required"});
// Only permit hosts explicitly configured by the operator. Prevents arbitrary URL fetches.
const allow=(process.env.SULLY_DVR_ALLOWED_HOSTS||"").split(",").map(s=>s.trim().toLowerCase()).filter(Boolean);
if(!allow.includes(new URL(url).hostname.toLowerCase()))return send(res,403,{error:"Stream host not allowlisted"});
const duration=Number(durationMinutes);
if(!Number.isFinite(duration)||duration<1||duration>240)return send(res,400,{error:"Duration must be 1–240 minutes"});
if(jobs.size>=2)return send(res,429,{error:"Two simultaneous recordings maximum"});
const id=crypto.randomUUID(),name=id+".ts",dest=path.join(root,name);
const child=spawn("ffmpeg",["-nostdin","-hide_banner","-loglevel","error","-i",url,"-t",String(Math.round(duration*60)),"-map","0:v:0?","-map","0:a:0?","-c","copy","-f","mpegts",dest],{stdio:"ignore"});
jobs.set(id,child);
child.on("error",()=>jobs.delete(id));child.on("exit",()=>jobs.delete(id));
return send(res,202,{id,status:"recording",durationMinutes:duration});
}
const m=u.pathname.match(/^\/api\/recordings\/([a-f0-9-]{36})(\/download)?$/);
if(m){
const id=m[1],file=path.join(root,id+".ts");
if(req.method==="POST"&&!m[2]){const job=jobs.get(id);if(!job)return send(res,404,{error:"Not recording"});job.kill("SIGINT");return send(res,202,{status:"stopping"})}
if(!fs.existsSync(file))return send(res,404,{error:"Not found"});
if(req.method==="DELETE"&&!m[2]){if(jobs.has(id))return send(res,409,{error:"Stop recording first"});fs.unlinkSync(file);return send(res,200,{deleted:true})}
if(req.method==="GET"&&m[2]){res.writeHead(200,{"content-type":"video/mp2t","content-length":fs.statSync(file).size,"content-disposition":'attachment; filename="'+id+'.ts"'});return fs.createReadStream(file).pipe(res)}
}
send(res,404,{error:"Not found"});
}catch(e){send(res,400,{error:e.message||"Request failed"})}
});
server.listen(port,"127.0.0.1",()=>console.log("Sully DVR backend on localhost:"+port));
