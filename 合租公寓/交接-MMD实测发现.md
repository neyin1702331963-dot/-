# MMD 平台实测发现 · 交接给 tavern-mmd skill 作者

> 测试环境：当前 MMD（meimoai13.com / sexyai 系），手机端 + 真实多轮对话
> 测试日期：2026-06-15
> 测试载体：除特别说明外，JS 均通过 `<img onerror>` 注入（已证实可靠）
> 配套实例：本仓库 `合租公寓/output/` 下的 ES6 探针、ES6 版状态栏、script 版（反例）

---

## 发现 1：当前 MMD 完全支持 ES6（实测 ✅，原"ES5 only"红线可解除）

用 `img onerror` 载体逐语法独立探针测试，**7/7 全部可用、结果正确**：

| 语法 | 测试代码 | 实测结果 |
|---|---|---|
| 箭头函数 | `[1,2,3].map(x=>x*2)` | ✅ `2,4,6` |
| let / const | `const a=10;let b=20;a+b` | ✅ `30` |
| 模板字符串 | `` `你好-${n}-${2020+6}` `` | ✅ `你好-MMD-2026` |
| 解构赋值 | `const {p,q}=o` | ✅ `16` |
| 展开运算符 | `[...[1,2],...[3,4]]` | ✅ `4` |
| 可选链 | `o?.a?.b` | ✅ `42/undefined` |
| ES5 基准 | `[1,2,3].join('-')` | ✅ `1-2-3` |

**结论**：旧版"遇到 `=>` 从该处截断、ES5 only"的限制，在当前版**已不存在**。
**前提**：以上在 `img onerror` 载体内测得；DOM 属性内仍建议单行（多行未单独验证）。

> 探针文件：`output/正则导入-es6测试.json`（可复现）

---

## 发现 2：`<script>` 载体做不了 per-message 自渲染状态栏（实测 ❌）

把雷达引擎从 `img onerror` 改成 `<script>` 载体后，状态栏**整块空白**。结合平台官方《聊天页正则JS写法指南》，原因有二：

1. **`<script>` 内拿不到自身位置**：官方所有 script 示例都是 `window.__fn = window.__fn || function(){}` + `onclick` 调用，**从不自定位**；自渲染引擎依赖的 `document.currentScript` 在 MMD 执行模型里不可用。
2. **同一段 `<script>` 只加载一次**（官方原文）：而状态栏每条消息都带一份相同引擎 → 会被去重，不逐条执行。

**结论**：
- **per-message 动态渲染（状态栏引擎）必须用 `<img onerror>`** —— 每元素每条触发、`this` 可靠自定位。
- `<script>` 的正确用途：定义 `window.__唯一名` 全局函数，给 `onclick` 调（选项填输入框、折叠、画廊切图等**交互**）。
- 即"开放 script"对**动态状态栏无帮助**；它主要让**点击类交互**可以正规写，降低新手门槛。

> 反例文件：`output/正则导入-script版.json`（导入后状态栏空白，作反面教材）

---

## 发现 2.5：内联事件实测（DOM 属性里的 JS）

| 写法 | 旧版 | 当前版实测 |
|---|---|---|
| 单行 `onerror` | ✅ | ✅ |
| **多行 `onerror`**（属性值带换行） | ❌ 单行 only | **✅ 可用** |
| **属性内双引号**（单引号属性 `onerror='...'` 内用 `"`） | ❌ 须单引号 | **✅ 可用** |
| **复杂 `onclick`**（多行 + `var` + `try-catch`） | ❌ 整个元素被"手术式切除" | ⚠️ **元素不再被删，但 onclick 不触发（被净化）** |

**结论**：
- `onerror` 彻底解放：多行、双引号随便用，代码可写干净。
- `onclick` 仍被净化：**只能"单行调用一个全局函数"**（官方示例全是 `onclick="window.__fn()"`）。复杂逻辑必须：① `<script>` 定义 `window.__唯一名`，或 ② 在 `img onerror` 里用 `el.onclick=function(){}` **JS 赋值**绑定（净化器只扫 HTML 属性文本，扫不到 JS 赋的处理器——雷达引擎选项按钮即此法，故不受影响）。
- 旧版"手术式切除整元素"在当前版**已改为只净化 onclick 属性**（元素保留）。

> 探针文件：`output/正则导入-内联测试.json`

---

## 发现 3：官方文档其他要点（与 skill 现状有出入，建议核对）

| 项 | skill 现状 | 官方文档实际 |
|---|---|---|
| 正则条数上限 | 旧版写 30 条 | **当前 130 条** |
| 原生状态栏 | 未提 | 有**内置 KV 替换**：`【状态】hp::85;;mood::害羞【/状态】` → 替换里直接用 `$hp`/`$mood`，**纯 HTML/CSS 零 JS**（适合固定字段；动态/自创 NPC 仍需 img 引擎） |
| 标签白名单 | 未列全 | 可用 `div span p a img button style details summary table video input textarea`；被删 `section header footer nav iframe canvas audio form` |
| `replaceString` 上限 | 文档某处写 10000 | mmd.md 表格写 20000；以平台实际为准，建议统一 |
| 选项填输入框选择器 | 引擎用 `.uni-textarea-textarea` | 官方示例用 `document.querySelector('textarea, input[type="text"]')`，建议引擎加兜底 |
| `{{user}}/{{char}}` | — | 仅开场白生效，AI 回复里不替换 |
| `{{random:A::B::C}}` | — | 替换内容里可用 |

---

## 建议 skill 更新清单

1. **`references/platforms/mmd.md`**
   - "ES6+ 语法：建议仍用 ES5（待验证）" → **改为"实测全支持（img 载体下）"**，附发现 1 的能力表。
   - 正则条数 30 → **130（当前版）**。
   - 增补"`<script>` 不适用于 per-message 自渲染（currentScript 不可用 + 同段去重）"，明确 `<script>` 仅用于 `window.__fn` 交互。
   - 增补官方原生 KV `$field` 状态栏写法（作为固定字段的轻量首选）。

2. **`references/beautify/statusbar-radar.md`**
   - 在"script 载体变体"处加红字警告：**当前 MMD 实测 `<script>` 载体会导致状态栏空白**，per-message 引擎只能 img onerror。
   - 引擎可改用 ES6（更短更易读），附 ES6 版引擎示例。

3. **`references/quality/checklist.md`**
   - "全 ES5"一项：当前 MMD 可放宽为 ES6；旧版仍 ES5。区分平台。

4. **`references/output/regex-output.md` / `references/beautify/global-css.md`**
   - 补充标签白名单、`{{random}}`、原生 `$field` 用法、选项选择器兜底。

---

## 配套文件索引（本仓库 `合租公寓/output/`）

| 文件 | 用途 |
|---|---|
| `正则导入-es6测试.json` | ES6 能力探针（7 语法，实测全绿） |
| `正则导入-es6版.json` | **ES6 版真实状态栏**（功能同 ES5 版，引擎 ES6 重写，可导入验证） |
| `正则导入.json` | ES5 版状态栏（稳定基线） |
| `正则导入-script版.json` | `<script>` 载体反例（空白，反面教材） |
| `预览-*.html` | 各版本本地浏览器预览 |
