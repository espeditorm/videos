// ---------- praia no Havaí (cenário do ator), tudo em coordenadas do mundo ----------
const HORIZON = -40, SHORE = 120;
const BEACH_CLOUDS = (() => { const r = rng(73), a = []; for (let i = 0; i < 9; i++) a.push({ x: -1800 + r() * 3600, y: -900 + r() * 520, w: 160 + r() * 260, v: 6 + r() * 10 }); return a; })();
function palm(x, y, sc, a, ph) {
  ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc);
  const sway = .05 * Math.sin(a * .9 + ph);
  // tronco curvo em segmentos arredondados
  let px = 0, py = 0, ang = -Math.PI / 2 + .18 + sway * .5;
  for (let i = 0; i < 9; i++) {
    ctx.save(); ctx.translate(px, py); ctx.rotate(ang + Math.PI / 2);
    ctx.fillStyle = i % 2 ? '#b97a50' : '#c98a5e'; ctx.beginPath(); ctx.roundRect(-17 + i, -54, 34 - i * 2, 58, 14); ctx.fill();
    ctx.restore();
    px += Math.cos(ang) * 50; py += Math.sin(ang) * 50; ang -= .035;
  }
  // folhas
  ctx.translate(px, py);
  for (let k = 0; k < 7; k++) {
    const base = -Math.PI / 2 + (k - 3) * .52 + sway * 2;
    ctx.save(); ctx.rotate(base);
    ctx.fillStyle = k % 2 ? '#3a9d62' : '#48ad6b';
    ctx.beginPath(); ctx.ellipse(120, 18, 130, 30, .35, 0, 6.283); ctx.fill();
    ctx.restore();
  }
  ctx.fillStyle = '#7a5235';
  for (const [cx, cy] of [[-14, 14], [12, 18], [0, 30]]) { ctx.beginPath(); ctx.arc(cx, cy, 15, 0, 6.283); ctx.fill(); }
  ctx.restore();
}
function drawBeach(a) {
  screenSpace(); ctx.fillStyle = '#2d8fd0'; ctx.fillRect(0, 0, W, H);
  applyCam();
  // céu de manhã
  const sky = ctx.createLinearGradient(0, -1600, 0, HORIZON);
  sky.addColorStop(0, '#1a66b8'); sky.addColorStop(.6, '#4dc7eb'); sky.addColorStop(1, '#ffe3a8');
  ctx.fillStyle = sky; ctx.fillRect(-4000, -3000, 8000, 3000 + HORIZON + 2);
  // sol baixo da manhã: só brilho suave, sem raios
  const sg = ctx.createRadialGradient(900, -170, 0, 900, -170, 520);
  sg.addColorStop(0, 'rgba(255,247,220,.95)'); sg.addColorStop(.18, 'rgba(255,217,138,.55)'); sg.addColorStop(1, 'rgba(255,217,138,0)');
  ctx.fillStyle = sg; ctx.beginPath(); ctx.arc(900, -170, 520, 0, 6.283); ctx.fill();
  ctx.fillStyle = '#fff7dc'; ctx.beginPath(); ctx.arc(900, -170, 70, 0, 6.283); ctx.fill();
  // nuvens em cápsula que andam
  for (const c of BEACH_CLOUDS) {
    let x = ((c.x + a * c.v + 2000) % 4000) - 2000;
    ctx.fillStyle = 'rgba(255,255,255,.9)';
    ctx.beginPath(); ctx.roundRect(x - c.w / 2, c.y, c.w, 44, 22); ctx.fill();
    ctx.beginPath(); ctx.roundRect(x - c.w / 4, c.y - 26, c.w * .5, 40, 20); ctx.fill();
  }
  // montanha verde ao longe (silhueta de cratera)
  ctx.fillStyle = '#5aa88a';
  ctx.beginPath(); ctx.moveTo(-1700, HORIZON + 2); ctx.bezierCurveTo(-1400, -300, -1150, -330, -980, -250); ctx.bezierCurveTo(-880, -210, -760, -120, -560, HORIZON + 2); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#4b9a7c';
  ctx.beginPath(); ctx.moveTo(-1250, HORIZON + 2); ctx.bezierCurveTo(-1150, -160, -1000, -190, -900, -150); ctx.bezierCurveTo(-820, -110, -760, -70, -680, HORIZON + 2); ctx.closePath(); ctx.fill();
  // mar
  const sea = ctx.createLinearGradient(0, HORIZON, 0, SHORE);
  sea.addColorStop(0, '#1a66b8'); sea.addColorStop(1, '#4dc7eb');
  ctx.fillStyle = sea; ctx.fillRect(-4000, HORIZON, 8000, SHORE - HORIZON + 10);
  // faixas de brilho na água
  for (let i = 0; i < 14; i++) {
    const y = HORIZON + 12 + i * 11, w = 120 + (i * 37) % 160, x = ((i * 523 + a * (10 + i)) % 3200) - 1600;
    ctx.fillStyle = `rgba(255,255,255,${.12 + .1 * Math.sin(a * 1.3 + i)})`; ctx.beginPath(); ctx.roundRect(x, y, w, 4, 2); ctx.fill();
  }
  // reflexo do sol
  ctx.fillStyle = 'rgba(255,240,200,.35)';
  for (let i = 0; i < 6; i++) { const y = HORIZON + 10 + i * 18; ctx.beginPath(); ctx.roundRect(900 - 60 + 10 * Math.sin(a * 2 + i), y, 120 - i * 10, 5, 3); ctx.fill(); }
  // areia molhada e espuma que vai e vem
  const surf = 14 * Math.sin(a * .8);
  ctx.fillStyle = '#e8b64f'; ctx.fillRect(-4000, SHORE - 6, 8000, 3000);
  ctx.fillStyle = '#f5c75f'; ctx.fillRect(-4000, SHORE + 24 + surf * .5, 8000, 3000);
  ctx.fillStyle = 'rgba(255,255,255,.85)';
  ctx.beginPath(); ctx.moveTo(-4000, SHORE - 10);
  for (let x = -4000; x <= 4000; x += 80) ctx.lineTo(x, SHORE - 2 + surf + 8 * Math.sin(x * .012 + a * 1.4));
  ctx.lineTo(4000, SHORE - 14); ctx.closePath(); ctx.fill();
  // pintas na areia
  const r = rng(19);
  for (let i = 0; i < 60; i++) { ctx.fillStyle = 'rgba(201,138,94,.25)'; ctx.beginPath(); ctx.ellipse(-1600 + r() * 3200, SHORE + 60 + r() * 500, 8 + r() * 10, 3 + r() * 3, 0, 0, 6.283); ctx.fill(); }
  // coqueiros e sombra do personagem
  palm(-640, 230, 1.05, a, 0); palm(760, 260, .9, a, 2);
  ctx.save(); ctx.scale(-1, 1); palm(-1100, 200, .8, a, 4); ctx.restore();
  ctx.fillStyle = 'rgba(122,82,53,.35)'; ctx.beginPath(); ctx.ellipse(MAN.x + 30, MAN.y + 4, 130, 18, 0, 0, 6.283); ctx.fill();
}
