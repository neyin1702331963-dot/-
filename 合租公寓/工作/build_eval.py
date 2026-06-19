# -*- coding: utf-8 -*-
# eval / 轻主板探针：测 onclick="eval(data-s)"（旧版§5.3 胖遥控器）在当前MMD还灵不灵
import json, os
OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")
BTN = "margin:6px;padding:8px 14px;border-radius:6px;border:1px solid #c8794f;background:#fff8f0;color:#5a4636"
OUTD = "margin:6px;padding:8px;font-size:13px;color:#856404"

# E0：对照——window.__fn（已知可用），确认本条消息里点击正常
E0 = ("<img src='x' style='display:none' onerror=\"window.__e0=window.__e0||function(){var o=document.getElementById('e0out');o.textContent='✓ E0 对照 window.__fn 可用';o.style.color='#1a7f1a'}\">"
      "<button type='button' style='" + BTN + "' onclick=\"window.__e0&&__e0()\">E0 · 点我（对照）</button>"
      "<div id='e0out' style='" + OUTD + "'>E0：待点击</div>")

# E1：轻主板+胖遥控器——onclick="eval(getElementById(...).dataset.s)"
E1 = ("<p id='FUNC_e1' style='display:none' data-s=\"var o=document.getElementById('e1out');o.textContent='✓ E1 eval(data-s) 轻主板可用';o.style.color='#1a7f1a'\"></p>"
      "<button type='button' style='" + BTN + "' onclick=\"eval(document.getElementById('FUNC_e1').dataset.s)\">E1 · 点我（轻主板 eval data-s）</button>"
      "<div id='e1out' style='" + OUTD + "'>E1：待点击</div>")

# E2：onclick 内直接 eval 一个字符串字面量（测 eval 本体是否被放行）
E2 = ("<button type='button' style='" + BTN + "' onclick=\"eval('var o=document.getElementById(&quot;e2out&quot;);o.textContent=&quot;✓ E2 eval(内联字符串) 可用&quot;;o.style.color=&quot;#1a7f1a&quot;')\">E2 · 点我（eval 内联字符串）</button>"
      "<div id='e2out' style='" + OUTD + "'>E2：待点击</div>")

probes = E0 + "\n" + E1 + "\n" + E2
mmd = {"pageDepth": 2, "statusbar": "",
       "beginning": "eval/轻主板探针：三个按钮各点一下。\nE0对照(必绿) / E1轻主板eval(data-s) / E2 eval内联字符串。\n绿=可用，无反应=被净化。\n<evalprobe>",
       "regex_scripts": [{"id": -1, "scriptName": "eval轻主板探针", "findRegex": "<evalprobe>", "replaceString": probes}]}
path = os.path.join(OUT, "正则导入-eval测试.json")
json.dump(mmd, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.load(open(path, encoding="utf-8"))
print("已生成:", path, "| 字符数:", len(probes), "| JSON OK")
