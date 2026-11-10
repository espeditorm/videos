// ---------- grão e vinheta ----------
const GRAIN = [];
(function () {
  for (let k = 0; k < 6; k++) {
    const c = document.createElement('canvas'); c.width = 512; c.height = 512;
    const g = c.getContext('2d'), d = g.createImageData(512, 512), r = rng(1000 + k);
    for (let i = 0; i < 512 * 512; i++) { const v = r() * 255; d.data[i * 4] = d.data[i * 4 + 1] = d.data[i * 4 + 2] = v; d.data[i * 4 + 3] = 255; }
    g.putImageData(d, 0, 0); GRAIN.push(c);
  }
})();
function finish(t) {
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * .35, W / 2, H / 2, H * 1.05);
  vg.addColorStop(0, 'rgba(4,4,20,0)'); vg.addColorStop(1, 'rgba(4,4,20,.45)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  const k = Math.floor(t * 24), r = rng(k * 7 + 3);
  ctx.save(); ctx.globalAlpha = .06; ctx.globalCompositeOperation = 'overlay';
  const tile = GRAIN[((k % GRAIN.length) + GRAIN.length) % GRAIN.length], ox = -Math.floor(r() * 512), oy = -Math.floor(r() * 512);
  for (let y = oy; y < H; y += 512) for (let x = ox; x < W; x += 512) ctx.drawImage(tile, x, y);
  ctx.restore();
}
