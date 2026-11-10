// Captura quadros específicos: node shot.js out_dir t1 t2 ...
const { chromium } = require('playwright');
(async () => {
  const [out, ...ts] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => m.type() === 'error' && errs.push(m.text()));
  await p.goto('file://' + __dirname + '/video.html');
  await p.waitForFunction(() => window.READY === true || false, null, { timeout: 60000 }).catch(() => {});
  if (errs.length) console.log('ERR', errs.join('\n'));
  const cues = await p.evaluate(() => window.CUES);
  require('fs').writeFileSync(out + '/cues.json', JSON.stringify(cues, null, 1));
  for (const t of ts) {
    const t0 = Date.now();
    await p.evaluate(t => window.renderFrame(Math.round(t * 30)), +t);
    await p.locator('#c').screenshot({ path: `${out}/f_${(+t).toFixed(2).padStart(6, '0')}.png` });
    console.log(t, Date.now() - t0, 'ms');
  }
  if (errs.length) console.log('ERR', errs.join('\n'));
  await b.close();
})();
