// =====================================================================
//  lib_char.js: personagem humano estilizado (proporção de cabeça grande, tronco em "feijão",
//  braços em tubo curvo com cotovelo por cinemática inversa, mãos com dedos, volume por degradê e luz de borda)
//  Sem contornos: todo volume vem de preenchimentos. Pés em (x, y); altura ~340 em sc = 1.
// =====================================================================
const CH = {
  skin: '#f2b58f', skinSh: '#d98f6c', blush: 'rgba(255,110,130,.35)',
  hair: '#3b2a4a', hairHi: '#6a4a8a', shirt: '#1fa3a8', shirtSh: '#147a86',
  pants: '#2b3346', pantsSh: '#1d2433', shoe: '#ff8f4a', rim: 'rgba(255,236,190,.5)'
};
function shade(hex, k) {   // escurece (k<0) ou clareia (k>0) uma cor #rrggbb
  const n = parseInt(hex.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  const f = c => Math.round(k < 0 ? c * (1 + k) : c + (255 - c) * k);
  return `rgb(${f(r)},${f(g)},${f(b)})`;
}
// preenche um caminho com volume: degradê (luz em cima à esquerda) + faixa de luz de borda no lado iluminado
function volume(path, base, bb, rim = CH.rim, rimW = 5) {
  const [x0, y0, x1, y1] = bb;
  ctx.save(); path(); ctx.clip();
  ctx.fillStyle = rim; ctx.fillRect(x0 - 20, y0 - 20, x1 - x0 + 40, y1 - y0 + 40);
  const g = ctx.createLinearGradient(x0, y0, x1, y1);
  g.addColorStop(0, shade(base, .12)); g.addColorStop(.55, base); g.addColorStop(1, shade(base, -.22));
  ctx.translate(rimW, rimW * .8); path(); ctx.fillStyle = g; ctx.fill();
  ctx.restore();
}
function tube(p, c, q, w0, w1, col, light = true) {
  // tubo que afina de w0 a w1, curvo (quadrática p -> q com controle c), desenhado em fatias
  const N = 14;
  for (let pass = 0; pass < (light ? 2 : 1); pass++) {
    for (let i = 0; i <= N; i++) {
      const u = i / N, x = (1 - u) * (1 - u) * p.x + 2 * (1 - u) * u * c.x + u * u * q.x, y = (1 - u) * (1 - u) * p.y + 2 * (1 - u) * u * c.y + u * u * q.y;
      const w = lerp(w0, w1, u);
      ctx.fillStyle = pass === 0 ? shade(col, -.18) : col;
      ctx.beginPath(); ctx.arc(x - (pass ? 2 : 0), y - (pass ? 2 : 0), w / 2 - (pass ? 2 : 0), 0, 6.283); ctx.fill();
    }
  }
}
// mão em mitene com dedos curtos. pose: relax | aberta | punho | aponta | joinha | pare
function hand2(wr, ang, pose, th, skin) {
  // mão sem dedos: uma ponta arredondada, com um leve brilho
  ctx.save(); ctx.translate(wr.x, wr.y); ctx.rotate(ang);
  const r = pose === 'punho' ? 15 : 13;
  ctx.fillStyle = shade(skin, -.15); ctx.beginPath(); ctx.arc(6, 1.5, r, 0, 6.283); ctx.fill();
  ctx.fillStyle = skin; ctx.beginPath(); ctx.arc(5, 0, r - 1.5, 0, 6.283); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,.25)'; ctx.beginPath(); ctx.ellipse(2, -5, 5, 3, -.4, 0, 6.283); ctx.fill();
  ctx.restore();
}
// braço: ombro -> alvo com cotovelo (IK de 2 ossos) desenhado como tubo curvo; devolve o punho
function arm2(sh, tgt, L1, L2, bend, sleeve, long, pose, th, skin) {
  const dx = tgt.x - sh.x, dy = tgt.y - sh.y, d = Math.min(Math.hypot(dx, dy), L1 + L2 - .5), a0 = Math.atan2(dy, dx);
  const b = Math.acos(clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1));
  const el = { x: sh.x + Math.cos(a0 + bend * b) * L1, y: sh.y + Math.sin(a0 + bend * b) * L1 };
  const wr = { x: sh.x + Math.cos(a0) * d, y: sh.y + Math.sin(a0) * d };
  const mid = { x: lerp(sh.x, el.x, .5), y: lerp(sh.y, el.y, .5) };
  // antebraço (pele ou manga) e braço (manga), com a curva passando pelo cotovelo
  tube(el, { x: lerp(el.x, wr.x, .5), y: lerp(el.y, wr.y, .5) }, wr, 24, 18, long ? sleeve : skin);
  tube(sh, mid, el, 32, 26, sleeve);
  if (!long) tube({ x: lerp(sh.x, el.x, .6), y: lerp(sh.y, el.y, .6) }, el, el, 22, 22, skin);
  const fa = Math.atan2(wr.y - el.y, wr.x - el.x);
  hand2(wr, fa, pose, th, skin);
  return wr;
}
// ---------------------------------------------------------------------
//  pessoa
// ---------------------------------------------------------------------
function drawPerson(x, y, sc, s, a, o = {}) {
  const P = { ...CH, ...(o.pal || {}) };
  let sq = 0; for (const k of (o.kicks || [])) sq += kick(s - k, .45, 13) * .12;
  sq += o.deflate || 0;
  const bob = 4 * Math.sin(a * 1.6), sx = 1 + sq * .8, sy = 1 - sq;
  ctx.save(); ctx.translate(x, y); ctx.scale(sc * sx, sc * sy); ctx.translate(0, -bob);
  const look = o.look ? { x: clamp((o.look.x - x) / 400, -1, 1), y: clamp((o.look.y - (y - 300 * sc)) / 400, -1, 1) } : { x: 0, y: 0 };
  // pernas curtas e sapatos
  if (!o.sit) {
    for (const dd of [-1, 1]) {
      const leg = () => { ctx.beginPath(); ctx.moveTo(dd * 25 - 21, -96); ctx.lineTo(dd * 25 + 21, -96); ctx.bezierCurveTo(dd * 25 + 20, -50, dd * 25 + 16, -10, dd * 25, -4); ctx.bezierCurveTo(dd * 25 - 16, -10, dd * 25 - 20, -50, dd * 25 - 21, -96); ctx.closePath(); };
      volume(leg, P.pants, [dd * 25 - 21, -96, dd * 25 + 21, -4], 'rgba(255,255,255,.14)', 3);
    }
  }
  // tronco em "feijão": ombros estreitos, base larga e arredondada
  const torso = () => { ctx.beginPath(); ctx.moveTo(0, -266); ctx.bezierCurveTo(-46, -266, -66, -248, -68, -206); ctx.bezierCurveTo(-72, -150, -78, -98, -58, -78); ctx.bezierCurveTo(-36, -62, 36, -62, 58, -78); ctx.bezierCurveTo(78, -98, 72, -150, 68, -206); ctx.bezierCurveTo(66, -248, 46, -266, 0, -266); ctx.closePath(); };
  // braço de trás (esquerdo do personagem) antes do tronco
  const armSw = .1 * Math.sin(a * 1.2);
  const lT = o.reachL || { x: -92 - 30 * armSw, y: -112 };
  arm2({ x: -58, y: -232 }, lT, 64, 62, -1, P.shirt, !!o.longSleeve, o.handL || 'relax', -1, P.skin);
  volume(torso, P.shirt, [-78, -266, 78, -64], P.rim, 4);
  if (o.pattern) { ctx.save(); torso(); ctx.clip(); o.pattern(); ctx.restore(); }
  // gola e pescoço curto
  ctx.fillStyle = shade(P.skin, -.1); ctx.beginPath(); ctx.roundRect(-16, -272, 32, 22, 10); ctx.fill();
  ctx.fillStyle = shade(P.shirt, -.3); ctx.beginPath(); ctx.ellipse(0, -258, 30, 9, 0, 0, Math.PI); ctx.fill();
  // cabeça grande
  const hx = look.x * 5, hy = -330 + look.y * 3;
  ctx.save(); ctx.translate(hx, hy); ctx.rotate(look.x * .05 + (o.headTilt || 0));
  ctx.fillStyle = P.skin; ctx.beginPath(); ctx.ellipse(-60, 8, 12, 15, 0, 0, 6.283); ctx.ellipse(60, 8, 12, 15, 0, 0, 6.283); ctx.fill();
  volume(() => { ctx.beginPath(); ctx.ellipse(0, 0, 62, 68, 0, 0, 6.283); }, P.skin, [-62, -68, 62, 68], CH.rim, 5);
  // cabelo volumoso com mechas de luz
  if (!o.bald) {
    const hairP = () => { ctx.beginPath(); ctx.moveTo(-70, 18); ctx.bezierCurveTo(-82, -60, -34, -92, 6, -88); ctx.bezierCurveTo(56, -86, 82, -52, 70, 14); ctx.bezierCurveTo(64, -10, 54, -22, 44, -26); ctx.lineTo(-44, -26); ctx.bezierCurveTo(-56, -20, -64, -6, -70, 18); ctx.closePath(); };
    volume(hairP, P.hair, [-82, -92, 82, 18], P.hairHi, 4);
    // franja: mechas arredondadas sobre a testa
    for (const [fx, fw, fh, rot] of [[-48, 34, 30, -.25], [-20, 36, 34, -.1], [10, 34, 30, .12], [36, 28, 24, .3]]) {
      ctx.save(); ctx.translate(fx + fw / 2, -30); ctx.rotate(rot); ctx.fillStyle = P.hair; ctx.beginPath(); ctx.roundRect(-fw / 2, -12, fw, fh, [6, 6, fw / 2, fw / 2]); ctx.fill(); ctx.restore();
    }
    ctx.fillStyle = P.hairHi; for (const [hx2, hy2, w2, r2] of [[-38, -70, 30, -.3], [2, -78, 26, 0], [34, -64, 20, .35]]) { ctx.save(); ctx.translate(hx2, hy2); ctx.rotate(r2); ctx.beginPath(); ctx.roundRect(0, 0, w2, 7, 3.5); ctx.fill(); ctx.restore(); }
  }
  // rosto: olhos escuros com brilho, sobrancelhas, nariz, bochechas, boca
  const bl = blink(a, .3), ex = look.x * 7, ey = look.y * 5, w = o.worry || 0;
  ctx.fillStyle = P.blush; ctx.beginPath(); ctx.ellipse(-36, 26, 13, 8, 0, 0, 6.283); ctx.ellipse(36, 26, 13, 8, 0, 0, 6.283); ctx.fill();
  for (const dd of [-1, 1]) {
    const eh = 17 * (1 - bl * .92) * (o.relief ? .3 : 1) * (1 + w * .12);
    ctx.fillStyle = '#241a33'; ctx.beginPath(); ctx.ellipse(dd * 24 + ex * .6, 2 + ey * .6, 13, eh, 0, 0, 6.283); ctx.fill();
    if (eh > 6) { ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.arc(dd * 24 + ex * .6 - 4, -4 + ey * .6, 4.5, 0, 6.283); ctx.fill(); ctx.beginPath(); ctx.arc(dd * 24 + ex * .6 + 4, 7 + ey * .6, 2, 0, 6.283); ctx.fill(); }
    ctx.save(); ctx.translate(dd * 24, -24 - w * 5); ctx.rotate(dd * -w * .35 + (o.relief ? dd * .15 : 0));
    ctx.fillStyle = shade(P.hair, -.1); ctx.beginPath(); ctx.roundRect(-11, -3.5, 22, 7, 3.5); ctx.fill(); ctx.restore();
  }
  ctx.fillStyle = shade(P.skin, -.12); ctx.beginPath(); ctx.ellipse(2, 18, 6, 8, 0, 0, 6.283); ctx.fill();
  ctx.fillStyle = '#9a3b4a';
  if (o.relief || o.smile) { ctx.beginPath(); ctx.ellipse(0, 38, 13, 7, 0, 0, Math.PI); ctx.fill(); }
  else if (w > .5) { ctx.beginPath(); ctx.ellipse(0, 40, 7, 9 * w, 0, 0, 6.283); ctx.fill(); }
  else { ctx.beginPath(); ctx.roundRect(-8, 36, 16, 5, 2.5); ctx.fill(); }
  ctx.restore();
  // braço da frente (direito do personagem): alcança o.reach (mundo) ou levanta o celular
  const up = o.phoneUp ?? 0;
  let hand = { x: lerp(94, 74, up) + 30 * armSw * (1 - up), y: lerp(-112, -300, up) };
  if (o.reach) { const ww = o.reachW ?? 1; const lx = (o.reach.x - x) / (sc * sx), ly = (o.reach.y - y) / (sc * sy) + bob; hand = { x: lerp(hand.x, lx, ww), y: lerp(hand.y, ly, ww) }; }
  hand = arm2({ x: 58, y: -232 }, hand, 64, 62, 1, P.shirt, !!o.longSleeve, o.handR || (up > .3 || o.reach ? 'punho' : 'relax'), 1, P.skin);
  ctx.restore();
  return { x: x + hand.x * sc * sx, y: y + (hand.y - bob) * sc * sy };
}
