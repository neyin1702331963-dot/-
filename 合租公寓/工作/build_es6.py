# -*- coding: utf-8 -*-
# ES6 能力探针：固定用 img onerror 当载体，逐个 ES6 语法独立测试
# 出绿框=可用；红框=运行报错（语法被解析了但抛错）；不出框=被平台截断/禁用
import json, os

OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")

# 每个探针：先 ES5 建框+默认黄字，再 try 里跑 ES6 特性，成功转绿、异常转红
def probe(label, body_js):
    # body_js 必须把结果赋给 __r
    return ("<img src='x' style='display:none' onerror=\""
            "(function(e){"
            "var d=document.createElement('div');"
            "d.style.margin='6px';d.style.padding='8px';d.style.borderRadius='6px';d.style.fontSize='13px';"
            "d.style.background='#fff3cd';d.style.color='#856404';"
            "d.textContent='⧗ " + label + "：未执行（疑被截断/禁用）';"
            "e.parentNode.insertBefore(d,e.nextSibling);"
            "try{" + body_js + ";"
            "d.style.background='#e6f7e6';d.style.color='#1a7f1a';"
            "d.textContent='✓ " + label + " 可用 → '+String(__r)}"
            "catch(err){d.style.background='#fdeaea';d.style.color='#b00020';"
            "d.textContent='✗ " + label + " 报错 → '+err}"
            "})(this)\">")

probes = [
    # A：纯 ES5 基准（必出，证明载体正常）
    probe("A 基准(ES5)", "var __r=[1,2,3].join('-')"),
    # B：箭头函数
    probe("B 箭头函数", "var __r=[1,2,3].map(x=>x*2).join(',')"),
    # C：let / const
    probe("C let/const", "const a=10;let b=20;var __r=a+b"),
    # D：模板字符串
    probe("D 模板字符串", "var n='MMD';var __r=`你好-${n}-${2020+6}`"),
    # E：解构赋值
    probe("E 解构赋值", "var o={p:7,q:9};var {p,q}=o;var __r=p+q"),
    # F：展开运算符
    probe("F 展开运算符", "var __r=[...[1,2],...[3,4]].length"),
    # G：可选链
    probe("G 可选链", "var o={a:{b:42}};var __r=(o?.a?.b)+'/'+(o?.x?.y)"),
]

mmd = {
    "pageDepth": 2,
    "statusbar": "",
    "beginning": "ES6 能力探针（载体=img onerror，已知可用）。\n下面应出现 7 个结果框：✓绿=该语法可用 / ✗红=运行报错 / 不出框=被平台截断或禁用。\n<es6probe>",
    "regex_scripts": [
        {"id": -1, "scriptName": "ES6探针", "findRegex": "<es6probe>",
         "replaceString": "".join(probes)},
    ],
}

path = os.path.join(OUT, "正则导入-es6测试.json")
json.dump(mmd, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("已生成:", path)
rs = mmd["regex_scripts"][0]["replaceString"]
print("探针条数:", len(probes), "| replaceString 字符数:", len(rs), "(限10000)")
# 安全自检：onerror 内不得有双引号
import re
inners = re.findall(r'onerror="(.*?)">', rs)
print("各探针 onerror 内双引号数:", [s.count('"') for s in inners])
print("校验:", end=" ")
json.load(open(path, encoding="utf-8")); print("JSON OK")
