# -*- coding: utf-8 -*-
# 缓存隔离对比探针：普通键 vs CUSTOM_ 前缀键，各带持久化计数器
# 重进聊天后看：两个都涨=平台已兼容普通键；只有CUSTOM_涨=隔离仍生效、普通键被隔离
import json, os
OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")

def probe(label, key):
    body = ("var k='" + key + "';"
            "localStorage.setItem(k+'_v','ok');"
            "var v=localStorage.getItem(k+'_v');"
            "if(v!=='ok')throw '写后立即读不回（强隔离）';"
            "var n=(parseInt(localStorage.getItem(k+'_n'))||0)+1;"
            "localStorage.setItem(k+'_n',n);"
            "d.textContent='✓ " + label + " 累计运行='+n+' 次（键名 '+k+'）'")
    return ("<img src='x' style='display:none' onerror=\"(function(e){"
            "var d=document.createElement('div');"
            "d.style.margin='6px';d.style.padding='8px';d.style.borderRadius='6px';d.style.fontSize='13px';"
            "d.style.background='#fff3cd';d.style.color='#856404';"
            "d.textContent='⧗ " + label + "：未执行';"
            "e.parentNode.insertBefore(d,e.nextSibling);"
            "try{" + body + ";d.style.background='#e6f7e6';d.style.color='#1a7f1a'}"
            "catch(err){d.style.background='#fdeaea';d.style.color='#b00020';"
            "d.textContent='✗ " + label + " 失败 → '+err}"
            "})(this)\">")

probes = probe("P1 普通键", "mmd_plain") + "\n" + probe("P2 CUSTOM_键", "CUSTOM_mmd")

mmd = {
    "pageDepth": 2, "statusbar": "",
    "beginning": ("缓存隔离对比探针：P1 普通键 vs P2 CUSTOM_ 键。\n"
                  "★记下两个「累计运行」数字 → 退出重进聊天 → 再看：\n"
                  "  两个都+1 = 平台已兼容普通键；只有 P2(CUSTOM_)+1 = 隔离仍生效，普通键被隔离。\n"
                  "<isoprobe>"),
    "regex_scripts": [{"id": -1, "scriptName": "缓存隔离对比", "findRegex": "<isoprobe>", "replaceString": probes}],
}
path = os.path.join(OUT, "正则导入-缓存隔离对比.json")
json.dump(mmd, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.load(open(path, encoding="utf-8"))
import re
inners = re.findall(r'onerror="(.*?)">', probes)
print("已生成:", path, "| 双引号数:", [s.count('\"') for s in inners], "| JSON OK")
