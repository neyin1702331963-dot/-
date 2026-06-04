/* 构建：把新引擎装回原 JSON（只换 JS 段），并产出浏览器预览页。 */
const fs = require('fs');
const path = require('path');
const SRC = __dirname;
const OUT = path.join(SRC, '..');

const orig = JSON.parse(fs.readFileSync(path.join(SRC, 'original.json'), 'utf8'));
const engine = fs.readFileSync(path.join(SRC, 'engine.js'), 'utf8');

function find(name) { return orig.regex_scripts.find(s => s.scriptName === name); }
const skeleton = find('主骨架').replaceString;
const css = find('CSS').replaceString;

// ---- 1) 生成 v2 JSON：原结构不动，仅替换 JS 段 ----
const v2 = JSON.parse(JSON.stringify(orig));
v2.regex_scripts.find(s => s.scriptName === 'JS').replaceString = engine;
fs.writeFileSync(path.join(OUT, '魔女能力选择-v2.json'), JSON.stringify(v2));

// ---- 2) 生成预览页：复刻 SillyTavern 的占位符替换链 ----
const injected = skeleton
  .split('[开场选择CSS]').join(css)
  .split('[开场选择脚本]').join(engine);
const preview =
`<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>魔女能力选择 · 预览</title>
<style>html,body{margin:0;min-height:100%;background:#04050c;display:flex;align-items:center;justify-content:center;padding:24px}</style>
</head><body>
${injected}
</body></html>`;
fs.writeFileSync(path.join(OUT, 'preview.html'), preview);

// ---- 3) 字符数核对（每段必须 < 20000）----
const LIMIT = 20000;
let ok = true;
console.log('段字符数 / 2w 上限:');
for (const s of v2.regex_scripts) {
  const n = s.replaceString.length;
  const pass = n < LIMIT;
  ok = ok && pass;
  console.log(`  ${s.scriptName.padEnd(8)} ${String(n).padStart(6)}  ${pass ? 'OK' : '!! 超限'}  (余 ${LIMIT - n})`);
}
console.log('preview.html 字节:', Buffer.byteLength(preview));
console.log(ok ? '全部通过 ✔' : '存在超限 ✘');
process.exit(ok ? 0 : 1);
