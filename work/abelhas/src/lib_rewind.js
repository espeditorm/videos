// ---------- rewind ----------
function drawRewindFX(t) {
  const u = (t - RW0) / .8; if (u < 0 || u > 1.15) return;
  const k = Math.sin(Math.PI * clamp(u));
  ctx.save();
  // faixas deslocadas
  const r = rng(Math.floor(t * 30) + 9);
  for (let i = 0; i < 7; i++) {
    const y = r() * H, h = 8 + r() * 40, dx = (r() - .5) * 90 * k;
    ctx.drawImage(cv, 0, y, W, h, dx, y, W, h);
  }
  ctx.fillStyle = `rgba(143,216,230,${.08 * k})`; ctx.fillRect(0, 0, W, H);
  // ícone de voltar (dois triângulos)
  ctx.globalAlpha = k; ctx.fillStyle = '#ffffff';
  for (const ox of [0, 56]) { ctx.beginPath(); ctx.moveTo(150 + ox, 110); ctx.lineTo(206 + ox, 76); ctx.lineTo(206 + ox, 144); ctx.closePath(); ctx.fill(); }
  ctx.restore();
}

