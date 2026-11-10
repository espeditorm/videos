// Render: node render.js worker nworkers -> chunks/part_<w>.mkv (lossless)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async () => {
  const w = +process.argv[2], nw = +process.argv[3], total = Math.round(62.5 * 30);
  const per = Math.ceil(total / nw), f0 = w * per, f1 = Math.min(total, f0 + per);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.error('pageerror', e.message));
  await p.goto('file://' + __dirname + '/video.html');
  await p.waitForFunction(() => window.READY === true, null, { timeout: 60000 });
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'ultrafast', `chunks/part_${w}.mkv`], { stdio: ['pipe', 'inherit', 'inherit'] });
  const c = p.locator('#c'); const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    await p.evaluate(i => window.renderFrame(i), f);
    const buf = await c.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 50 === 0) console.log(`w${w} ${f - f0}/${f1 - f0} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  console.log(`w${w} done`); await b.close();
})();
