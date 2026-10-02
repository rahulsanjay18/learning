#!/bin/sh
# Verify every pixel picture, then fill lesson and reference templates (scripts/*.template.html) with the verified art. Usage: sh scripts/build_lessons.sh
set -e
cd "$(dirname "$0")/.."
node scripts/verify_art.js > /tmp/verify_art.out
node -e '
const fs=require("fs"),m={};let cur;
for(const l of fs.readFileSync("/tmp/verify_art.out","utf8").split("\n")){
  let r=l.match(/^ok   (\w+)/); if(r){cur=r[1];m[cur]={};continue}
  r=l.match(/^\s+(art|marked):\s+(.*)$/); if(r&&cur)m[cur][r[1]]=r[2];}
const fill=f=>{const h=fs.readFileSync("scripts/"+f,"utf8").replace(/\{\{(\w+)\.(art|marked)\}\}/g,(_,k,v)=>m[k][v]);
  if(h.includes("{{"))throw new Error("unfilled placeholder in "+f); return h;};
for(const f of fs.readdirSync("scripts").filter(f=>f.endsWith(".template.html"))){
  let out, r=f.match(/^lesson-(\d+)\./);
  if(r) out="lessons/"+fs.readdirSync("lessons").find(x=>x.startsWith(r[1]+"-"));
  else out="reference/"+f.replace(/^reference-/,"").replace(".template","");
  fs.writeFileSync(out,fill(f)); console.log("built "+out);}'
