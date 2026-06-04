(function(img){
var root=img.closest?img.closest('.mw-ability-start'):img.parentElement;
if(!root)root=img.parentElement;
if(!root||root.getAttribute('data-mw-ready')==='1')return;
root.setAttribute('data-mw-ready','1');
var cv=root.querySelector('.mw-canvas'),ctx=cv&&cv.getContext('2d');
if(!ctx)return;
var code=root.querySelector('.mw-code'),name=root.querySelector('.mw-name'),en=root.querySelector('.mw-en'),desc=root.querySelector('.mw-desc'),tags=root.querySelector('.mw-tags'),page=root.querySelector('.mw-page'),steps=root.querySelector('.mw-steps'),confirmBtn=root.querySelector('.mw-confirm');
var C={w:'#fffdf8',s:'#e8e5ff',l:'#c9c1ff',v:'#8f82ff',c:'#9deaff',g:'#f6e6b6',d:'#70699c'},Q=2.2;

/* 3 个能力模板。最后一个字段是造型 key，对应一个正面线描图标。 */
var A=[
 ['星门启录','Astral Keygate','门不是入口，是被星光承认的许可。','在短时间内开启一枚只允许 user 通过的星门，可越过封锁、距离或一次失败判定。','指定一个可视或已知坐标，开启短距星门并重置一次进入条件。','开场时银白钥孔在空中展开，十三枚星钉依次点亮通行许可。','星门/钥孔/通行','key'],
 ['晶钟裁时','Crystal Chronometer','时间不是河流，是可以被裁开的晶面。','召唤晶钟结构，将一个动作拆成预备、发生、余波三个切面。','选择其中一个切面延迟或提前，使行动节奏被 user 重新排序。','开场时六角晶钟悬在胸前，指针划过透明的时间切片。','晶钟/裁时/节奏','clock'],
 ['假面授冠','Crowned Mask','戴上王冠之前，先选择要扮演的奇迹。','召唤三枚假面，让 user 临时获得一种演出身份：守护者、欺诈者或处刑者。','选择一种身份获得对应强化，但身份会限制本回合的行动风格。','开场时白银假面围绕王冠旋转，最终有一枚落到 user 面前。','假面/王冠/身份','crown']
];

function pad(n){return(n<10?'0':'')+n}
/* 确定性 hash 噪声：同样的 (i,s) 永远得到同一值，避免抖动闪烁 */
function R(i,s){var v=Math.sin(i*12.9898+s*78.233)*43758.5453;return v-Math.floor(v)}

/* ===== 正面线描图元：全部往目标数组 T 里推点，z 只给一点微厚度 ===== */
var TH=7;
function pt(T,x,y,c,s,z){T.push({x:x,y:y,z:(z==null?(R(T.length,3)-.5)*TH:z),c:c||C.s,s:s||1})}
function seg(T,x1,y1,x2,y2,n,w,c,s,sd){n=Math.max(2,n*Q|0);for(var i=0;i<n;i++){var t=i/(n-1);pt(T,x1+(x2-x1)*t+(R(i,sd)-.5)*(w||0),y1+(y2-y1)*t+(R(i,sd+1)-.5)*(w||0),c,s)}}
function arc(T,cx,cy,rx,ry,a,b,n,w,c,s,sd){n=Math.max(2,n*Q|0);for(var i=0;i<n;i++){var t=a+(b-a)*i/(n-1),o=(R(i,sd)-.5)*(w||0);pt(T,cx+Math.cos(t)*(rx+o),cy+Math.sin(t)*(ry+o),c,s)}}
function ring(T,cx,cy,r,n,w,c,s,sd){arc(T,cx,cy,r,r,0,6.283,n,w,c,s,sd)}
function poly(T,ps,n,w,c,s){for(var i=0;i<ps.length;i++){var p=ps[i],q=ps[(i+1)%ps.length];seg(T,p[0],p[1],q[0],q[1],n,w,c,s,30+i*7)}}
function star(T,x,y,r,c){poly(T,[[x,y-r],[x+r*.5,y-r*.1],[x+r*.22,y+r*.34],[x-r*.22,y+r*.34],[x-r*.5,y-r*.1]],14,1.3,c,1);pt(T,x,y,C.w,2)}
function dot(T,x,y,r,c){ring(T,x,y,r,28,1.2,c,1,77);pt(T,x,y,C.w,1.6)}

/* ===== 造型库：每个能力一个正面可识别图标 ===== */
function bKey(T){           /* 星门启录 → 钥匙 / 钥孔 */
 ring(T,0,-90,48,150,2,C.g,1.1,10); ring(T,0,-90,30,90,1.6,C.l,.7,20);
 star(T,0,-90,16,C.w);
 seg(T,0,-42,0,118,150,2,C.w,1.1,40);
 seg(T,0,92,36,92,40,1.4,C.c,1,50); seg(T,36,92,36,72,26,1.4,C.c,1,55);
 seg(T,0,112,30,112,34,1.4,C.c,1,60); seg(T,30,112,30,94,24,1.4,C.c,1,65);
}
function bClock(T){         /* 晶钟裁时 → 六角晶钟 + 指针 */
 var hx=[],k;for(k=0;k<6;k++){var a=-1.5708+k*1.0472;hx.push([Math.cos(a)*128,Math.sin(a)*128])}
 poly(T,hx,52,2,C.l,.7);
 ring(T,0,0,106,170,2,C.c,1,80);
 for(var i=0;i<12;i++){var t=i*0.5236,r2=(i%3===0)?76:88;seg(T,Math.cos(t)*96,Math.sin(t)*96,Math.cos(t)*r2,Math.sin(t)*r2,12,1,C.s,.9,90+i)}
 seg(T,0,0,0,-58,58,1.6,C.w,1.1,140);
 seg(T,0,0,66,28,62,1.6,C.g,1.1,150);
 dot(T,0,0,9,C.w);
}
function bCrown(T){         /* 假面授冠 → 王冠 */
 var pk=[[-122,-84],[-72,8],[-36,-48],[0,-94],[36,-48],[72,8],[122,-84]],i;
 for(i=0;i<pk.length-1;i++)seg(T,pk[i][0],pk[i][1],pk[i+1][0],pk[i+1][1],46,2,C.g,1.1,200+i);
 seg(T,-122,-84,-122,70,40,1.6,C.l,.9,220);
 seg(T,122,-84,122,70,40,1.6,C.l,.9,225);
 seg(T,-122,70,122,70,120,2,C.w,1.1,230);
 seg(T,-122,40,122,40,120,1.4,C.c,.8,235);
 dot(T,-122,-84,10,C.c); dot(T,0,-94,13,C.w); dot(T,122,-84,10,C.c);
 dot(T,-36,-48,8,C.g); dot(T,36,-48,8,C.g);
 for(var j=-2;j<=2;j++)star(T,j*44,55,9,j===0?C.g:C.s);
}
var SHAPES={key:bKey,clock:bClock,crown:bCrown};

/* 背景星尘：跨能力固定不变，只让前景图标形变 */
var BG=[];(function(){for(var i=0;i<260;i++){var a=R(i,900)*6.283,r=152+R(i,901)*150;BG.push({x:Math.cos(a)*r,y:(R(i,902)-.5)*330,z:(R(i,903)-.5)*180,c:i%5?C.d:C.c,s:.5})}})();

/* 把任意点数归一到固定 ICON，方便每帧一一对应做补间 */
var ICON=820;
function build(key){var T=[];(SHAPES[key]||bKey)(T);
 if(T.length>ICON){var out=[],step=T.length/ICON,i;for(i=0;i<ICON;i++)out.push(T[Math.floor(i*step)]);T=out;}
 else{var n0=T.length||1,i=0;while(T.length<ICON){var b=T[i%n0];T.push({x:b.x+(R(T.length,5)-.5)*4,y:b.y+(R(T.length,6)-.5)*4,z:(R(T.length,7)-.5)*TH,c:b.c,s:b.s});i++}}
 return T;
}

/* ===== 粒子池：前 ICON 个做图标(会形变)，其后是静态背景星尘 ===== */
var P=[],i;
for(i=0;i<ICON;i++)P.push({x:0,y:0,z:0,sx:0,sy:0,sz:0,tx:0,ty:0,tz:0,c:C.s,s:1});
for(i=0;i<BG.length;i++){var b=BG[i];P.push({x:b.x,y:b.y,z:b.z,sx:b.x,sy:b.y,sz:b.z,tx:b.x,ty:b.y,tz:b.z,c:b.c,s:b.s,bg:1})}

var idx=0,mStart=-1e9,mDur=640;
function ease(t){return t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2}
function setTarget(key){var T=build(key),i;for(i=0;i<ICON;i++){var p=P[i],t=T[i];p.sx=p.x;p.sy=p.y;p.sz=p.z;p.tx=t.x;p.ty=t.y;p.tz=t.z;p.c=t.c;p.s=t.s}mStart=performance.now()}

/* ===== 文案渲染 ===== */
function render(){var m=A[idx],n=pad(idx+1);
 if(code)code.textContent='Archive '+n+' / Witch Ability';
 if(name)name.textContent=m[0];
 if(en)en.textContent=m[1];
 if(desc){var q=desc.querySelector('.mw-quote'),d=desc.querySelector('.mw-detail');if(q)q.textContent=m[2];if(d)d.textContent=m[3]}
 if(page)page.innerHTML='<strong>'+n+'</strong><i>/</i><span>'+pad(A.length)+'</span>';
 if(tags){tags.innerHTML='';var ts=m[6].split('/'),i;for(i=0;i<ts.length;i++){var spn=document.createElement('span');spn.textContent=ts[i];tags.appendChild(spn)}}
 if(steps){steps.innerHTML='';for(i=0;i<A.length;i++){var st=document.createElement('i');st.className='mw-step'+(i===idx?' active':'');st.setAttribute('data-step',i);steps.appendChild(st)}}}
function go(n){idx=(n+A.length)%A.length;setTarget(A[idx][7]);render()}

/* ===== SillyTavern 输入框对接 ===== */
function choice(){var m=A[idx];return '【开场魔女能力选择】'+String.fromCharCode(10)+'我选择「'+m[0]+' / '+m[1]+'」作为 user 的魔女能力。'+String.fromCharCode(10)+'能力定义：'+m[4]+String.fromCharCode(10)+'开场演出：'+m[5]+String.fromCharCode(10)+'关键词：'+m[6].replace(/\//g,'、')}
function inp(doc){return doc.querySelector('.chat .chat-bottom .uni-textarea .chat-input-scope textarea')||doc.querySelector('.chatMsgTextarea textarea')||doc.querySelector('.chat .chat-bottom textarea')||doc.querySelector('.chat-input-scope textarea')||doc.querySelector('.uni-textarea textarea')||doc.querySelector('textarea:not(.ps-custom-input):not(#hu-custom-input)')||doc.querySelector('[contenteditable=true]')||doc.querySelector('textarea')||doc.querySelector('input[type=text]')||doc.querySelector('input:not([type])')}
function send(){var el=inp(document),txt=choice();try{if(!el&&window.top&&window.top.document)el=inp(window.top.document)}catch(e){}if(!el){if(confirmBtn)confirmBtn.textContent='未找到输入框';return}if(el.isContentEditable){var ov=el.textContent||'';el.textContent=ov&&ov.replace(/\s/g,'')?ov+String.fromCharCode(10)+String.fromCharCode(10)+txt:txt}else{ov=el.value||'';el.value=ov&&ov.replace(/\s/g,'')?ov+String.fromCharCode(10)+String.fromCharCode(10)+txt:txt}try{el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));el.focus()}catch(e2){}if(confirmBtn){confirmBtn.textContent='已追加';setTimeout(function(){confirmBtn.textContent='确定选择'},1100)}}

function cls(n,c){while(n&&n!==root){if(n.classList&&n.classList.contains(c))return n;n=n.parentNode}return n&&n.classList&&n.classList.contains(c)?n:null}
root.addEventListener('click',function(e){var st=cls(e.target,'mw-step');if(st){e.stopPropagation();go(parseInt(st.getAttribute('data-step'),10)||0);return}if(cls(e.target,'mw-prev')){e.stopPropagation();go(idx-1);return}if(cls(e.target,'mw-next')){e.stopPropagation();go(idx+1);return}if(cls(e.target,'mw-confirm')){e.stopPropagation();send()}},true);

/* ===== 渲染：正面朝向 + 轻微摇摆 + 上下浮动 + 形变补间 ===== */
var rx=0,ry=0,drag=0,lx=0,ly=0,dvx=0,dvy=0;
function size(){var r=cv.getBoundingClientRect(),d=Math.max(1,Math.min(2,window.devicePixelRatio||1));cv.width=Math.max(260,Math.floor(r.width*d));cv.height=Math.max(260,Math.floor(r.height*d))}
function draw(){requestAnimationFrame(draw);
 var w=cv.width,h=cv.height,d=Math.max(1,Math.min(2,window.devicePixelRatio||1)),now=performance.now();
 var mp=mStart<-1e8?1:Math.min(1,(now-mStart)/mDur),e=ease(mp),i;
 for(i=0;i<ICON;i++){var p=P[i];p.x=p.sx+(p.tx-p.sx)*e;p.y=p.sy+(p.ty-p.sy)*e;p.z=p.sz+(p.tz-p.sz)*e}
 var t=now*.001;if(!drag){rx+=dvx;ry+=dvy;dvx*=.9;dvy*=.9;rx*=.95;ry*=.95}
 var ay=ry+Math.sin(t*.6)*.14,ax=rx+Math.cos(t*.8)*.06,bob=Math.sin(t*.9)*8;
 var cy=Math.cos(ay),sy=Math.sin(ay),cx=Math.cos(ax),sx=Math.sin(ax),sc=Math.min(w,h)/430;
 ctx.clearRect(0,0,w,h);ctx.globalCompositeOperation='lighter';
 for(i=0;i<P.length;i++){var q=P[i],x1=q.x*cy-q.z*sy,z1=q.x*sy+q.z*cy,y1=q.y*cx-z1*sx,z2=q.y*sx+z1*cx,per=560/(560+z2),X=w/2+x1*per*sc,Y=h/2+(y1+bob)*per*sc,ps=Math.max(1,(q.s||1)*per*d);
  ctx.globalAlpha=q.bg?Math.max(.1,Math.min(.5,(z2+260)/620)):Math.max(.32,Math.min(1,(z2+260)/520));
  ctx.fillStyle=q.c;ctx.fillRect(X,Y,ps,ps)}
 ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1}

function down(e){drag=1;var p=e.touches?e.touches[0]:e;lx=p.clientX;ly=p.clientY;if(e.preventDefault)e.preventDefault()}
function move(e){if(!drag)return;var p=e.touches?e.touches[0]:e;dvy=(p.clientX-lx)*.004;dvx=(p.clientY-ly)*.004;ry+=dvy;rx+=dvx;rx=Math.max(-.55,Math.min(.55,rx));ry=Math.max(-.7,Math.min(.7,ry));lx=p.clientX;ly=p.clientY}
function up(){drag=0}
cv.addEventListener('mousedown',down);cv.addEventListener('touchstart',down);window.addEventListener('mousemove',move);window.addEventListener('touchmove',move);window.addEventListener('mouseup',up);window.addEventListener('touchend',up);window.addEventListener('resize',size);
size();go(0);
/* 开场首帧不要补间，直接落到图标 */
for(i=0;i<ICON;i++){P[i].x=P[i].tx;P[i].y=P[i].ty;P[i].z=P[i].tz}
draw();
try{img.parentNode.removeChild(img)}catch(e){}
})(this);
