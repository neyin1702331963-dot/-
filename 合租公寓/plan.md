# 合租公寓 · 任务计划

## 决策记录
- 平台：旧版 MMD（不支持 script，ES5）
- 卡类型：多角色卡 · 现代都市暧昧 · 合租公寓 · 3 位可互动角色
- 组件：世界书 + 状态栏 + 全局美化
- 产出：`output/角色卡.json`（chara_card_v3）+ `output/正则导入.json`（MMD 4 字段：状态栏+全局美化）

## 步骤清单

### 阶段 A：设定（纯文字，平台无关）
- [x] A1 角色阵容确认（3 位角色一句话概念）—— **停下让用户确认**
- [x] A2 三位角色 description（YAML+xml，绝对零度/八股检查）
- [x] A3 世界书条目规划表（条目名+触发+用途）—— **停下让用户确认**
- [x] A4 世界书条目正文撰写
- [x] A5 文风条目（style_guide，蓝灯常驻）
- [x] A6 开场白 first_mes（三人同场引入，符合文风）

### 阶段 B：技术组件（旧版 MMD 红线分流）
- [x] B1 状态栏方案选型（混合态雷达法 / KV V4.0）+ 字段设计
- [x] B2 状态栏正则代码（img onerror 点火器 / ES5 / 时间戳 / data-s）
- [x] B3 全局美化（正则包裹 + uni-app 类名覆盖 + !important + body 开关类）
- [x] B4 技术组件成稿 —— **停下让用户确认**

### 阶段 C：组装与交付
- [x] C1 组装 chara_card_v3 角色卡 json（含 character_book）
- [x] C2 组装 MMD 4 字段正则导入 json
- [x] C3 跑 quality/checklist.md 自检 + `python -m json.tool` 校验
- [x] C4 全部产出进 output/，更新 main.md —— **最终交付**

## 验收标准
- 角色卡：3 位角色性格独立成块，AI 不串调；全简中；无占位符/八股
- 世界书：条目触发关键词明确，token 预算合理
- 状态栏：旧版 MMD 可二次使用（时间戳唯一）、单行 onerror、ES5
- 全局美化：!important 覆盖 uni-app 类名，body 开关类可切换
- 所有 json 通过语法校验
