#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the witch-ability regex pack:
   - reuse 主骨架 + CSS from the original upload verbatim
   - replace the JS particle engine with a glyph/morph engine
   - split glyph paths into a nested [能力造型库] segment (<20k each)
"""
import json, os

SRC = "/root/.claude/uploads/976cd92e-1f4b-4258-96bd-383e3ee1d9d4/89a3266c-________4.json"
OUT = "/home/user/-/witch-ability.json"

orig = json.load(open(SRC, encoding="utf-8"))
by = {s["scriptName"]: s for s in orig["regex_scripts"]}
skeleton = by["主骨架"]
css = by["CSS"]

# ---- ability text table (fields 0..6 reused from original) + glyph key (field 7) ----
A = [
 ["星门启录","Astral Keygate","门不是入口，是被星光承认的许可。","在短时间内开启一枚只允许 user 通过的星门，可越过封锁、距离或一次失败判定。","指定一个可视或已知坐标，开启短距星门并重置一次进入条件。","开场时银白钥孔在空中展开，十三枚星钉依次点亮通行许可。","星门/钥孔/通行","key"],
 ["镜廊折光","Mirror Corridor","真正的方向，藏在第十三面镜子之后。","制造一组镜廊折面，让敌人的视线、瞄准和判断在多重倒影中偏移。","让一次锁定、追踪或攻击目标发生折射，生成可操控的虚假落点。","开场时两列银镜从星雾中升起，user 的影子被折成多重轨迹。","镜廊/折光/偏移","rune"],
 ["晶钟裁时","Crystal Chronometer","时间不是河流，是可以被裁开的晶面。","召唤晶钟结构，将一个动作拆成预备、发生、余波三个切面。","选择其中一个切面延迟或提前，使行动节奏被 user 重新排序。","开场时六角晶钟悬在胸前，指针划过透明的时间切片。","晶钟/裁时/节奏","hourglass"],
 ["银线织命","Silver Loom","命运没有线头，我替它织出线头。","把人物、物品和地点之间的关系显影成银线，并允许 user 临时重接其中一段。","改变一个关系连接，例如追踪对象、保护对象、仇恨对象或归属对象。","开场时巨大织机浮现，银线在 user 指尖结成新的命运纹路。","银线/织命/关系","rune"],
 ["假面授冠","Crowned Mask","戴上王冠之前，先选择要扮演的奇迹。","召唤三枚假面，让 user 临时获得一种演出身份：守护者、欺诈者或处刑者。","选择一种身份获得对应强化，但身份会限制本回合的行动风格。","开场时白银假面围绕王冠旋转，最终有一枚落到 user 面前。","假面/王冠/身份","crown"],
 ["光谱静域","Prism Quietus","所有噪声，都能被拆成安静的颜色。","展开棱镜静域，把混乱能量分解成数段可见光谱，削弱冲击和干扰。","降低范围内爆发、污染、恐惧或精神噪声的强度，并提取一枚光谱残片。","开场时透明棱镜张开，战场噪声被分解成银紫色的光带。","光谱/静域/分解","rune"],
 ["纸星律令","Paperstar Edict","写在纸星上的一句话，可以短暂命令现实。","折出纸星律令，将一句简短规则贴在场景上，规则只持续一个关键节点。","建立一条短句规则，例如不可追逐、不可越界、不可直视。","开场时纸星从掌心飞散，组成一页发光的临时律令。","纸星/律令/规则","rune"],
 ["星弦改写","Stellar Strings","记忆会撒谎，但弦不会。","把一段记忆、承诺或情绪挂到星弦上，拨动后可调整它的轻重与方向。","弱化一段负面记忆或强化一个誓约动机，使角色立场发生细微偏转。","开场时竖琴状星弦拉开，音符沿着银色轨道回旋。","星弦/改写/情绪","rune"],
 ["画框造境","Framecraft","画框不是边界，是新世界的草稿。","展开一枚魔法画框，在框内生成一小片可编辑场景。","临时改写框内地形、遮挡、出口或物体位置，但不能直接改写生命。","开场时发光画框落下，星尘笔触把空白处描成可进入的场景。","画框/造境/地形","rune"],
 ["花骸炼成","Bloom Relic","凋零不是死亡，是被炼成新的容器。","把破损、废弃或被诅咒的物质炼成花骸圣遗物，短暂转化其用途。","将一个无效物、废墟或负面残留转化为护盾、路标或一次性媒介。","开场时银白花骸从裂缝中生长，碎片被炼成发光遗物。","花骸/炼成/转化","rune"],
 ["星棋布局","Astral Gambit","我不预言胜负，我先摆好棋盘。","把战场抽象成星棋盘，标记十三个关键节点并指定其中一个为优势点。","下一次行动围绕优势点获得路线、距离或配合修正。","开场时星棋节点铺开，user 选中的棋位亮成银紫色。","星棋/布局/节点","rune"],
 ["银秤裁决","Silver Verdict","公平不是慈悲，是让代价回到该去的人手里。","召唤银秤称量一次伤害、承诺或牺牲，并把不对等的部分重新分配。","在一次交换中调整代价归属，使承受者、获益者或偿还者发生变化。","开场时银秤浮起，两侧砝码化成星光重新落位。","银秤/裁决/代价","rune"],
 ["月冠燃素","Lunar Phlogiston","月冠点燃时，奇迹会获得自己的温度。","点燃月冠燃素，使 user 的下一项魔法获得更强表现，但会留下可见光痕。","强化下一次能力效果或范围，同时生成一枚可被追踪的月冠痕迹。","开场时银月王冠燃起紫白火焰，光痕沿发梢和指尖蔓延。","月冠/燃素/强化","rune"],
]
Ajs = json.dumps(A, ensure_ascii=False, separators=(",", ":"))

# ---- glyph library (nested segment [能力造型库]) ----
# each returns an array of polylines in a roughly -120..120 coordinate space.
# ring()/arc() helpers live in the engine closure, available at call time.
GLYPH = (
"{"
"key:function(){return[ring(0,-50,42),ring(0,-50,18),[[0,-8],[0,84]],[[0,56],[24,56],[24,40]],[[0,76],[32,76],[32,58]]];},"
"hourglass:function(){return[[[-54,-80],[54,-80]],[[-54,80],[54,80]],[[-48,-74],[0,0],[-48,74]],[[48,-74],[0,0],[48,74]],[[0,-4],[0,36]],[[-30,70],[30,70],[0,30],[-30,70]]];},"
"crown:function(){return[[[-64,44],[64,44],[64,20],[-64,20],[-64,44]],[[-64,20],[-40,-42],[-18,8],[0,-62],[18,8],[40,-42],[64,20]],ring(0,-62,9),ring(-40,-42,6),ring(40,-42,6)];},"
"rune:function(){return[ring(0,0,74),ring(0,0,30),[[0,-76],[22,-23],[72,-23],[32,9],[47,60],[0,28],[-47,60],[-32,9],[-72,-23],[-22,-23],[0,-76]]];}"
"}"
)

# ---- engine: part before A, then A, then part after A (references [能力造型库]) ----
ENGINE_PRE = r"""(function(img){var root=img.closest?img.closest('.mw-ability-start'):img.parentElement;if(!root)root=img.parentElement;if(!root||root.getAttribute('data-mw-ready')==='1')return;root.setAttribute('data-mw-ready','1');var cv=root.querySelector('.mw-canvas'),ctx=cv&&cv.getContext('2d');if(!ctx)return;var code=root.querySelector('.mw-code'),name=root.querySelector('.mw-name'),en=root.querySelector('.mw-en'),desc=root.querySelector('.mw-desc'),tags=root.querySelector('.mw-tags'),page=root.querySelector('.mw-page'),steps=root.querySelector('.mw-steps'),confirmBtn=root.querySelector('.mw-confirm');var C={w:'#fffdf8',s:'#e8e5ff',l:'#c9c1ff',v:'#8f82ff',c:'#9deaff',g:'#f6e6b6',d:'#70699c'};var PAL=[C.w,C.s,C.l,C.c,C.v,C.s,C.w,C.l,C.g];var A="""

ENGINE_POST = r""";function ring(cx,cy,r,a0){var p=[],s=46,i;for(i=0;i<=s;i++){var a=(a0||0)+i/s*6.2832;p.push([cx+Math.cos(a)*r,cy+Math.sin(a)*r]);}return p;}function arc(cx,cy,r,a0,a1,sg){var p=[],i;sg=sg||26;for(i=0;i<=sg;i++){var a=a0+(a1-a0)*i/sg;p.push([cx+Math.cos(a)*r,cy+Math.sin(a)*r]);}return p;}var G=[能力造型库];var N=760,P=[],AMB=[],i;function pad(n){return(n<10?'0':'')+n;}function sample(pls,n){var segs=[],total=0,p,i,a,b,L;for(p=0;p<pls.length;p++){var pl=pls[p];for(i=0;i<pl.length-1;i++){a=pl[i];b=pl[i+1];L=Math.sqrt((b[0]-a[0])*(b[0]-a[0])+(b[1]-a[1])*(b[1]-a[1]));if(L<1e-4)continue;segs.push([a[0],a[1],b[0],b[1],L]);total+=L;}}var out=[],acc=0,si=0,k;for(k=0;k<n;k++){var d=k/n*total;while(si<segs.length-1&&acc+segs[si][4]<d){acc+=segs[si][4];si++;}var s=segs[si],t=s?(d-acc)/s[4]:0;out.push(s?[s[0]+(s[2]-s[0])*t,s[1]+(s[3]-s[1])*t]:[0,0]);}return out;}for(i=0;i<N;i++)P.push({x:(Math.random()-.5)*440,y:(Math.random()-.5)*440,z:(Math.random()-.5)*240,tx:0,ty:0,tz:0,ph:Math.random()*6.2832,co:PAL[i%PAL.length]});for(i=0;i<120;i++)AMB.push({x:(Math.random()-.5)*540,y:(Math.random()-.5)*480,z:(Math.random()-.5)*320,ph:Math.random()*6.2832,co:Math.random()<.32?C.c:C.d});var idx=0,rx=-.1,ry=0,drag=0,lx=0,ly=0;function setGlyph(key){var fn=G[key]||G.rune,pt=sample(fn(),N),i;for(i=0;i<N;i++){var q=pt[i];P[i].tx=q[0];P[i].ty=q[1];P[i].tz=Math.sin(i*1.7)*9+(Math.random()-.5)*14;}}function render(){var m=A[idx],n=pad(idx+1),i;if(code)code.textContent='Archive '+n+' / Witch Ability';if(name)name.textContent=m[0];if(en)en.textContent=m[1];if(desc){var q=desc.querySelector('.mw-quote'),d=desc.querySelector('.mw-detail');if(q)q.textContent=m[2];if(d)d.textContent=m[3];}if(page)page.innerHTML='<strong>'+n+'</strong><i>/</i><span>'+pad(A.length)+'</span>';if(tags){tags.innerHTML='';var ts=m[6].split('/');for(i=0;i<ts.length;i++){var sp=document.createElement('span');sp.textContent=ts[i];tags.appendChild(sp);}}if(steps){steps.innerHTML='';for(i=0;i<A.length;i++){var st=document.createElement('i');st.className='mw-step'+(i===idx?' active':'');st.setAttribute('data-step',i);steps.appendChild(st);}}}function go(n){idx=(n+A.length)%A.length;setGlyph(A[idx][7]);render();}function choice(){var m=A[idx],L=String.fromCharCode(10);return '【开场魔女能力选择】'+L+'我选择「'+m[0]+' / '+m[1]+'」作为 user 的魔女能力。'+L+'能力定义：'+m[4]+L+'开场演出：'+m[5]+L+'关键词：'+m[6].replace(/\//g,'、');}function inp(doc){return doc.querySelector('.chat .chat-bottom .uni-textarea .chat-input-scope textarea')||doc.querySelector('.chatMsgTextarea textarea')||doc.querySelector('.chat .chat-bottom textarea')||doc.querySelector('.chat-input-scope textarea')||doc.querySelector('.uni-textarea textarea')||doc.querySelector('textarea:not(.ps-custom-input):not(#hu-custom-input)')||doc.querySelector('[contenteditable=true]')||doc.querySelector('textarea')||doc.querySelector('input[type=text]')||doc.querySelector('input:not([type])');}function send(){var el=inp(document),txt=choice(),L=String.fromCharCode(10);try{if(!el&&window.top&&window.top.document)el=inp(window.top.document);}catch(e){}if(!el){if(confirmBtn)confirmBtn.textContent='未找到输入框';return;}if(el.isContentEditable){var ov=el.textContent||'';el.textContent=ov&&ov.replace(/\s/g,'')?ov+L+L+txt:txt;}else{ov=el.value||'';el.value=ov&&ov.replace(/\s/g,'')?ov+L+L+txt:txt;}try{el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));el.focus();}catch(e2){}if(confirmBtn){confirmBtn.textContent='已追加';setTimeout(function(){confirmBtn.textContent='确定选择';},1100);}}function cls(n,c){while(n&&n!==root){if(n.classList&&n.classList.contains(c))return n;n=n.parentNode;}return n&&n.classList&&n.classList.contains(c)?n:null;}root.addEventListener('click',function(e){var st=cls(e.target,'mw-step');if(st){e.stopPropagation();go(parseInt(st.getAttribute('data-step'),10)||0);return;}if(cls(e.target,'mw-prev')){e.stopPropagation();go(idx-1);return;}if(cls(e.target,'mw-next')){e.stopPropagation();go(idx+1);return;}if(cls(e.target,'mw-confirm')){e.stopPropagation();send();}},true);function size(){var r=cv.getBoundingClientRect(),d=Math.max(1,Math.min(2,window.devicePixelRatio||1));cv.width=Math.max(260,Math.floor(r.width*d));cv.height=Math.max(260,Math.floor(r.height*d));}function draw(){requestAnimationFrame(draw);var w=cv.width,h=cv.height,dpr=Math.max(1,Math.min(2,window.devicePixelRatio||1)),T=performance.now();var yaw=ry+Math.sin(T*4e-4)*.17,pit=rx+Math.sin(T*3e-4)*.05,cyaw=Math.cos(yaw),syaw=Math.sin(yaw),cp=Math.cos(pit),sp=Math.sin(pit),sc=Math.min(w,h)/300;ctx.clearRect(0,0,w,h);ctx.globalCompositeOperation='lighter';var i,p,x1,z1,y1,z2,per,x,y;for(i=0;i<AMB.length;i++){p=AMB[i];x1=p.x*cyaw-p.z*syaw;z1=p.x*syaw+p.z*cyaw;y1=p.y*cp-z1*sp;z2=p.y*sp+z1*cp;per=560/(560+z2);x=w/2+x1*per*sc*.5;y=h/2+y1*per*sc*.5;ctx.globalAlpha=.14+.12*(Math.sin(T*.001+p.ph)*.5+.5);ctx.fillStyle=p.co;ctx.fillRect(x,y,dpr,dpr);}var e=.085;for(i=0;i<N;i++){p=P[i];p.x+=(p.tx-p.x)*e;p.y+=(p.ty-p.y)*e;p.z+=(p.tz-p.z)*e;var X=p.x+Math.sin(T*.0012+p.ph)*1.5,Y=p.y+Math.cos(T*.001+p.ph)*1.5,Z=p.z;x1=X*cyaw-Z*syaw;z1=X*syaw+Z*cyaw;y1=Y*cp-z1*sp;z2=Y*sp+z1*cp;per=560/(560+z2);x=w/2+x1*per*sc;y=h/2+y1*per*sc;var sz=Math.max(1,1.7*per*dpr*(.82+.32*Math.sin(T*.003+p.ph)));ctx.globalAlpha=Math.max(.22,Math.min(1,(z2+200)/360));ctx.fillStyle=p.co;ctx.fillRect(x,y,sz,sz);}ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;}function down(e){drag=1;var p=e.touches?e.touches[0]:e;lx=p.clientX;ly=p.clientY;if(e.preventDefault)e.preventDefault();}function move(e){if(!drag)return;var p=e.touches?e.touches[0]:e;ry+=(p.clientX-lx)*.006;rx+=(p.clientY-ly)*.006;if(rx>.9)rx=.9;if(rx<-.9)rx=-.9;lx=p.clientX;ly=p.clientY;}function up(){drag=0;}cv.addEventListener('mousedown',down);cv.addEventListener('touchstart',down);window.addEventListener('mousemove',move);window.addEventListener('touchmove',move);window.addEventListener('mouseup',up);window.addEventListener('touchend',up);window.addEventListener('resize',size);size();go(0);draw();try{img.parentNode.removeChild(img);}catch(e){}})(this);"""

engine = ENGINE_PRE + Ajs + ENGINE_POST

scripts = [
 skeleton,
 css,
 {"id": -1, "replaceString": engine, "scriptName": "JS", "findRegex": "[开场选择脚本]"},
 {"id": -1, "replaceString": GLYPH, "scriptName": "能力造型库", "findRegex": "[能力造型库]"},
]
out = {
 "pageDepth": orig.get("pageDepth", 2),
 "statusbar": orig.get("statusbar", ""),
 "beginning": orig.get("beginning", "[主骨架]"),
 "regex_scripts": scripts,
}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=None)

print("wrote", OUT)
for s in scripts:
    print("%-10s %6d chars  %s" % (s["scriptName"], len(s["replaceString"]),
          "OK" if len(s["replaceString"]) <= 20000 else "OVER 20000!"))
