// Quadros limpos (sem pílulas) para miniaturas: node thumb_shot.js <projeto> <saida_dir> t1 t2 ...
const { chromium } = require('playwright');
(async () => {
  const [proj, out, ...ts] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + require('path').resolve(proj) + '/video.html');
  await p.waitForFunction(() => window.READY === true, null, { timeout: 60000 });
  await p.evaluate(() => { window.NO_TEXT = true; });
  for (const t of ts) { await p.evaluate(t => window.renderFrame(Math.round(t * 30)), +t); await p.locator('#c').screenshot({ path: `${out}/${proj.replace(/\W/g, '')}_${t}.png` }); }
  await b.close();
})();
