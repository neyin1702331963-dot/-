# -*- coding: utf-8 -*-
# 生成 <script> 载体版的本地预览（浏览器静态解析会执行内联 script）
import json, os, re, html

OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")
reg = json.load(open(os.path.join(OUT, "正则导入-script版.json"), encoding="utf-8"))
card = json.load(open(os.path.join(OUT, "角色卡.json"), encoding="utf-8"))

def rule(name):
    return [r for r in reg["regex_scripts"] if r["scriptName"] == name][0]["replaceString"]

CSS      = rule("响应式样式部署")
ENGINE   = rule("雷达引擎(script载体)")
BEAUTIFY = rule("全局美化激活")

fm = card["first_mes"]
narrative, _, datablock = fm.partition("<ztl>")
narr_html = "<font>" + html.escape(narrative).replace("\n", "<br>") + "</font>"
beacons = re.sub(r"\[([^=\[\]]+)=([^\[\]]+)\]",
                 lambda m: '<span style="display:none">[%s=%s]</span>' % (m.group(1), m.group(2)),
                 datablock)
bubble_inner = narr_html + "\n" + beacons + "\n" + ENGINE

page = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>合租公寓 · 状态栏预览（script载体）</title>
<style>body{margin:0;background:#fbf3e9;font-family:system-ui,sans-serif;}
.preview-note{max-width:640px;margin:12px auto;padding:10px 14px;background:#fff8f0;border:1px solid #e6c9a8;border-radius:10px;color:#7a6450;font-size:13px;line-height:1.6;}
.chat{max-width:640px;margin:0 auto;padding:8px 12px 80px;}</style>
%(CSS)s
%(BEAUTIFY)s
</head>
<body class="z-enabled">
<div class="preview-note"><b>&lt;script&gt; 载体版预览</b>：状态栏引擎改用 &lt;script&gt; 执行（当前 MMD 已开放）。<br>浏览器里内联 script 会正常执行；但 MMD 是否执行取决于它把消息 HTML 注入 DOM 的方式（见聊天里我的说明）。</div>
<div class="chat"><div class="chat-bg"></div><div class="chat-scope-box"><div class="scroll-view"><div class="chat-body">
<div class="item"><div class="touch-scope"><div class="content left">
%(BUBBLE)s
</div></div></div>
</div></div></div></div>
<div class="chat-bottom"><div class="uni-textarea"><div class="chat-input-scope"><textarea class="uni-textarea-textarea"></textarea></div></div></div>
</body></html>
""" % {"CSS": CSS, "BEAUTIFY": BEAUTIFY, "BUBBLE": bubble_inner}

path = os.path.join(OUT, "预览-script版.html")
open(path, "w", encoding="utf-8").write(page)
print("已生成:", path, "(%d bytes)" % os.path.getsize(path))
