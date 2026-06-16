# -*- coding: utf-8 -*-
# 复测文档主张：AI「回复」里被正则替换出的 <script> 到底执不执行
# 产出① 一张让AI每轮输出 <scrtest> 的极简卡  ② 把 <scrtest> 替换成 script盒+img盒 的正则
import json, os
OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")
ST = "margin:6px;padding:8px;border-radius:6px;font-size:13px"

# 正则替换为：S(script盒) + I(img盒对照)
S = ("<div id='srx'></div><script>(function(){var a=document.getElementById('srx')||document.body;"
     "var d=document.createElement('div');d.style.cssText='" + ST + ";background:#e6f7e6;color:#1a7f1a';"
     "d.textContent='✓ S 正则替换出的 <script> 在【AI回复】里执行了';a.appendChild(d)})();</script>")
I = ("<img src='x' style='display:none' onerror=\"(function(e){"
     "var d=document.createElement('div');d.style.cssText='" + ST + ";background:#e6f7e6;color:#1a7f1a';"
     "d.textContent='✓ I 对照 img onerror 在【AI回复】里执行了';e.parentNode.insertBefore(d,e.nextSibling)})(this)\">")

reg = {
    "pageDepth": 2, "statusbar": "",
    "beginning": "（script 回复复测）随便发一句话，我每轮回复末尾会带一个测试标记。\n看 AI 回复下方出现：S(绿)=正则替换的<script>在回复里执行 / 只有I=仍不执行。",
    "regex_scripts": [
        {"id": -1, "scriptName": "script回复复测", "findRegex": "<scrtest>", "replaceString": S + I},
    ],
}
p1 = os.path.join(OUT, "正则导入-script复测.json")
json.dump(reg, open(p1, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 极简卡：强制 AI 每轮回复输出 <scrtest>
NAME = "script回复复测卡"
PHI = "（系统功能指令，最高优先级）每次回复的正文之后，必须另起一行，原样输出这一行标记，不要解释、不要加引号、不要省略：\n<scrtest>"
inner = {
    "name": NAME, "description": "用于复测：AI 回复里被正则替换出的 <script> 是否执行。",
    "personality": "", "scenario": "随便聊，每轮都会带测试标记。",
    "first_mes": "随便发一句话即可。我每轮回复末尾会输出测试标记 <scrtest>，配合「正则导入-script复测.json」观察 S 框是否出现。",
    "mes_example": "", "creator_notes": "复测专用，测完可删。", "system_prompt": PHI,
    "post_history_instructions": PHI, "tags": ["测试"], "creator": "", "character_version": "1.0",
    "alternate_greetings": [], "group_only_greetings": [],
    "extensions": {"talkativeness": "0.5", "fav": False, "world": NAME,
                   "depth_prompt": {"prompt": PHI, "depth": 1, "role": "system"}},
    "character_book": {"name": NAME, "entries": []},
}
card = {"name": NAME, "description": inner["description"], "personality": "", "scenario": inner["scenario"],
        "first_mes": inner["first_mes"], "mes_example": "", "creatorcomment": inner["creator_notes"],
        "avatar": "none", "talkativeness": "0.5", "fav": False, "tags": inner["tags"],
        "spec": "chara_card_v3", "spec_version": "3.0", "create_date": "2026-06-16T00:00:00.000Z", "data": inner}
p2 = os.path.join(OUT, "script复测-角色卡.json")
json.dump(card, open(p2, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

json.load(open(p1, encoding="utf-8")); json.load(open(p2, encoding="utf-8"))
print("已生成:", p1, "\n        ", p2, "\nJSON OK")
