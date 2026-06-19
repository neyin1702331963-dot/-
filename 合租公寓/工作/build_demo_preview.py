# -*- coding: utf-8 -*-
# 演示"预览功能"原理：把 MMD 正则链预跑一遍 → 独立 HTML（浏览器里 img onerror 真跑）
import json, os, re, html
OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")

# ── 1. 状态栏 CSS ──
CSS = ("<style>"
".sb{max-width:360px;margin:12px 0;background:linear-gradient(145deg,#1f2430,#161a23);"
"border:1px solid #3a4252;border-radius:12px;padding:14px;color:#e6e9ef;"
"font-family:system-ui,sans-serif;font-size:13px;line-height:1.6}"
".sb-t{color:#7aa2f7;font-weight:bold;margin-bottom:10px;letter-spacing:2px}"
".sb-row{display:flex;padding:3px 0}"
".sb-l{width:46px;color:#7c8499;flex-shrink:0}"
".sb-v{color:#e6e9ef}"
".sb-favwrap{display:flex;justify-content:space-between;margin-top:10px}"
".sb-favnum{color:#f7768e;font-weight:bold}"
".sb-bar{height:6px;background:#2a3040;border-radius:3px;overflow:hidden;margin-top:5px}"
".sb-fill{height:100%;background:linear-gradient(90deg,#f7768e,#ff9e64);border-radius:3px}"
".sb-tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}"
".sb-chip{background:#2a3040;border:1px solid #3a4252;border-radius:10px;padding:2px 9px;font-size:11px;color:#9aa5b8}"
"</style>")

# ── 2. 引擎（img onerror，纯 ES5，零双引号，星号用 /0.01 规避）──
ENGINE = (r'''<img src='x' style='display:none' onerror="(function(e){'''
r'''var b=e.closest('.content')||e.closest('.bubble')||e.parentNode;'''
r'''var reg=/\[([^=\[\]]+)=([^\[\]]+)\]/g;var d={},m;'''
r'''while((m=reg.exec(b.textContent))!==null){d[m[1].replace(/(^\s+)|(\s+$)/g,'')]=m[2].replace(/(^\s+)|(\s+$)/g,'')}'''
r'''var mk=function(c,t){var x=document.createElement('div');if(c)x.className=c;if(t)x.textContent=t;return x};'''
r'''var box=mk('sb','');box.appendChild(mk('sb-t','◆ 状态面板'));'''
r'''var row=function(l,v){if(!v)return;var r=mk('sb-row','');r.appendChild(mk('sb-l',l));r.appendChild(mk('sb-v',v));box.appendChild(r)};'''
r'''row('时间',d['时间']);row('地点',d['地点']);row('心情',d['心情']);'''
r'''var fav=d['好感'];if(fav){var fm=fav.match(/(\d+)\D+(\d+)/);if(fm){'''
r'''var w=mk('sb-favwrap','');w.appendChild(mk('sb-l','好感'));w.appendChild(mk('sb-favnum',fm[1]+'/'+fm[2]));box.appendChild(w);'''
r'''var bar=mk('sb-bar','');var fl=mk('sb-fill','');fl.style.width=Math.min(100,parseInt(fm[1])/parseInt(fm[2])/0.01)+'%';bar.appendChild(fl);box.appendChild(bar)}}'''
r'''if(d['标签']){var tg=mk('sb-tags','');var arr=d['标签'].split(/[,，]/);'''
r'''for(var i=0;i<arr.length;i++){var c=arr[i].replace(/(^\s+)|(\s+$)/g,'');if(c)tg.appendChild(mk('sb-chip',c))}box.appendChild(tg)}'''
r'''e.parentNode.insertBefore(box,e.nextSibling);e.remove()})(this)">''')

# ── 3. 样例：AI 输出的正文 + 数据块（MMD 里 AI 会吐这些）──
narrative = "她把拿铁推到你面前，杯壁的热气在窗玻璃上糊出一小片白。"
datablock = ("\n[时间=周六 下午 15:20]\n[地点=咖啡馆靠窗位]\n[心情=愉悦]"
             "\n[好感=68/100]\n[标签=放松,微醺,想聊天]")

# ── 模拟 MMD 信标转换器：把 [键=值] 包进隐藏 span（textContent 仍可读）──
beacons = re.sub(r"\[([^=\[\]]+)=([^\[\]]+)\]",
                 lambda x: '<span style="display:none">[%s=%s]</span>' % (x.group(1), x.group(2)),
                 datablock)

bubble = '<p>' + html.escape(narrative) + '</p>' + beacons.replace("\n", "") + ENGINE

# ── 预览 HTML（浏览器打开即所见即所得）──
page = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>状态栏预览</title>'
        + CSS +
        '<style>body{margin:0;background:#0d1117;font-family:system-ui;padding:18px;color:#c9d1d9}'
        '.note{max-width:420px;background:#161b22;border:1px solid #30363d;border-radius:10px;padding:12px;font-size:13px;line-height:1.7;margin-bottom:14px}'
        '.content{max-width:420px;background:#161b22;border:1px solid #30363d;border-radius:12px;padding:12px}</style>'
        '</head><body>'
        '<div class="note">这是<b>预览功能</b>的产物：MMD 正则链已预跑一遍。<br>'
        '下面这个气泡里：正文 + 隐藏数据 span + 引擎 img。<br>浏览器加载时 img onerror 触发 → 引擎读隐藏数据 → 拼出状态栏。</div>'
        '<div class="content">' + bubble + '</div>'
        '</body></html>')
p_html = os.path.join(OUT, "预览-状态栏demo.html")
open(p_html, "w", encoding="utf-8").write(page)

# ── 顺带产出对应的 MMD 导入 json（同一套东西，给 MMD 用）──
mmd = {
    "pageDepth": 2,
    "statusbar": "<demosbcss>",
    "beginning": narrative + datablock + "\n<demosb>",
    "regex_scripts": [
        {"id": -1, "scriptName": "demo样式", "findRegex": "<demosbcss>", "replaceString": CSS},
        {"id": -1, "scriptName": "数据信标转换器", "findRegex": r"/\[([^=\]]+)=([^\]]+)\]\s*/g",
         "replaceString": '<span style="display:none">[$1=$2]</span>'},
        {"id": -1, "scriptName": "demo引擎", "findRegex": "<demosb>", "replaceString": ENGINE},
    ],
}
p_json = os.path.join(OUT, "正则导入-状态栏demo.json")
json.dump(mmd, open(p_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.load(open(p_json, encoding="utf-8"))

inner = ENGINE.split('onerror="', 1)[1].rsplit('">', 1)[0]
print("已生成:", p_html)
print("        ", p_json)
print("引擎自检: onerror内双引号=%d 星号=%d | JSON OK" % (inner.count('"'), inner.count('*')))
