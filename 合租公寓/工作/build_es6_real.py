# -*- coding: utf-8 -*-
# ES6 版真实状态栏：与 ES5 版功能完全一致（同 hz- 类名/同 KV 协议），仅引擎改用 ES6 重写
# 载体仍是 img onerror（per-message 自渲染唯一可靠方式）；ES6 已实测全支持
import json, os, re

OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")

# ---- ES6 引擎（箭头/let-const/模板字符串/可选链/for-of），单行、零双引号 ----
ENGINE = r'''<img src='x' style='display:none' onerror="(e=>{const run=()=>{let b=e,curr=e,c=5,fnd=false;while(c>0&&curr.parentNode&&curr.parentNode.tagName!=='BODY'){c--;curr=curr.parentNode;const cl=curr.classList;if(cl&&(cl.contains('item')||cl.contains('content')||cl.contains('vditor-reset')||cl.contains('vditor-ir')||cl.contains('vditor-preview'))){b=curr;fnd=true;c=0;}}if(!fnd){b=e.parentNode;if(b&&(b.tagName==='P'||b.tagName==='FONT'||b.tagName==='SPAN'))b=b.parentNode;}const trim=s=>s.replace(/(^\s+)|(\s+$)/g,'');const reg=/\[([^=\[\]]+)=([^\[\]]+)\]/g;const cur={},opts=[];let m;while((m=reg.exec(b.textContent))!==null){const k=trim(m[1]),v=trim(m[2]);if(k.indexOf('选项')===0&&k!=='选项标题')opts.push(v);else cur[k]=v;}const hist={};const els=document.querySelectorAll('.item, .content, .vditor-reset, .vditor-ir, .vditor-preview');for(const el of els){if(b.compareDocumentPosition(el)&2){const tx=el.textContent;if(tx.indexOf('[')===-1)continue;reg.lastIndex=0;let mm;while((mm=reg.exec(tx))!==null){hist[trim(mm[1])]=trim(mm[2]);}}}const gv=(k,fb)=>cur[k]!==undefined?cur[k]:(fb&&hist[k]!==undefined?hist[k]:null);const loc=gv('当前地点',true),tm=gv('当前时间',true),sit=gv('当前情境',true),rnd=gv('回复轮次',true);const present=(cur['在场角色']||'').split(/[|｜,，]+/).map(trim).filter(x=>x);const optTitle=cur['选项标题']||hist['选项标题']||'接下来：';let hash=`${loc}|${tm}|${sit}|${rnd}|${present.join('~')}`;for(const pn of present){hash+=`#${pn}:${gv(`角色-${pn}-好感`,true)}:${cur[`角色-${pn}-状态`]||''}`;}hash+=`||${opts.join('~')}`;let sid=e.getAttribute('data-sid');if(!sid){let h=0;for(let i=0;i<hash.length;i++)h=Math.imul(31,h)+hash.charCodeAt(i)|0;sid='hz'+h;e.setAttribute('data-sid',sid);}if(e.rdrNode&&document.body.contains(e.rdrNode)&&e.rdrNode.getAttribute('data-h')===hash)return;if(e.rdrNode?.parentNode)e.rdrNode.remove();const mk=cl=>{const d=document.createElement('div');if(cl)d.className=cl;return d;};const sp=(t,cl)=>{const s=document.createElement('span');if(cl)s.className=cl;if(t)s.textContent=t;return s;};const nC=mk('hz-box');nC.id=sid;nC.setAttribute('data-h',hash);nC.onmousedown=ev=>ev.stopPropagation();nC.onclick=ev=>ev.stopPropagation();const ti=mk('hz-title');ti.textContent='合租公寓 · 当前状态';nC.appendChild(ti);const env=mk('hz-env');const addRow=(lbl,val)=>{if(!val)return;const r=mk('hz-row');r.appendChild(sp(lbl,'hz-lbl'));r.appendChild(sp(val,'hz-val'));env.appendChild(r);};addRow('时间',tm);addRow('地点',loc);addRow('此刻',sit);nC.appendChild(env);if(present.length){const cwrap=mk('hz-chars');for(const pn of present){const card=mk('hz-card');const head=mk('hz-chead');const av=mk('hz-av');av.textContent=pn.charAt(0);head.appendChild(av);const nfo=mk('hz-cinfo');const nmd=mk('hz-cname');nmd.textContent=pn;nfo.appendChild(nmd);const role=gv(`角色-${pn}-身份`,true);if(role){const rd=mk('hz-crole');rd.textContent=role;nfo.appendChild(rd);}head.appendChild(nfo);const fav=gv(`角色-${pn}-好感`,true);const fm=fav?.match(/(-?\d+)[^\d]+(\d+)/);if(fm)head.appendChild(sp(`好感 ${fm[1]}/${fm[2]}`,'hz-fav'));card.appendChild(head);if(fm){const bg=mk('hz-bar');const fl=mk('hz-fill');const mx=parseInt(fm[2]);const pct=mx>0?Math.min(100,Math.max(0,parseInt(fm[1])/mx/0.01)):0;fl.style.width=pct+'%';bg.appendChild(fl);card.appendChild(bg);}const stt=cur[`角色-${pn}-状态`];if(stt){const sd=mk('hz-cst');sd.textContent=stt;card.appendChild(sd);}cwrap.appendChild(card);}nC.appendChild(cwrap);}if(opts.length){const ow=mk('hz-opts');const oh=mk('hz-ohead');oh.textContent=optTitle;ow.appendChild(oh);for(const o of opts){const parts=o.split(/[|｜]+/);const ob=mk('hz-opt');const ot=mk('hz-ot');ot.textContent=parts[0]||'选项';ob.appendChild(ot);if(parts[1]){const od=mk('hz-od');od.textContent=parts[1];ob.appendChild(od);}ob.setAttribute('data-cmd',parts[0]||'');ob.onclick=function(ev){ev.stopPropagation();const a=document.querySelector('.uni-textarea-textarea')||document.querySelector('textarea');if(a){a.value=this.getAttribute('data-cmd');a.dispatchEvent(new Event('input',{bubbles:true}));}};ow.appendChild(ob);}nC.appendChild(ow);}if(rnd){const rb=mk('hz-rnd');rb.textContent=`第 ${rnd} 轮`;nC.appendChild(rb);}if(e.parentNode)e.parentNode.insertBefore(nC,e.nextSibling);e.rdrNode=nC;};run();let rc=5;const iv=setInterval(()=>{if(!document.body.contains(e)){if(e.rdrNode?.parentNode)e.rdrNode.remove();clearInterval(iv);return;}if(e.rdrNode&&!document.body.contains(e.rdrNode))run();rc--;if(rc<=0)clearInterval(iv);},500);})(this)">'''

