// =====================================================================
//  lib_char.js v4: personagem esguio, cabeça pequena, braços e pernas longos, rosto mínimo,
//  sombra chapada em dois tons (sem degradê, sem contorno), mãos e pés como pontas arredondadas.
//  Pés em (x, y); altura ~360 em sc = 1. Sem dedos e sem sapatos. (v3 de cabeça grande: lib_char_v3_cabecao.js)
// =====================================================================
function shade(hex, k) {
  const n = parseInt(hex.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  const f = c => Math.round(k < 0 ? c * (1 + k) : c + (255 - c) * k);
  return '#' + [f(r), f(g), f(b)].map(v => v.toString(16).padStart(2, '0')).join('');
}
const CH = { skin: '#f2a98a', hair: '#3b2a4a', top: '#1fa3a8', bottom: '#2b3346', accent: '#ff8a7a' };
// dois tons: a forma inteira na cor base, e o lado direito (oposto à luz) num tom mais escuro
function flat2(path, base, splitX = 0, k = -.18) {
  ctx.fillStyle = base; path(); ctx.fill();
  ctx.save(); path(); ctx.clip(); ctx.fillStyle = shade(base, k); ctx.fillRect(splitX, -2000, 2000, 4000); ctx.restore();
}
function limb(p, q, w0, w1, col) {   // membro fino e afilado entre dois pontos, pontas arredondadas
  const a = Math.atan2(q.y - p.y, q.x - p.x), nx = -Math.sin(a), ny = Math.cos(a);
  ctx.fillStyle = col; ctx.beginPath();
  ctx.moveTo(p.x + nx * w0 / 2, p.y + ny * w0 / 2); ctx.lineTo(q.x + nx * w1 / 2, q.y + ny * w1 / 2);
  ctx.arc(q.x, q.y, w1 / 2, a + Math.PI / 2, a - Math.PI / 2, true);
  ctx.lineTo(p.x - nx * w0 / 2, p.y - ny * w0 / 2); ctx.arc(p.x, p.y, w0 / 2, a - Math.PI / 2, a + Math.PI / 2, true);
  ctx.fill();
}
// braço longo com cotovelo (IK de 2 ossos); a mão é uma ponta arredondada
function arm4(sh, tgt, L1, L2, bend, sleeve, longSleeve, skin) {
  const dx = tgt.x - sh.x, dy = tgt.y - sh.y, d = Math.min(Math.hypot(dx, dy), L1 + L2 - .5), a0 = Math.atan2(dy, dx);
  const b = Math.acos(clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1));
  const el = { x: sh.x + Math.cos(a0 + bend * b) * L1, y: sh.y + Math.sin(a0 + bend * b) * L1 };
  const wr = { x: sh.x + Math.cos(a0) * d, y: sh.y + Math.sin(a0) * d };
  limb(el, wr, 13, 11, longSleeve ? sleeve : skin);
  limb(sh, el, 17, 14, sleeve);
  ctx.fillStyle = skin; ctx.beginPath(); ctx.arc(wr.x, wr.y, 9, 0, 6.283); ctx.fill();
  return wr;
}
// cabelo: chanel | coque | curto | topete
function hair4(style, col) {
  const dk = shade(col, -.2);
  ctx.fillStyle = col;
  if (style === 'coque') { ctx.beginPath(); ctx.arc(0, -40, 17, 0, 6.283); ctx.fill(); ctx.beginPath(); ctx.ellipse(0, -10, 27, 24, 0, Math.PI, 0); ctx.fill(); ctx.fillStyle = dk; ctx.beginPath(); ctx.ellipse(10, -12, 16, 14, 0, Math.PI * 1.2, 0); ctx.fill(); }
  else if (style === 'chanel') { ctx.beginPath(); ctx.moveTo(-32, 22); ctx.bezierCurveTo(-40, -30, -18, -40, 2, -40); ctx.bezierCurveTo(28, -40, 40, -24, 32, 22); ctx.lineTo(22, 22); ctx.bezierCurveTo(22, -6, 10, -14, -4, -14); ctx.bezierCurveTo(-18, -12, -22, 2, -22, 22); ctx.closePath(); ctx.fill(); }
  else if (style === 'topete') { ctx.beginPath(); ctx.moveTo(-27, 0); ctx.bezierCurveTo(-34, -30, -10, -46, 14, -40); ctx.bezierCurveTo(32, -36, 34, -18, 27, -4); ctx.bezierCurveTo(14, -18, -10, -16, -27, 0); ctx.fill(); }
  else if (style === 'curto') { ctx.beginPath(); ctx.ellipse(0, -8, 26, 24, 0, Math.PI, 0); ctx.fill(); ctx.fillStyle = dk; ctx.beginPath(); ctx.ellipse(12, -10, 12, 16, 0, Math.PI * 1.3, 0); ctx.fill(); }
}
function drawPerson(x, y, sc, s, a, o = {}) {
  const P = { ...CH, ...(o.pal || {}) };
  let sq = 0; for (const k of (o.kicks || [])) sq += kick(s - k, .45, 13) * .1;
  sq += o.deflate || 0;
  const bob = 3 * Math.sin(a * 1.6), sx = 1 + sq * .6, sy = 1 - sq;
  ctx.save(); ctx.translate(x, y); ctx.scale(sc * sx, sc * sy); ctx.translate(0, -bob);
  const look = o.look ? { x: clamp((o.look.x - x) / 400, -1, 1), y: clamp((o.look.y - (y - 330 * sc)) / 400, -1, 1) } : { x: 0, y: 0 };
  ctx.rotate(o.lean || 0);
  // pernas longas e finas, terminando em ponta arredondada (sem sapatos)
  if (!o.sit) {
    for (const dd of [-1, 1]) {
      const hip = { x: dd * 12, y: -170 }, foot = { x: dd * 18, y: -8 };
      limb(hip, foot, 22, 15, dd > 0 ? shade(P.bottom, -.18) : P.bottom);
    }
  }
  // braço de trás
  const sw = .1 * Math.sin(a * 1.2);
  arm4({ x: -26, y: -262 }, o.reachL || { x: -44 - 25 * sw, y: -146 }, 72, 66, -1, shade(o.dress ? P.skin : P.top, -.12), !!o.longSleeve && !o.dress, shade(P.skin, -.08));
  // tronco esguio; vestido desce até o joelho
  const torso = o.dress
    ? () => { ctx.beginPath(); ctx.moveTo(-24, -270); ctx.lineTo(24, -270); ctx.lineTo(20, -200); ctx.lineTo(44, -96); ctx.lineTo(-44, -96); ctx.lineTo(-20, -200); ctx.closePath(); }
    : () => { ctx.beginPath(); ctx.moveTo(-30, -272); ctx.quadraticCurveTo(-37, -270, -37, -256); ctx.lineTo(-28, -176); ctx.lineTo(28, -176); ctx.lineTo(37, -256); ctx.quadraticCurveTo(37, -270, 30, -272); ctx.closePath(); };
  flat2(torso, P.top, 6);
  if (o.tie) { ctx.fillStyle = '#f3f7fb'; ctx.beginPath(); ctx.moveTo(-9, -272); ctx.lineTo(9, -272); ctx.lineTo(0, -248); ctx.fill(); ctx.fillStyle = o.tie; ctx.beginPath(); ctx.moveTo(-4, -262); ctx.lineTo(4, -262); ctx.lineTo(6, -212); ctx.lineTo(0, -204); ctx.lineTo(-6, -212); ctx.closePath(); ctx.fill(); }
  if (o.pattern) { ctx.save(); torso(); ctx.clip(); o.pattern(); ctx.restore(); }
  if (!o.dress) { ctx.fillStyle = P.bottom; ctx.beginPath(); ctx.roundRect(-29, -184, 58, 22, 8); ctx.fill(); }
  // pescoço fino e cabeça pequena e oval
  ctx.fillStyle = shade(P.skin, -.1); ctx.fillRect(-6, -288, 12, 20);
  ctx.save(); ctx.translate(look.x * 3, -314 + look.y * 2); ctx.rotate(look.x * .06 + (o.headTilt || 0));
  if (o.hairStyle === 'chanel') hair4('chanel', P.hair);
  flat2(() => { ctx.beginPath(); ctx.ellipse(0, 0, 24, 29, 0, 0, 6.283); }, P.skin, 8, -.1);
  ctx.fillStyle = P.skin; ctx.beginPath(); ctx.ellipse(-23, 4, 5, 7, 0, 0, 6.283); ctx.fill();
  if (o.hairStyle === 'chanel') { ctx.fillStyle = P.hair; ctx.beginPath(); ctx.ellipse(0, -16, 25, 15, 0, Math.PI, 0); ctx.fill(); }
  else if (o.hairStyle !== 'careca') hair4(o.hairStyle || 'curto', P.hair);
  // rosto mínimo: olhos em ponto, nariz, boca
  const bl = blink(a, .3), ex = look.x * 4, ey = look.y * 3, w = o.worry || 0;
  ctx.fillStyle = '#241a33';
  for (const dd of [-1, 1]) { ctx.beginPath(); ctx.ellipse(dd * 9 + ex, 2 + ey, 3, 3.6 * (1 - bl * .9) * (o.relief ? .3 : 1), 0, 0, 6.283); ctx.fill(); }
  if (w > .3) for (const dd of [-1, 1]) { ctx.save(); ctx.translate(dd * 9, -7); ctx.rotate(dd * -.35 * w); ctx.fillRect(-5, -1.2, 10, 2.4); ctx.restore(); }
  ctx.fillStyle = shade(P.skin, -.2); ctx.beginPath(); ctx.ellipse(3 + ex * .5, 9, 3, 4, 0, 0, 6.283); ctx.fill();
  ctx.fillStyle = '#9a3b4a';
  if (o.smile || o.relief) { ctx.beginPath(); ctx.ellipse(1, 17, 6, 3.5, 0, 0, Math.PI); ctx.fill(); }
  else if (w > .5) { ctx.beginPath(); ctx.ellipse(1, 19, 3.5, 4.5 * w, 0, 0, 6.283); ctx.fill(); }
  else ctx.fillRect(-3, 17, 7, 2.2);
  ctx.restore();
  // braço da frente: alcança o.reach (mundo) ou levanta o celular
  const up = o.phoneUp ?? 0;
  let hand = { x: lerp(52, 40, up) + 25 * sw * (1 - up), y: lerp(-140, -250, up) };
  if (o.reach) { const ww = o.reachW ?? 1; hand = { x: lerp(hand.x, (o.reach.x - x) / (sc * sx), ww), y: lerp(hand.y, (o.reach.y - y) / (sc * sy) + bob, ww) }; }
  // braço pendurado: cotovelo para fora; braço levantado ou alcançando: cotovelo para baixo
  hand = arm4({ x: 28, y: -262 }, hand, 72, 66, (up > .3 || o.reach) ? 1 : -1, o.dress ? P.skin : P.top, !!o.longSleeve && !o.dress, P.skin);
  ctx.restore();
  return { x: x + hand.x * sc * sx, y: y + (hand.y - bob) * sc * sy };
}
