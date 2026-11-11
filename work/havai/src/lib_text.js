// ---------- texto ----------
const FONT = (w, px) => `${w} ${px}px Fredoka`;
const COL = { teal: '#8fd8e6', gold: '#ffd98a', white: '#ffffff', coral: '#ff8a7a' };
// linha que sobe 1,3x a própria altura através de um recorte (ease-out-quint)
function riseText(str, x, y, px, color, t, t0, t1 = 1e9, opt = {}) {
  if (t < t0 || t > t1 + .6) return 0;
  ctx.save();
  ctx.font = FONT(opt.w || 700, px); ctx.letterSpacing = (opt.ls ?? 5) + 'px';
  ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
  const w = ctx.measureText(str).width + (opt.ls ?? 5) * str.length, h = px * 1.15;
  const x0 = opt.align === 'left' ? x : x - w / 2;
  const uIn = easeOutQuint((t - t0) / .55), uOut = easeInCubic((t - t1) / .45);
  const off = (1 - uIn) * h * 1.3 + uOut * h * 1.3;
  ctx.beginPath(); ctx.rect(x0 - 20, y - px * .95, w + 40, h * 1.05); ctx.clip();
  ctx.fillStyle = color; ctx.fillText(str, x0, y + off);
  ctx.restore();
  return w;
}
// pílula arredondada com linhas que sobem
function pill(lines, cx, cy, t, t0, t1 = 1e9, opt = {}) {
  if (window.NO_TEXT) return;   // quadros limpos para miniaturas
  if (t < t0 || t > t1 + .6) return;
  ctx.save();
  const pad = opt.pad ?? 26, gap = opt.gap ?? 10;
  let wmax = 0, htot = 0;
  for (const L of lines) { ctx.font = FONT(L.w || 700, L.px); ctx.letterSpacing = (L.ls ?? 5) + 'px'; wmax = Math.max(wmax, ctx.measureText(L.s).width + (L.ls ?? 5) * (L.s.length - 1)); htot += L.px * 1.12; }
  htot += gap * (lines.length - 1);
  const pw = wmax + pad * 2, ph = htot + pad * 1.3;
  const sIn = spring(t - t0, .5, 15), sOut = 1 - easeInCubic((t - t1) / .5);
  const sc = Math.max(0, sIn * sOut);
  if (sc <= .001) { ctx.restore(); return; }
  ctx.translate(cx, cy); ctx.scale(lerp(.6, 1, sc), lerp(.6, 1, sc));
  ctx.globalAlpha = clamp(sc * 1.4);
  ctx.fillStyle = 'rgba(6,20,40,.62)';
  ctx.beginPath(); ctx.roundRect(-pw / 2, -ph / 2, pw, ph, Math.min(ph / 2, 40)); ctx.fill();
  ctx.globalAlpha = 1;
  ctx.restore();
  let y = cy - htot / 2;
  lines.forEach((L, i) => {
    y += L.px * .88;
    riseText(L.s, cx, y, L.px, L.c || COL.white, t, t0 + .08 + i * .1, t1 - i * .03, { ls: L.ls, w: L.w });
    y += L.px * .24 + gap;
  });
}