# 复用现成 json 的其余 4 条规则，只替换雷达引擎
src = json.load(open(os.path.join(OUT, "正则导入.json"), encoding="utf-8"))
rules = []
for r in src["regex_scripts"]:
    if r["scriptName"] == "雷达引擎":
        rules.append({"id": -1, "scriptName": "雷达引擎(ES6)", "findRegex": "<ztl>", "replaceString": ENGINE})
    else:
        rules.append(r)

out = {"pageDepth": src["pageDepth"], "statusbar": src["statusbar"],
       "beginning": src["beginning"], "regex_scripts": rules}

path = os.path.join(OUT, "正则导入-es6版.json")
json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 自检
inner = ENGINE.split('onerror="', 1)[1].rsplit('">', 1)[0]
print("已生成:", path)
print("引擎自检: 双引号=%d | 箭头=%d | const=%d | let=%d | 模板串=%d | 可选链=%d"
      % (inner.count('"'), inner.count('=>'), inner.count('const '),
         inner.count('let '), inner.count('`'), inner.count('?.')))
for r in out["regex_scripts"]:
    print("  %-16s replaceString=%d %s" % (r["scriptName"], len(r["replaceString"]),
          "OK" if len(r["replaceString"]) <= 10000 else "!!超限"))
json.load(open(path, encoding="utf-8")); print("JSON OK")

# 预览
reg = out
def rule(n): return [x for x in reg["regex_scripts"] if x["scriptName"] == n][0]["replaceString"]
card = json.load(open(os.path.join(OUT, "角色卡.json"), encoding="utf-8"))
CSS, BEAUTIFY = rule("响应式样式部署"), rule("全局美化激活")
narrative, _, datablock = card["first_mes"].partition("<ztl>")
import html as _h
narr = "<font>" + _h.escape(narrative).replace("\n", "<br>") + "</font>"
beacons = re.sub(r"\[([^=\[\]]+)=([^\[\]]+)\]",
                 lambda m: '<span style="display:none">[%s=%s]</span>' % (m.group(1), m.group(2)), datablock)
page = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>ES6版预览</title>'
        '<style>body{margin:0;background:#fbf3e9;font-family:system-ui,sans-serif}.chat{max-width:640px;margin:0 auto;padding:12px 12px 80px}'
        '.note{max-width:640px;margin:12px auto;padding:10px 14px;background:#fff8f0;border:1px solid #e6c9a8;border-radius:10px;color:#7a6450;font-size:13px}</style>'
        + CSS + BEAUTIFY + '</head><body class="z-enabled">'
        '<div class="note"><b>ES6 版状态栏预览</b>：引擎用 ES6 重写，功能与 ES5 版一致。</div>'
        '<div class="chat"><div class="chat-body"><div class="item"><div class="content left">'
        + narr + "\n" + beacons + "\n" + ENGINE +
        '</div></div></div></div>'
        '<div class="chat-bottom"><div class="uni-textarea"><div class="chat-input-scope"><textarea class="uni-textarea-textarea"></textarea></div></div></div>'
        '</body></html>')
open(os.path.join(OUT, "预览-es6版.html"), "w", encoding="utf-8").write(page)
print("已生成 预览-es6版.html")
