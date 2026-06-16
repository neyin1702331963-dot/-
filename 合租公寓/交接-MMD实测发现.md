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

**专项判定探针实测（决定性）**：一条正则同时注入 `<script>`（S1，用 `document.currentScript` 自检）+ `img onerror`（S2，对照）。结果：**S2 绿、S1 一个框都没有**。S1 脚本经 `new Function` 验证语法合法（浏览器必执行）→ 即 **`<script>` 经正则注入在 MMD 根本不执行**（不是"执行了但 currentScript 为 null"——那会出 S1 橙框）。

**机制**：平台把正则替换内容当 **innerHTML** 插入；HTML 规范下 **innerHTML 里的 inline `<script>` 永不执行**，而 `<img onerror>` 会触发。这就是为什么状态栏引擎换 `<script>` 载体后整块空白。

**结论**：
- **per-message 动态渲染（状态栏引擎）必须用 `<img onerror>`**；字面 `<script>` 标签经正则注入**不执行**。
- ⚠️ **与官方《写法指南》有出入**：官方示例 5/6/14 写 `<script>window.__fn=…</script>` 并称可用，但实测正则注入的 `<script>` 不执行。可能文档不准，或指"非正则注入（如直接写入某处、一次性）"的场景——**建议作者复核其示例 `<script>` 的实际生效位置**。
- 术语澄清：作者口中"script 还能生效"指**广义 JS 能跑**（其卡用 `img onerror` 载体，JS 照跑），并非字面 `<script>` 标签执行——与本结论不冲突。

> 探针文件：`output/正则导入-script版.json`（状态栏空白反例）、`output/正则导入-script判定.json`（S1无输出/S2绿，决定性证据）

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
| `onclick="eval(getElementById(..).dataset.s)"`（轻主板+胖遥控器 §5.3） | ✅ | ✅ **仍可用**（E1 实测；eval 本体未被 CSP 拦） |
| `onclick="eval('内联代码字符串')"`（代码串塞进属性） | — | ❌ 不触发（E2 实测） |
| 复杂/多行 `onclick`（`var`+`try-catch`） | 整元素被"手术式切除" | ⚠️ 元素保留但不触发 |

**结论**：
- `onerror` 彻底解放：多行、双引号随便用，代码可写干净。
- **`onclick` 属性放行的是"干净的调用/引用表达式"**（`__fn()`、`eval(x.dataset.s)`——属性里只有标识符与属性访问）；**一旦属性里出现代码字符串字面量或直接 DOM 赋值语句就被净化**（C1 单行 `this.x='y'`、E2 `eval('...代码...')` 均不触发）。
- **旧版 §5.3「轻主板+胖遥控器」在当前 MMD 确认仍可用**（E1）——因为它把代码放进 `data-s`、onclick 只做 `eval(dataset.s)`，恰好符合"属性内只有调用表达式"的放行条件。**无需标"待复测"，可标"已复测可用"。**
- 干活三条路（均实测可用）：① `onclick="window.__fn()"` 调全局函数；② `img onerror` 里 `el.onclick=function(){}` JS 赋值（雷达引擎用此法）；③ 轻主板 `onclick="eval(...dataset.s)"`。
- 旧版"手术式切除整元素"在当前版**已改为只净化 onclick 属性**（元素保留）。

> 探针文件：`output/正则导入-内联测试.json`、`output/正则导入-onclick边界.json`、`output/正则导入-eval测试.json`

---

## 发现 2.6：浏览器存储/缓存（localStorage 等）+ 6.15 隔离事件

**实测（img onerror 载体）：`localStorage` / `sessionStorage` / `cookie` / `indexedDB` 接口均可用，且 localStorage/sessionStorage 跨"重进聊天"持久化成功（计数器累加，非每次归零）。**

| 项 | 实测 |
|---|---|
| localStorage 写读 + 持久 | ✅（重进聊天计数器 +1，读回正确） |
| sessionStorage | ✅ |
| cookie | ✅ |
| indexedDB 接口 | ✅ 存在 |
| 引擎重跑时机 | 页内"小刷新"不重跑（DOM 不重建）；**退出重进**才重渲染、img onerror 重触发 |

**6.15 隔离事件（重要，关系到老卡批量"数据空/情报不足"）：**
- 6.15 更新一度把缓存**做了隔离**（官方"小魅"说法），用**普通键**缓存的老卡集体失效——引擎若靠 localStorage 兜底数据，隔离期读空 → 状态栏显示"情报不足/--"。
- 平台随后打了**兼容补丁**，普通键又可持久（实测：普通键 `mmd_plain` 与 `CUSTOM_mmd` 重进后均 +1，两者都活）。
- 官方正解：**使用 `CUSTOM_` 前缀的 localStorage 键**（隔离豁免）。

**结论 / 建议**：
- 卡的 localStorage 键**一律加 `CUSTOM_` 前缀**——官方豁免、隔离开关都稳；普通键"现在能用"只是靠兼容补丁，不保证（6.15 证明平台会收紧），不要依赖。
- 老卡缓存失效的修复 = **只把键名加 `CUSTOM_` 前缀，逻辑不动**。
- 注意：存储是**显示层**，不进 AI 上下文（AI 读不到 localStorage）；解决的是"前端记忆/兜底数据"，不是"让 AI 记住"。

> 探针文件：`output/正则导入-存储测试.json`、`output/正则导入-缓存隔离对比.json`

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

> **真实崩卡案例（平台作者群 2026-06）**：有作者的卡更新后"全崩"，自述"es6 对标签闭合的清洗，把我有些标签当做恶意代码洗掉了"。**实为误判**——ES6 语法实测 7/7 全通过，真正机制是**渲染层 HTML 净化器把非白名单/未规范闭合的标签整段剥离**，依赖这些标签的代码失去载体而崩。排查方向：① 是否用了被删标签（`section/header/footer/nav/iframe/canvas/audio/form`）；② 标签是否规范闭合。修复：只用白名单标签 + 规范闭合 + 载体统一 `img onerror`。（另有作者反馈个例 fix「把 `W.` 改成 `document`」，疑为 `window` 别名在净化/新引擎下失效，偏卡片特定，需原码确认。）
> 作者后续**亲口确认**：崩卡「和 script 没关系」「script 还能生效」，他的修复就是「换了其中几个标签，换成合法的」。即根因 = **标签净化**，与 `<script>`、ES6 均无关。注意此处「script 还能生效」指广义 `<script>` 可执行（定义 `window.__fn` 等用法）；与本文发现 2「`<script>` 做不了 per-message 自渲染引擎」不冲突——两者指不同场景。

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
