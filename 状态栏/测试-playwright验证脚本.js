// 用法: node 测试-playwright验证脚本.js      (对比旧版: SB_DIR=<旧文件目录> node 测试-playwright验证脚本.js)
const fs = require('fs');
const path = require('path');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const DIR = process.env.SB_DIR || '/home/user/-/状态栏';


function body(file) {
  const t = fs.readFileSync(path.join(DIR, file), 'utf8');
  const i = t.indexOf('替换内容：');
  return t.slice(i + '替换内容：'.length).split('\n────')[0];
}
const CSS = body('01-状态栏CSS-常驻.txt').trim();
const HTML = body('02-状态栏HTML+JS-常驻.txt').replace(/\n$/, '');
const PORTRAIT = /立绘=[ \t]*(?!https?:)([^_|;\s]+)_([^|;\r\n]+?)[ \t]*(?=[|;\r\n]|$)/g;

function build(statusText) {
  return statusText
    .replace(new RegExp(PORTRAIT.source, 'g'), '立绘=https://meimoaiimg.com/user/1462820/$1-$2.png')
    .replace('<status>', HTML)
    .replace('</status>', '</div></div>');
}

const okStatus = fs.readFileSync(path.join(DIR, '05-状态栏生成示例.txt'), 'utf8');
const badStatus = fs.readFileSync(path.join(DIR, '测试样本-原先失败的AI生成内容.txt'), 'utf8');

const page0 = `<!doctype html><html><head><meta charset="utf-8">${CSS}</head><body>
<div id="chat"></div><div class="chatMsgTextarea"><textarea></textarea></div></body></html>`;

async function probe(page) {
  return page.evaluate(() => {
    const s = document.querySelector('.gal-status-shell');
    if (!s) return { err: 'no shell' };
    const g = n => { const e = s.querySelector(`[data-gal-bind=${n}]`); return e ? e.textContent : null; };
    const body = s.querySelector('.gal-status-npc-body');
    return {
      time: g('time'), turn: g('turn'), event: g('eventTitle'), weather: g('weather'),
      progress: s.querySelector('[data-gal-npc-progress]').textContent,
      tabs: [...s.querySelectorAll('.gal-status-npc-tab')].map(b => b.textContent),
      npcName: g('npcName'), npcField0: g('npcField0'), npcField1: g('npcField1'), npcField8: g('npcField8'),
      favor: g('npcFavor'),
      npcImg: s.querySelector('[data-gal-npc-image]').getAttribute('src'),
      bodyHidden: body.hasAttribute('hidden'),
      bodyDisplay: getComputedStyle(body).display,
      nearby: [...s.querySelectorAll('[data-gal-nearby] .gal-status-scene-option')].map(b => b.textContent),
      actions: [...s.querySelectorAll('.gal-status-action')].map(b => b.textContent),
      badges: ['badge0', 'badge1', 'badge2'].map(g),
      userHasImage: s.querySelector('.gal-status-user-portrait').classList.contains('has-image'),
    };
  });
}

