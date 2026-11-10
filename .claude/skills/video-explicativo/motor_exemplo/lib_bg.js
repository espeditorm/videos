// ---------- fundo: nebulosas e estrelas ----------
const NEB = [
  { x: -500, y: -300, r: 1100, c: [24, 150, 160], a: .20, d: .05 },
  { x: 700, y: 250, r: 1200, c: [40, 95, 195], a: .16, d: .08 },
  { x: -200, y: 450, r: 900, c: [220, 95, 110], a: .10, d: .1 },
  { x: 1100, y: -400, r: 1000, c: [60, 70, 175], a: .15, d: .06 },
  { x: -1300, y: 200, r: 1000, c: [24, 150, 160], a: .14, d: .09 }
];
const STAR_LAYERS = [.12, .35, .6].map((d, li) => {
  const r = rng(77 + li * 31), n = [420, 240, 120][li], arr = [];
  for (let i = 0; i < n; i++) arr.push({
    x: r() * 2400, y: r() * 1500, s: [0.9, 1.4, 2.1][li] * (.6 + r() * .8),
    ph: r() * 6.28, f: .6 + r() * 2.2, sp: li === 2 && r() < .4, hue: r()
  });
  return { d, arr };
});
function drawBackground(a, dim) {
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#081d2c'); g.addColorStop(1, '#102348');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (const n of NEB) {
    const k = Math.pow(CAM.z, n.d * 2);
    const x = W / 2 + (n.x - CAM.x * n.d) * k * .9 + 40 * Math.sin(a * .05 + n.x);
    const y = H / 2 + (n.y - CAM.y * n.d) * k * .9 + 30 * Math.cos(a * .04 + n.y);
    const rg = ctx.createRadialGradient(x, y, 0, x, y, n.r * k);
    rg.addColorStop(0, `rgba(${n.c},${n.a})`); rg.addColorStop(.55, `rgba(${n.c},${n.a * .45})`); rg.addColorStop(1, `rgba(${n.c},0)`);
    ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
  }
  for (const L of STAR_LAYERS) {
    const k = Math.pow(CAM.z, L.d * .6);
    for (const p of L.arr) {
      let x = ((p.x - CAM.x * L.d * CAM.z * .35) * k) % 2400; if (x < 0) x += 2400; x -= 240;
      let y = ((p.y - CAM.y * L.d * CAM.z * .35) * k) % 1500; if (y < 0) y += 1500; y -= 210;
      if (x < -20 || x > W + 20 || y < -20 || y > H + 20) continue;
      const tw = .55 + .45 * Math.sin(a * p.f + p.ph);
      const al = (.35 + .65 * tw) * (L.d === .6 ? .95 : L.d === .35 ? .75 : .5);
      const col = p.hue < .7 ? '255,255,255' : p.hue < .85 ? '170,230,255' : '255,225,170';
      if (p.sp) {
        const s = p.s * (2.2 + 1.6 * tw);
        ctx.fillStyle = `rgba(${col},${al})`;
        ctx.beginPath();
        ctx.moveTo(x, y - s * 2); ctx.quadraticCurveTo(x, y, x + s * 2, y); ctx.quadraticCurveTo(x, y, x, y + s * 2);
        ctx.quadraticCurveTo(x, y, x - s * 2, y); ctx.quadraticCurveTo(x, y, x, y - s * 2); ctx.fill();
      } else {
        ctx.fillStyle = `rgba(${col},${al})`;
        ctx.beginPath(); ctx.arc(x, y, p.s * (.8 + .3 * tw), 0, 6.283); ctx.fill();
      }
    }
  }
  ctx.restore();
}
