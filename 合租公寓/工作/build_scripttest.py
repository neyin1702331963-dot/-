# -*- coding: utf-8 -*-
# 终极判定探针：<script> 到底执行不执行？currentScript 到底有没有？
# 一条正则同时放：S1 <script>(查 currentScript) + S2 img onerror(对照)
import json, os
OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")

ST = "margin:6px;padding:8px;border-radius:6px;font-size:13px"

# S1：<script> 自检——它执行了吗？document.currentScript 拿得到吗？
S1 = ("<div id='s1anchor'></div>"
      "<script>(function(){"
      "var s=document.currentScript;"
      "var a=document.getElementById('s1anchor');"
      "var d=document.createElement('div');d.style.cssText='" + ST + "';"
      "if(s){d.style.background='#e6f7e6';d.style.color='#1a7f1a';"
      "d.textContent='✓ S1 <script> 执行了，且 document.currentScript 可用（能自定位→自渲染引擎理论可行）';}"
      "else{d.style.background='#fde2c8';d.style.color='#a05a00';"
      "d.textContent='△ S1 <script> 执行了，但 document.currentScript=null（无法自定位→做不了per-message自渲染）';}"
      "(a||document.body).appendChild(d);"
      "})();</script>")

# S2：img onerror 对照——确认本条消息已渲染、载体正常（必出绿）
S2 = ("<img src='x' style='display:none' onerror=\"(function(e){"
      "var d=document.createElement('div');d.style.cssText='" + ST + ";background:#e6f7e6;color:#1a7f1a';"
      "d.textContent='✓ S2 对照 img onerror 可用（本消息已渲染）';"
      "e.parentNode.insertBefore(d,e.nextSibling)})(this)\">")

probes = S1 + "\n" + S2

mmd = {
    "pageDepth": 2, "statusbar": "",
    "beginning": ("script 终极判定探针。看出现哪些框：\n"
                  "• 只有 S2(绿)、没有 S1 → <script> 在消息里根本不执行\n"
                  "• S1 绿 → script 执行且 currentScript 可用（自渲染引擎可行，我之前的结论要修正）\n"
                  "• S1 橙 → script 执行但 currentScript=null（做不了自渲染，须 img onerror）\n"
                  "<scripttest>"),
    "regex_scripts": [{"id": -1, "scriptName": "script判定", "findRegex": "<scripttest>", "replaceString": probes}],
}
path = os.path.join(OUT, "正则导入-script判定.json")
json.dump(mmd, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.load(open(path, encoding="utf-8"))
print("已生成:", path, "| 字符数:", len(probes), "| JSON OK")
