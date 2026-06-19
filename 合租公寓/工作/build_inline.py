# -*- coding: utf-8 -*-
# 内联事件能力探针：测 DOM 属性里的 JS 能不能 多行 / 用双引号 / 复杂onclick
# 出绿框=可用；按钮消失=被手术式切除；不出框=被截断
import json, os

OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")

# A：单行 onerror（基准，必出）
A = ("<img src='x' style='display:none' onerror=\""
     "(function(e){var d=document.createElement('div');"
     "d.style.margin='6px';d.style.padding='8px';d.style.borderRadius='6px';d.style.fontSize='13px';"
     "d.style.background='#e6f7e6';d.style.color='#1a7f1a';"
     "d.textContent='✓ A 单行 onerror 可用（基准）';"
     "e.parentNode.insertBefore(d,e.nextSibling)})(this)\">")

# B：多行 onerror（属性值里有真实换行）
B = ("<img src='x' style='display:none' onerror=\"\n"
     "(function(e){\n"
     "  var d=document.createElement('div');\n"
     "  d.style.margin='6px';d.style.padding='8px';d.style.borderRadius='6px';d.style.fontSize='13px';\n"
     "  d.style.background='#e6f7e6';d.style.color='#1a7f1a';\n"
     "  d.textContent='✓ B 多行 onerror 可用（属性里带换行）';\n"
     "  e.parentNode.insertBefore(d,e.nextSibling);\n"
     "})(this)\n"
     "\">")

# C：多行 onclick 按钮 + try-catch（旧版会被手术式切除）
C = ("<button type='button' style='margin:6px;padding:8px 14px;border-radius:6px;border:1px solid #c8794f;background:#fff8f0;color:#5a4636' onclick=\"\n"
     "var d=this.nextElementSibling;\n"
     "try{\n"
     "  var x=1+2;\n"
     "  d.textContent='✓ C 多行 onclick(含try-catch) 可用 结果='+x;\n"
     "  d.style.color='#1a7f1a';\n"
     "}catch(err){\n"
     "  d.textContent='✗ C 报错 '+err;\n"
     "}\n"
     "\">点我测多行 onclick</button>"
     "<div style='margin:6px;padding:8px;font-size:13px;color:#856404'>C：点上面的按钮看结果（按钮若消失=被切除）</div>")

# D：单引号属性 + 内部用双引号（测能不能放心用双引号）
D = ("<img src='x' style='display:none' onerror='"
     "(function(e){var d=document.createElement(\"div\");"
     "d.style.margin=\"6px\";d.style.padding=\"8px\";d.style.borderRadius=\"6px\";d.style.fontSize=\"13px\";"
     "d.style.background=\"#e6f7e6\";d.style.color=\"#1a7f1a\";"
     "d.textContent=\"✓ D 单引号属性内用双引号 可用\";"
     "e.parentNode.insertBefore(d,e.nextSibling)})(this)'>")

probes = A + "\n" + B + "\n" + C + "\n" + D

mmd = {
    "pageDepth": 2,
    "statusbar": "",
    "beginning": ("内联事件探针：测 DOM 属性里的 JS 能否 多行 / 双引号 / 复杂onclick。\n"
                  "应出现 A/B/D 三个绿框 + C 一个按钮（点它出结果）。哪个缺失=该写法被限制。\n"
                  "<inlineprobe>"),
    "regex_scripts": [
        {"id": -1, "scriptName": "内联探针", "findRegex": "<inlineprobe>", "replaceString": probes},
    ],
}

path = os.path.join(OUT, "正则导入-内联测试.json")
json.dump(mmd, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("已生成:", path)
print("replaceString 字符数:", len(probes), "| 含真实换行:", probes.count(chr(10)))
json.load(open(path, encoding="utf-8")); print("JSON OK")

# 预览
page = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>内联探针预览</title>'
        '<style>body{margin:0;background:#fbf3e9;font-family:system-ui,sans-serif}.wrap{max-width:560px;margin:0 auto;padding:16px}'
        '.note{background:#fff8f0;border:1px solid #e6c9a8;border-radius:10px;padding:10px 14px;color:#7a6450;font-size:13px;margin-bottom:8px}</style>'
        '</head><body><div class="wrap"><div class="note"><b>内联事件探针 · 预览</b><br>浏览器里 A/B/D 应绿、C 按钮可点。MMD 实测里缺谁=该写法被平台限制。</div>'
        '<div class="content left">' + probes + '</div></div></body></html>')
open(os.path.join(OUT, "预览-内联测试.html"), "w", encoding="utf-8").write(page)
print("已生成 预览-内联测试.html")
