# -*- coding: utf-8 -*-
# onclick 精确边界探针：单行inline onclick / window.__fn模式 / JS赋值 三种到底行不行
import json, os
OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")

# C1：单行 inline onclick（极简单行，官方说可用）
C1 = ("<button type='button' style='margin:6px;padding:8px 14px;border-radius:6px;border:1px solid #c8794f;background:#fff8f0;color:#5a4636' "
      "onclick=\"this.nextElementSibling.textContent='✓ C1 单行 inline onclick 可用';this.nextElementSibling.style.color='#1a7f1a'\">"
      "C1 · 点我（单行 onclick）</button>"
      "<div style='margin:6px;padding:8px;font-size:13px;color:#856404'>C1：待点击</div>")

# C2：onclick 调用 <img onerror> 里定义的 window.__fn（官方推荐模式）
C2 = ("<img src='x' style='display:none' onerror=\"window.__probeFn=window.__probeFn||function(el){el.textContent='✓ C2 window.__fn 模式可用';el.style.color='#1a7f1a'}\">"
      "<button type='button' style='margin:6px;padding:8px 14px;border-radius:6px;border:1px solid #c8794f;background:#fff8f0;color:#5a4636' "
      "onclick=\"window.__probeFn&&__probeFn(this.nextElementSibling)\">"
      "C2 · 点我（onclick 调 window.__fn）</button>"
      "<div style='margin:6px;padding:8px;font-size:13px;color:#856404'>C2：待点击</div>")

# C3：img onerror 里用 JS 赋值 btn.onclick（雷达引擎用的方式，预期可用）
C3 = ("<div><button type='button' id='c3btn' style='margin:6px;padding:8px 14px;border-radius:6px;border:1px solid #c8794f;background:#fff8f0;color:#5a4636'>"
      "C3 · 点我（JS赋值 onclick）</button>"
      "<div id='c3out' style='margin:6px;padding:8px;font-size:13px;color:#856404'>C3：待点击</div>"
      "<img src='x' style='display:none' onerror=\"(function(e){var b=e.parentNode.querySelector('#c3btn');var o=e.parentNode.querySelector('#c3out');if(b)b.onclick=function(){o.textContent='✓ C3 JS赋值 onclick 可用';o.style.color='#1a7f1a'}})(this)\"></div>")

probes = C1 + "\n" + C2 + "\n" + C3
mmd = {"pageDepth": 2, "statusbar": "",
       "beginning": "onclick 边界探针：三个按钮各点一下。\n绿=可用。对比哪种 onclick 写法被放行。\n<onclickprobe>",
       "regex_scripts": [{"id": -1, "scriptName": "onclick边界", "findRegex": "<onclickprobe>", "replaceString": probes}]}
path = os.path.join(OUT, "正则导入-onclick边界.json")
json.dump(mmd, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.load(open(path, encoding="utf-8"))
print("已生成:", path, "| 字符数:", len(probes), "| JSON OK")
