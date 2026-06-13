# -*- coding: utf-8 -*-
# 生成本地预览 HTML：把 MMD 正则链对开场白跑一遍，浏览器打开即所见即所得
import json, os, re, html

OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")
reg = json.load(open(os.path.join(OUT, "正则导入.json"), encoding="utf-8"))
card = json.load(open(os.path.join(OUT, "角色卡.json"), encoding="utf-8"))

def rule(name):
    return [r for r in reg["regex_scripts"] if r["scriptName"] == name][0]["replaceString"]

CSS      = rule("响应式样式部署")   # <style> 状态栏样式
ENGINE   = rule("雷达引擎")         # <ztl> -> img 引擎
BEAUTIFY = rule("全局美化激活")     # <beautify> -> 激活img + 主题style

# 取开场白，拆成 叙事 + <ztl>数据块
fm = card["first_mes"]
narrative, _, datablock = fm.partition("<ztl>")

# 叙事换行转 <br>，包进 font（模拟 MMD 气泡）
narr_html = "<font>" + html.escape(narrative).replace("\n", "<br>") + "</font>"

# 信标转换：每个 [k=v] -> 隐藏 span（引擎靠 textContent 读取）
def beacon(m):
    return '<span style="display:none">[%s=%s]</span>' % (m.group(1), m.group(2))
beacons = re.sub(r"\[([^=\[\]]+)=([^\[\]]+)\]", beacon, datablock)

# <ztl> -> 引擎 img（必须在 .content 内部）
bubble_inner = narr_html + "\n" + beacons + "\n" + ENGINE

page = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>合租公寓 · 状态栏预览</title>
<style>body{margin:0;background:#fbf3e9;font-family:system-ui,sans-serif;}
.preview-note{max-width:640px;margin:12px auto;padding:10px 14px;background:#fff8f0;border:1px solid #e6c9a8;border-radius:10px;color:#7a6450;font-size:13px;line-height:1.6;}
.chat{max-width:640px;margin:0 auto;padding:8px 12px 80px;}</style>
%(CSS)s
%(BEAUTIFY)s
</head>
<body class="z-enabled">
<div class="preview-note">本地预览：模拟旧版 MMD 正则链渲染效果（暖调主题 + 雷达法状态栏）。<br>选项可点（预览页无输入框，点击不回填属正常）；实际效果以 MMD 实机为准。</div>
<div class="chat"><div class="chat-bg"></div><div class="chat-scope-box"><div class="scroll-view"><div class="chat-body">
<div class="item"><div class="touch-scope"><div class="content left">
%(BUBBLE)s
</div></div></div>
</div></div></div></div>
<div class="chat-bottom"><div class="uni-textarea"><div class="chat-input-scope"><textarea class="uni-textarea-textarea"></textarea></div></div></div>
</body></html>
""" % {"CSS": CSS, "BEAUTIFY": BEAUTIFY, "BUBBLE": bubble_inner}

path = os.path.join(OUT, "预览.html")
open(path, "w", encoding="utf-8").write(page)
print("已生成:", path, "(%d bytes)" % os.path.getsize(path))
print("解析出的选项数（预览应显示）:", len(re.findall(r"\[选项=", datablock)))
