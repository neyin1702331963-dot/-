# -*- coding: utf-8 -*-
# 生成 <script> 载体版正则导入 json（当前MMD）：仅把雷达引擎从 img onerror 换成 <script>
# 数据格式、引擎逻辑、CSS、美化、对抗哨兵全部不变 —— 受控 A/B，便于实测对比
import importlib.util, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
OUT = os.path.join(PROJ, "output")

spec = importlib.util.spec_from_file_location("buildmod", os.path.join(HERE, "build.py"))
bm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bm)

# ---- 把 img onerror 引擎转成 <script> 载体 ----
ENGINE_IMG = bm.ENGINE  # <img src='x' ... onerror="(function(e){...})(this)">
inner = ENGINE_IMG.split('onerror="', 1)[1].rsplit('">', 1)[0]   # (function(e){...})(this)
assert inner.endswith("(this)"), "引擎尾部结构异常"
body = inner[:-len("(this)")]                                     # (function(e){...})
ENGINE_SCRIPT = "<script>" + body + "(document.currentScript)</script>"

# ---- 安全检查：script 内不得出现会提前闭合的序列 ----
problems = []
if "</script" in ENGINE_SCRIPT[len("<script>"):-len("</script>")].lower():
    problems.append("内部含 </script")
if "<!--" in ENGINE_SCRIPT:
    problems.append("含 <!--")
if '"' in body:
    problems.append("引擎内含双引号")
print("script 载体安全检查:", problems if problems else "通过（无 </script / <!-- / 双引号）")

# ---- 复用现成 json 的其余 4 条规则，只替换雷达引擎 ----
src = json.load(open(os.path.join(OUT, "正则导入.json"), encoding="utf-8"))
rules = []
for r in src["regex_scripts"]:
    if r["scriptName"] == "雷达引擎":
        rules.append({"id": -1, "scriptName": "雷达引擎(script载体)",
                      "findRegex": "<ztl>", "replaceString": ENGINE_SCRIPT})
    else:
        rules.append(r)

out = {
    "pageDepth": src["pageDepth"],
    "statusbar": src["statusbar"],
    "beginning": src["beginning"],
    "regex_scripts": rules,
}

path = os.path.join(OUT, "正则导入-script版.json")
json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("\n已生成:", path)
print("== 字符数核查（限 findRegex<=1000 / replaceString<=10000 / 条数<=30）==")
for r in out["regex_scripts"]:
    fr, rs = len(r["findRegex"]), len(r["replaceString"])
    print("  %-18s findRegex=%-4d replaceString=%-5d %s"
          % (r["scriptName"], fr, rs, "OK" if fr <= 1000 and rs <= 10000 else "!!超限"))
print("  条数 = %d / 30" % len(out["regex_scripts"]))
print("\n载体对比：")
print("  旧 img版:", ENGINE_IMG[:70], "...")
print("  新script版:", ENGINE_SCRIPT[:70], "...")
