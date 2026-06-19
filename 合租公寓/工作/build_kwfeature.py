# -*- coding: utf-8 -*-
# 小功能：输入框打字 → 检测关键词 → 底部弹「检测到「xxx」，是否加载相关内容？[加载][忽略]」
# 载体 img onerror（唯一可靠）；监听全局 textarea 的 input；按钮用 el.onclick JS 赋值（净化下可用）
# 全 ES5 + 零双引号 + 防重复绑定 + 忽略后移除关键词可再次提示
import json, os
OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")

# 关键词 → 点「加载」时插入输入框的内容（用全角【】避免和 [键=值] 信标正则冲突）
ENGINE = (
"<img src='x' style='display:none' onerror=\"(function(e){"
"var KW={'林夏':'【和林夏在客厅闲聊】','顾沉':'【深夜厨房遇到顾沉】','沈知意':'【阳台找刚下夜班的沈知意】','烧烤':'【三人去楼下吃烧烤】'};"
"var getInput=function(){return document.querySelector('.uni-textarea-textarea')||document.querySelector('textarea')};"
"var setup=function(){"
"var ta=getInput();if(!ta)return false;if(ta.__kwBound)return true;ta.__kwBound=true;"
"window.__kwDismissed=window.__kwDismissed||{};var banner=null;"
"var closeBanner=function(){if(banner&&banner.parentNode)banner.parentNode.removeChild(banner);banner=null};"
"var showBanner=function(kw){closeBanner();"
"banner=document.createElement('div');"
"banner.style.cssText='position:fixed;left:50%;bottom:72px;transform:translateX(-50%);z-index:99999;background:#fffaf3;border:1px solid #d99a5e;border-radius:12px;padding:10px 12px;box-shadow:0 4px 16px rgba(150,110,70,.3);display:flex;align-items:center;gap:10px;font-size:13px;color:#5a4636;max-width:92%';"
"banner.onclick=function(ev){ev.stopPropagation()};"
"var t=document.createElement('span');t.textContent='💡 检测到「'+kw+'」，是否加载相关内容？';banner.appendChild(t);"
"var load=document.createElement('button');load.textContent='加载';"
"load.style.cssText='border:none;background:#c8794f;color:#fff;border-radius:8px;padding:6px 12px;font-size:13px';"
"load.onclick=function(ev){ev.stopPropagation();ta.value=ta.value+' '+KW[kw];ta.dispatchEvent(new Event('input',{bubbles:true}));window.__kwDismissed[kw]=true;closeBanner()};"
"banner.appendChild(load);"
"var ig=document.createElement('button');ig.textContent='忽略';"
"ig.style.cssText='border:1px solid #e6c9a8;background:transparent;color:#a98e6f;border-radius:8px;padding:6px 10px;font-size:13px';"
"ig.onclick=function(ev){ev.stopPropagation();window.__kwDismissed[kw]=true;closeBanner()};"
"banner.appendChild(ig);document.body.appendChild(banner)};"
"var onInput=function(){var v=ta.value||'';"
"for(var dk in window.__kwDismissed){if(v.indexOf(dk)===-1)delete window.__kwDismissed[dk]}"
"var hit=null;for(var k in KW){if(v.indexOf(k)!==-1&&!window.__kwDismissed[k]){hit=k;break}}"
"if(hit)showBanner(hit);else closeBanner()};"
"ta.addEventListener('input',onInput);return true};"
"if(!setup()){var n=0;var iv=setInterval(function(){if(setup()||++n>20)clearInterval(iv)},300)}"
"e.remove()})(this)\">"
)

mmd = {
    "pageDepth": 2,
    "statusbar": "",
    "beginning": ("关键词检测·加载提示 已启用。\n"
                  "在下方输入框打字试试：输入「林夏 / 顾沉 / 沈知意 / 烧烤」任一词，\n"
                  "底部会弹出「检测到「xxx」，是否加载相关内容？」——点【加载】把相关内容填进输入框，点【忽略】关闭。\n"
                  "<kwload>"),
    "regex_scripts": [
        {"id": -1, "scriptName": "关键词检测加载", "findRegex": "<kwload>", "replaceString": ENGINE},
    ],
}
path = os.path.join(OUT, "正则导入-关键词加载.json")
json.dump(mmd, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.load(open(path, encoding="utf-8"))
inner = ENGINE.split('onerror="', 1)[1].rsplit('">', 1)[0]
print("已生成:", path)
print("引擎字符数:", len(ENGINE), "| onerror 内双引号:", inner.count('"'), "| 箭头:", inner.count('=>'), "(应0,纯ES5) | JSON OK")

# 本地预览：带一个假输入框
page = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>关键词加载预览</title>'
        '<style>body{margin:0;background:#fbf3e9;font-family:system-ui,sans-serif}.wrap{max-width:600px;margin:0 auto;padding:16px 16px 120px}'
        '.note{background:#fff8f0;border:1px solid #e6c9a8;border-radius:10px;padding:10px 14px;color:#7a6450;font-size:13px;line-height:1.7}'
        '.bar{position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:1px solid #eee;padding:12px;display:flex;gap:8px}'
        '.bar textarea{flex:1;height:40px;border:1px solid #ccc;border-radius:10px;padding:8px;font-size:14px;resize:none}</style>'
        '</head><body><div class="wrap"><div class="note"><b>关键词检测·加载提示 · 预览</b><br>'
        '在下面输入框打字：输入「林夏 / 顾沉 / 沈知意 / 烧烤」任一词 → 底部弹提示。点【加载】内容填进输入框；【忽略】关闭；删掉词再打可再次弹。</div>'
        + ENGINE +
        '</div><div class="bar"><textarea class="uni-textarea-textarea" placeholder="在这里打字，试试输入 林夏"></textarea></div>'
        '</body></html>')
open(os.path.join(OUT, "预览-关键词加载.html"), "w", encoding="utf-8").write(page)
print("已生成 预览-关键词加载.html")