const results = [];
function check(name, cond, extra = '') {
  results.push({ name, pass: !!cond, extra });
  console.log((cond ? '  PASS  ' : '  FAIL  ') + name + (extra ? '   ' + extra : ''));
}

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await browser.newContext({ viewport: { width: 900, height: 900 } });
  const page = await ctx.newPage();
  page.on('pageerror', e => console.log('  !! pageerror:', e.message));
  await page.route('https://gal.test/**', r => r.fulfill({ contentType: 'text/html; charset=utf-8', body: page0 }));
  await page.route('**meimoaiimg.com**', r =>
    r.fulfill({ status: 200, contentType: 'image/gif',
      body: Buffer.from('R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==', 'base64') }));

  // ---- 1. one-shot render (the "示例" case) ----
  console.log('\n[1] 一次性插入（示例）');
  await page.goto('https://gal.test/');
  await page.evaluate(h => { document.getElementById('chat').innerHTML = h; }, build(okStatus));
  await page.waitForTimeout(600);
  let r = await probe(page);
  check('顶栏时间', r.time === '星穹历 17:43', r.time);
  check('轮次', r.turn === '016', r.turn);
  check('NPC 进度 1 / 5', r.progress === '1 / 5', r.progress);
  check('桌面端每页 3 个标签', r.tabs.length === 3, JSON.stringify(r.tabs));
  check('NPC 立绘 URL', r.npcImg === 'https://meimoaiimg.com/user/1462820/橘诗夜-学园校服.png', r.npcImg);
  await page.click('[data-gal-npc-next]');
  let r2 = await probe(page);
  check('翻页看到后 2 个', JSON.stringify(r2.tabs) === '["朝雾纱良","雾岛遥"]', JSON.stringify(r2.tabs));
  await page.click('[data-gal-npc-prev]');
  check('附近地点 3 个', r.nearby.length === 3, JSON.stringify(r.nearby));
  check('行动 3 个', r.actions.length === 3, JSON.stringify(r.actions));

  // ---- 2. STREAMING: re-parse innerHTML on every chunk ----
  console.log('\n[2] 流式逐字输出（AI 正文，整段重解析）');
  await page.goto('https://gal.test/');
  const full = build(badStatus);
  await page.evaluate(async h => {
    const chat = document.getElementById('chat');
    for (let i = 40; i <= h.length; i += 37) {
      chat.innerHTML = h.slice(0, i);
      await new Promise(r => setTimeout(r, 0));
    }
    chat.innerHTML = h;
  }, full);
  await page.waitForTimeout(900);
  r = await probe(page);
  check('顶栏时间', r.time === '四月上旬 · 星期一 · 早晨8:20', r.time);
  check('事件标题', r.event === '入学第一天，迎新流程进行中', r.event);
  check('NPC 进度 1 / 1', r.progress === '1 / 1', r.progress);
  check('NPC 标签 = 五堂爱', JSON.stringify(r.tabs) === '["五堂爱"]', JSON.stringify(r.tabs));
  check('NPC 名', r.npcName === '五堂爱', r.npcName);
  check('NPC 身份', r.npcField0 === '一年E班学生·迎新委员', r.npcField0);
  check('NPC 立绘已加载', /meimoaiimg\.com/.test(r.npcImg || ''), r.npcImg);
  check('私密好感', r.favor === '初见好感·礼貌的新同学', r.favor);
  check('徽章', JSON.stringify(r.badges) === '["天生魔女（世间唯二之一）","一年级新生","一年D班"]', JSON.stringify(r.badges));

  // ---- 3. STREAMING: incremental patch (img created once, raw filled later) ----
  console.log('\n[3] 流式增量 patch（img 只创建一次、raw 后到 —— 旧版的真实死法）');
  await page.goto('https://gal.test/');
  await page.evaluate(async ([htmlPrefix, fullHtml]) => {
    const chat = document.getElementById('chat');
    chat.innerHTML = htmlPrefix + '</div></div>';          // 骨架+img 先到，raw 空
    const raw = chat.querySelector('.gal-status-raw');
    const box = document.createElement('div');
    box.innerHTML = fullHtml;
    const src = box.querySelector('.gal-status-raw');
    const kids = [...src.childNodes];
    for (const k of kids) {                                // <div protocol> <div top> ... 逐块到达
      if (k.nodeType === 1) {                              // 元素再逐字填文本，模拟真实流式
        const txt = k.textContent; k.textContent = '';
        raw.appendChild(k);
        for (let i = 0; i < txt.length; i += 25) {
          k.textContent = txt.slice(0, i + 25);
          await new Promise(r => setTimeout(r, 5));
        }
      } else { raw.appendChild(k); }
      await new Promise(r => setTimeout(r, 10));
    }
  }, [HTML, build(okStatus)]);
  await page.waitForTimeout(900);
  r = await probe(page);
  check('增量 patch 下顶栏时间', r.time === '星穹历 17:43', r.time);
  check('增量 patch 下 NPC 进度', r.progress === '1 / 5', r.progress);
  check('增量 patch 下 NPC 标签', r.tabs.length === 3, JSON.stringify(r.tabs));
  check('增量 patch 下立绘', /meimoaiimg/.test(r.npcImg || ''), r.npcImg);

  // ---- 3b. 手机视口：滑动列表应列出全部 NPC ----
  console.log('\n[3b] 手机视口 430px 的 NPC 滑动列表');
  await page.setViewportSize({ width: 430, height: 900 });
  await page.waitForTimeout(400);
  r = await probe(page);
  check('手机端列出全部 5 个 NPC', r.tabs.length === 5, JSON.stringify(r.tabs));
  check('手机端箭头隐藏', await page.evaluate(() => getComputedStyle(document.querySelector('[data-gal-npc-next]')).display === 'none'));
  await page.setViewportSize({ width: 900, height: 900 });
  await page.waitForTimeout(300);

  // ---- 4. interaction ----
  console.log('\n[4] NPC 切换 / 私密信息 / 行动注入');
  await page.click('.gal-status-npc-tab:nth-child(3)');
  r = await probe(page);
  check('切到第 3 个 NPC', r.npcName === '白夜凛' && r.progress === '3 / 5', r.npcName + ' ' + r.progress);
  check('切换后立绘跟随', /(白夜凛|%E7%99%BD%E5%A4%9C%E5%87%9B)-/.test(r.npcImg || ''), r.npcImg);
  await page.click('.gal-status-secret');
  check('私密信息可展开', await page.evaluate(() => document.querySelector('.gal-status-secret').classList.contains('is-revealed')));
  await page.click('.gal-status-action');
  check('行动写入输入框',
    (await page.inputValue('textarea')) === '[行动指令：询问橘诗夜关于星盘异常的细节]',
    await page.inputValue('textarea'));
  await page.click('[data-gal-nearby] .gal-status-scene-option');
  check('地点写入输入框',
    (await page.inputValue('textarea')) === '[行动指令：前往星穹回廊]',
    await page.inputValue('textarea'));

  // ---- 5. empty NPC ----
  console.log('\n[5] 无 NPC 时');
  await page.goto('https://gal.test/');
  await page.evaluate(h => { document.getElementById('chat').innerHTML = h; },
    build(okStatus.replace(/<div npc>[\s\S]*?<\/div>/, '<div npc>\n</div>')));
  await page.waitForTimeout(500);
  r = await probe(page);
  check('进度 0 / 0', r.progress === '0 / 0', r.progress);
  check('NPC 面板真的隐藏了（原来被 display:grid 顶掉）', r.bodyDisplay === 'none', r.bodyDisplay);

  // ---- 6. USER portrait persistence ----
  console.log('\n[6] USER 立绘上传 + 跨回合继承');
  await page.goto('https://gal.test/');
  await page.evaluate(h => { document.getElementById('chat').innerHTML = h; }, build(okStatus));
  await page.waitForTimeout(400);
  const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==', 'base64');
  await page.setInputFiles('[data-gal-user-upload]', { name: 'u.png', mimeType: 'image/png', buffer: png });
  await page.waitForTimeout(600);
  check('上传后本回合显示立绘', (await probe(page)).userHasImage);
  check('已写入 localStorage', await page.evaluate(() => !!localStorage.getItem('galStatusUserPortrait')));
  await page.evaluate(h => { document.getElementById('chat').insertAdjacentHTML('beforeend', h); }, build(badStatus));
  await page.waitForTimeout(800);
  const inherited = await page.evaluate(() => {
    const shells = document.querySelectorAll('.gal-status-shell');
    const last = shells[shells.length - 1];
    return { count: shells.length,
      has: last.querySelector('.gal-status-user-portrait').classList.contains('has-image'),
      progress: last.querySelector('[data-gal-npc-progress]').textContent };
  });
  check('下一回合状态栏继承 USER 立绘', inherited.has, JSON.stringify(inherited));
  check('新旧两条状态栏共存且新的也解析了', inherited.count === 2 && inherited.progress === '1 / 1', JSON.stringify(inherited));
  await page.reload();
  await page.evaluate(h => { document.getElementById('chat').innerHTML = h; }, build(okStatus));
  await page.waitForTimeout(700);
  check('刷新页面后仍继承', (await probe(page)).userHasImage);
  await page.click('[data-gal-user-clear]');
  await page.waitForTimeout(300);
  check('清除按钮生效', !(await probe(page)).userHasImage);
  check('清除后 localStorage 也清了', await page.evaluate(() => !localStorage.getItem('galStatusUserPortrait')));

  // ---- 7. tolerance ----
  console.log('\n[7] 容错');
  const messy = okStatus
    .replace('林深月::立绘=林深月_学园校服|', '林深月::立绘=林深月_学园校服 |')
    .replace('weather::薄雨后的星尘雾;;', 'weather：：薄雨后的星尘雾；；');
  await page.goto('https://gal.test/');
  await page.evaluate(h => { document.getElementById('chat').innerHTML = h; }, build(messy));
  await page.waitForTimeout(500);
  r = await probe(page);
  check('全角 ：： ；； 仍能解析', r.progress === '1 / 5' && r.tabs.length === 3 && r.weather === '薄雨后的星尘雾', r.progress + ' / 天气=' + r.weather);
  await page.click('.gal-status-npc-tab:nth-child(2)');
  r = await probe(page);
  check('立绘尾空格不再产生坏 URL', !/(%20|\s)\.png/.test(r.npcImg || ''), r.npcImg);
  await page.goto('https://gal.test/');
  await page.evaluate(h => { document.getElementById('chat').innerHTML = h; },
    okStatus.replace('<status>', HTML).replace('</status>', '</div></div>'));
  await page.waitForTimeout(500);
  r = await probe(page);
  check('正则未生效时 JS 兜底拼图床链接', /meimoaiimg\.com\/user\/1462820\/%E6%A9%98%E8%AF%97%E5%A4%9C-%E5%AD%A6%E5%9B%AD%E6%A0%A1%E6%9C%8D\.png/.test(r.npcImg || ''), r.npcImg);
  await page.goto('https://gal.test/');
  await page.evaluate(h => { document.getElementById('chat').innerHTML = h; },
    build(okStatus.replace(/可互动点=询问星盘异常;;/, '可互动点=询问星盘异常')));
  await page.waitForTimeout(500);
  r = await probe(page);
  check('漏写 ;; 时靠换行兜底', r.progress === '1 / 5' && r.npcField8 === '询问星盘异常', r.progress + ' / ' + r.npcField8);

  // ---- 8. regex idempotency ----
  const once = okStatus.replace(new RegExp(PORTRAIT.source, 'g'), '立绘=https://meimoaiimg.com/user/1462820/$1-$2.png');
  const twice = once.replace(new RegExp(PORTRAIT.source, 'g'), '立绘=https://meimoaiimg.com/user/1462820/$1-$2.png');
  check('正则重复执行不二次转换', once === twice, twice.match(/立绘=[^|]*/)[0]);

  await ctx.newPage();
  await browser.close();
  const failed = results.filter(r => !r.pass);
  console.log(`\n=== ${results.length - failed.length}/${results.length} passed ===`);
  if (failed.length) { console.log('FAILED:', failed.map(f => f.name).join(' | ')); process.exit(1); }
})();
