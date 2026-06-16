# -*- coding: utf-8 -*-
# 浏览器存储/缓存探针：localStorage / sessionStorage / cookie / indexedDB
# 载体 img onerror；带"累计运行次数"计数器 → 刷新后数字变大=持久化成功
import json, os
OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")

def probe(label, body):
    return ("<img src='x' style='display:none' onerror=\"(function(e){"
            "var d=document.createElement('div');"
            "d.style.margin='6px';d.style.padding='8px';d.style.borderRadius='6px';d.style.fontSize='13px';"
            "d.style.background='#fff3cd';d.style.color='#856404';"
            "d.textContent='⧗ " + label + "：未执行';"
            "e.parentNode.insertBefore(d,e.nextSibling);"
            "try{" + body + ";d.style.background='#e6f7e6';d.style.color='#1a7f1a'}"
            "catch(err){d.style.background='#fdeaea';d.style.color='#b00020';"
            "d.textContent='✗ " + label + " 不可用 → '+err}"
            "})(this)\">")

probes = "".join([
    # localStorage：写读 + 持久化计数器
    probe("A localStorage",
          "localStorage.setItem('mmd_ls','ok');"
          "var v=localStorage.getItem('mmd_ls');"
          "if(v!=='ok')throw '读回不一致';"
          "var n=(parseInt(localStorage.getItem('mmd_ls_n'))||0)+1;"
          "localStorage.setItem('mmd_ls_n',n);"
          "d.textContent='✓ A localStorage 可用｜读回='+v+'｜累计运行='+n+' 次（刷新后应+1）'"),
    # sessionStorage：写读 + 计数器
    probe("B sessionStorage",
          "sessionStorage.setItem('mmd_ss','ok');"
          "var v=sessionStorage.getItem('mmd_ss');"
          "if(v!=='ok')throw '读回不一致';"
          "var n=(parseInt(sessionStorage.getItem('mmd_ss_n'))||0)+1;"
          "sessionStorage.setItem('mmd_ss_n',n);"
          "d.textContent='✓ B sessionStorage 可用｜累计运行='+n+' 次'"),
    # cookie：写读
    probe("C cookie",
          "document.cookie='mmd_ck=ok;path=/';"
          "if(document.cookie.indexOf('mmd_ck=ok')===-1)throw 'cookie 未写入';"
          "d.textContent='✓ C cookie 可用｜cookie 串长='+document.cookie.length"),
    # indexedDB：接口存在性（open 为异步，此处只测接口）
    probe("D indexedDB",
          "if(!window.indexedDB)throw 'indexedDB 接口不存在';"
          "d.textContent='✓ D indexedDB 接口存在（异步库，可用于大数据缓存）'"),
])

mmd = {
    "pageDepth": 2, "statusbar": "",
    "beginning": ("浏览器存储/缓存探针（载体 img onerror）。\n"
                  "应出现 4 个框：绿=可用 / 红=被禁。\n"
                  "★关键：记下 A/B 的「累计运行」数字，刷新或重进聊天后再看——\n"
                  "  数字变大=缓存能持久化；一直是 1 或报错=被沙箱隔离。\n"
                  "<storeprobe>"),
    "regex_scripts": [{"id": -1, "scriptName": "存储探针", "findRegex": "<storeprobe>", "replaceString": probes}],
}
path = os.path.join(OUT, "正则导入-存储测试.json")
json.dump(mmd, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.load(open(path, encoding="utf-8"))
import re
inners = re.findall(r'onerror="(.*?)">', probes)
print("已生成:", path)
print("字符数:", len(probes), "| 各探针 onerror 内双引号数:", [s.count('\"') for s in inners], "| JSON OK")

# 预览
page = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>存储探针预览</title>'
        '<style>body{margin:0;background:#fbf3e9;font-family:system-ui,sans-serif}.wrap{max-width:560px;margin:0 auto;padding:16px}'
        '.note{background:#fff8f0;border:1px solid #e6c9a8;border-radius:10px;padding:10px 14px;color:#7a6450;font-size:13px;margin-bottom:8px}</style>'
        '</head><body><div class="wrap"><div class="note"><b>浏览器存储探针 · 预览</b><br>浏览器里 4 个应全绿；刷新本页 A/B 的「累计运行」会+1。MMD 实测里看哪个绿、刷新后数字是否增长。</div>'
        '<div class="content left">' + probes + '</div></div></body></html>')
open(os.path.join(OUT, "预览-存储测试.html"), "w", encoding="utf-8").write(page)
print("已生成 预览-存储测试.html")
