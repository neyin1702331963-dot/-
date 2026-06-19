# -*- coding: utf-8 -*-
# 测试：① <script> 直接写进开场白(非正则注入)执不执行  ② 平台是否内置 window.ButtonListenModule
# 基准 D(正则注入img,必出) + A(直接script) + B(直接img) + E(查ButtonListenModule,正则img可靠)
import json, os
OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")
ST = "margin:6px;padding:8px;border-radius:6px;font-size:13px"

def imgbox(label, color="#e6f7e6", fg="#1a7f1a"):
    return ("<img src='x' style='display:none' onerror=\"(function(e){"
            "var d=document.createElement('div');d.style.cssText='" + ST + ";background:" + color + ";color:" + fg + "';"
            "d.textContent='" + label + "';e.parentNode.insertBefore(d,e.nextSibling)})(this)\">")

# A：<script> 直接写进开场白
A = ("<div id='dsa'></div>"
     "<script>(function(){try{var a=document.getElementById('dsa')||document.body;"
     "var d=document.createElement('div');d.style.cssText='" + ST + ";background:#e6f7e6;color:#1a7f1a';"
     "d.textContent='✓ A 直接写入开场白的 <script> 执行了';a.appendChild(d);}catch(err){}})();</script>")

# B：img onerror 直接写进开场白（非正则注入）
B = imgbox("✓ B 直接写入开场白的 img onerror 执行了")

beginning = (
    "测试：① <script> 直接写进开场白执不执行 ② 平台是否内置 ButtonListenModule。\n"
    "看出现哪些框：\n"
    "• D(必出) = 消息已渲染、正则注入基准\n"
    "• A 绿 = 直接写入的 <script> 会执行；没 A = 不执行\n"
    "• B 绿 = 直接写入的 img onerror 会执行；没 B = 直接 HTML 也被吃掉\n"
    "• E 绿 = 平台内置了 window.ButtonListenModule；E 橙 = 没内置\n\n"
    + "<ctrlbase>"   # → D
    + A
    + B
    + "<blmcheck>"   # → E
)

# E：用正则注入的可靠 img 查 window.ButtonListenModule 是否存在
E = ("<img src='x' style='display:none' onerror=\"(function(e){"
     "var has=(typeof window.ButtonListenModule!=='undefined');"
     "var d=document.createElement('div');d.style.cssText='" + ST + "';"
     "d.style.background=has?'#e6f7e6':'#fde2c8';d.style.color=has?'#1a7f1a':'#a05a00';"
     "d.textContent=has?'✓ E 平台已内置 window.ButtonListenModule':'△ E 平台没内置 ButtonListenModule（须自行加载）';"
     "e.parentNode.insertBefore(d,e.nextSibling)})(this)\">")

mmd = {
    "pageDepth": 2, "statusbar": "", "beginning": beginning,
    "regex_scripts": [
        {"id": -1, "scriptName": "基准D", "findRegex": "<ctrlbase>", "replaceString": imgbox("✓ D 正则注入 img onerror（基准，必出）")},
        {"id": -1, "scriptName": "BLM检查E", "findRegex": "<blmcheck>", "replaceString": E},
    ],
}
path = os.path.join(OUT, "正则导入-script直写测试.json")
json.dump(mmd, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.load(open(path, encoding="utf-8"))
print("已生成:", path, "| JSON OK")
