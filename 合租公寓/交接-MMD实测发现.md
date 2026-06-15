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
**前提**：以上在 `img onerror` 载体内测得。`onerror` 属性已实测可多行、可用双引号（见发现 2.5）。

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
| 单行 inline `onclick`（`this.x='y'` 直接 DOM 操作） | 旧版"放行极简单行" | ❌ **不触发**（C1 实测） |
| `onclick="window.__fn()"`（调全局函数） | — | ✅ 可用（C2 实测） |
| `el.onclick=function(){}`（img onerror 里 JS 赋值） | ✅ | ✅ 可用（C3 实测） |
| 复杂/多行 `onclick`（`var`+`try-catch`） | 整元素被"手术式切除" | ⚠️ 元素保留但不触发 |

**结论**：
- `onerror` 彻底解放：多行、双引号随便用，代码可写干净。
- **`onclick` 属性里的逻辑全被净化**——连单行 `this.xxx='yyy'` 都不放行（比旧版更严）；**只认 `onclick="window.__fn()"` 这种"调用全局函数"的形式**。
- 干活两条路：① `img onerror`/`<script>` 里定义 `window.__唯一名` + `onclick="__fn()"`（官方推荐）；② `img onerror` 里 `el.onclick=function(){}` **JS 赋值**绑定（净化器只扫 HTML 属性文本，扫不到 JS 赋的 handler——雷达引擎选项按钮即此法，故一直能点）。
- 旧版"手术式切除整元素"在当前版**已改为只净化 onclick 属性**（元素保留）。

> 探针文件：`output/正则导入-内联测试.json`、`output/正则导入-onclick边界.json`

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

## 这次平台更新具体能做到什么（给作者/进阶用户）

**本质：是"代码终于能正常写了"，不是"能算的东西变多了"。** ES5 + img onerror 本就图灵完备，任何逻辑都算得出来。所以收益是——同一功能，代码更短、能用双引号、能多行、人能读能改、bug 更少。

**最有实感的一块：`onerror` 能多行 + 用双引号。** 以前引擎是"单行天书"（全挤一行、只能单引号），复杂状态栏基本"只能 AI 生成、人看不懂改不动"；现在能写成正常多行函数，维护难度断崖下降。这是对会写引擎的人最实在的好处。

**ES6 语法（纯写法糖，举卡片里的实际用法）：**

- **展开运算符** — 不可变更新状态 / 合并列表：
  ```js
  const next = { ...上一轮状态, 好感: 上一轮状态.好感 + 3 };   // 复制并只改一个字段
  const 在场 = [ ...三位室友, ...新登场NPC ];                    // 合并在场名单
  ```
- **模板字符串** — 拼 HTML/文本不用满屏 `+`：`` `好感 ${cur}/${max}` ``
- **解构 + 可选链** — 一次取多字段、安全取嵌套不崩：
  ```js
  const { hp, mood, favor } = 数据;
  const 好感 = 数据?.npc?.好感 ?? 0;   // 不存在给 0，不报错
  ```
- **箭头 + map/filter** — 一行渲染"只显示在场角色"：`在场.filter(n=>n).map(name=>建角色卡(name))`

**没解放的边界（仍受限）：**
- inline `onclick` 里写逻辑依然不行（连单行都被净化），只能 `onclick="window.__fn()"` 或 JS 赋值绑定。
- `<script>` 载体做不了 per-message 自渲染，状态栏引擎仍只能 `img onerror`。

**一句话**：状态栏这种复杂引擎，从"prompt 辅助生成的天书"变成"人能手写手改的正常 ES6 代码"。对作者/进阶用户是实打实提效；对普通玩家几乎无感（卡照用，只是以后的卡可能更稳更花哨）。

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
| `正则导入-内联测试.json` | 内联事件探针（多行 onerror / 双引号 / 复杂 onclick） |
| `正则导入-onclick边界.json` | onclick 边界探针（单行 inline / window.__fn / JS 赋值） |
| `预览-*.html` | 各版本本地浏览器预览 |
