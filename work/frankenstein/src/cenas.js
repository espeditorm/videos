// =====================================================================
//  QUEM É O MONSTRO? Frankenstein e a IA
// =====================================================================
const T = {
  t1: C.livro1 - .25,      // escrivaninha 1818 -> laboratório
  t2: C.hoje1 - .15,       // laboratório -> hoje (IA)
  t3: C.escrito - .6,      // hoje -> o livro como aviso
  t4: C.entao - .2         // livro -> pergunta final
};
const TD = .5;
const earthRot = (s, a) => 0;
const SUBSOLAR = [0, 0];

// ---------------------------------------------------------------------
//  PERSONAGENS
// ---------------------------------------------------------------------
// a criatura: design próprio (retalhos de pele, olhos desiguais), sem parafusos nem cabeça chata
function drawCreature(x, y, sc, s, a, o = {}) {
  let sq = 0; for (const k of (o.kicks || [])) sq += kick(s - k, .45, 13) * .16;
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot || 0); ctx.scale(sc * (1 + sq * .8), sc * (1 - sq));
  const bob = (o.lying ? 0 : 4 * Math.sin(a * 1.4));
  ctx.translate(0, -bob);
  const sk = '#9db7c2', sk2 = '#bccfd6', sk3 = '#86a2ad';
  // pernas
  ctx.fillStyle = '#3d4a63'; for (const d of [-1, 1]) { ctx.beginPath(); ctx.roundRect(d * 30 - 18, -110, 36, 110, 14); ctx.fill(); }
  ctx.fillStyle = '#2a3346'; for (const d of [-1, 1]) { ctx.beginPath(); ctx.roundRect(d * 32 - 24, -16, 48, 18, 9); ctx.fill(); }
  // tronco com casaco remendado
  ctx.fillStyle = '#5b4a6e'; ctx.beginPath(); ctx.roundRect(-74, -290, 148, 190, 40); ctx.fill();
  ctx.fillStyle = '#6e5a84'; ctx.beginPath(); ctx.roundRect(-60, -250, 50, 60, 12); ctx.fill(); ctx.fillStyle = '#4a3c5c'; ctx.beginPath(); ctx.roundRect(14, -180, 52, 50, 12); ctx.fill();
  // braços
  const arm = o.reach || 0;
  for (const d of [-1, 1]) {
    ctx.save(); ctx.translate(d * 72, -270); ctx.rotate(d * (.15 + .05 * Math.sin(a + d)) - (d === 1 ? arm * 1.6 : 0));
    ctx.fillStyle = '#5b4a6e'; ctx.beginPath(); ctx.roundRect(-18, 0, 36, 90, 16); ctx.fill();
    ctx.fillStyle = sk; ctx.beginPath(); ctx.roundRect(-16, 80, 32, 46, 14); ctx.fill();
    ctx.restore();
  }
  // cabeça arredondada com retalhos e pontos de costura (preenchidos)
  const sad = o.sad || 0;
  ctx.save(); ctx.translate(0, -360); ctx.rotate(sad * .18);
  ctx.fillStyle = sk; ctx.beginPath(); ctx.roundRect(-70, -76, 140, 150, 60); ctx.fill();
  ctx.fillStyle = sk2; ctx.beginPath(); ctx.roundRect(-70, -76, 70, 70, [60, 0, 0, 0]); ctx.fill();
  ctx.fillStyle = sk3; ctx.beginPath(); ctx.roundRect(10, 20, 60, 54, [0, 0, 50, 0]); ctx.fill();
  ctx.fillStyle = '#3b4a3f'; for (let k = 0; k < 6; k++) { ctx.beginPath(); ctx.roundRect(-64 + k * 12, -8, 4, 12, 2); ctx.fill(); }
  for (let k = 0; k < 4; k++) { ctx.beginPath(); ctx.roundRect(4, 22 + k * 12, 12, 4, 2); ctx.fill(); }
  // cabelo
  // careca: cicatriz de costura no alto da cabeça (pontos preenchidos) e brilho na calva
  ctx.fillStyle = 'rgba(255,255,255,.18)'; ctx.beginPath(); ctx.ellipse(-22, -52, 26, 12, -.3, 0, 6.283); ctx.fill();
  ctx.fillStyle = '#5c7480'; ctx.beginPath(); ctx.roundRect(-50, -58, 100, 6, 3); ctx.fill();
  ctx.fillStyle = '#3b4a3f'; for (let k = 0; k < 7; k++) { ctx.beginPath(); ctx.roundRect(-46 + k * 15, -66, 4, 22, 2); ctx.fill(); }
  // olhos desiguais
  const open = o.open ?? 1, bl = blink(a, .5);
  const ec = o.red ? '#ff5f6d' : '#ffd98a';
  ctx.fillStyle = '#1b2433';
  ctx.beginPath(); ctx.ellipse(-26, 6, 18, 18 * open * (1 - bl) * (1 - sad * .4), 0, 0, 6.283); ctx.fill();
  ctx.beginPath(); ctx.ellipse(28, 10, 12, 12 * open * (1 - bl) * (1 - sad * .4), 0, 0, 6.283); ctx.fill();
  if (open > .3) { ctx.fillStyle = ec; ctx.beginPath(); ctx.arc(-24, 4, 6, 0, 6.283); ctx.arc(29, 9, 4, 0, 6.283); ctx.fill(); }
  // boca
  ctx.fillStyle = '#3b4a3f'; ctx.beginPath(); ctx.ellipse(0, 46 + sad * 4, 18, 5 + sad * 3, 0, sad > .3 ? Math.PI : 0, sad > .3 ? 2 * Math.PI : Math.PI); ctx.fill();
  ctx.restore();
  ctx.restore();
}
const COAT = { shirt: '#f3f7fb', hair: '#3b2a2e', pants: '#2b3346', longPants: true, plain: true };
function bolt(x0, y0, x1, y1, seed, w, col) {
  const r = rng(seed); ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = w; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x0, y0);
  for (let i = 1; i <= 8; i++) { const k = i / 8; ctx.lineTo(lerp(x0, x1, k) + (i < 8 ? (r() - .5) * 60 : 0), lerp(y0, y1, k)); }
  ctx.stroke(); ctx.restore();
}

// ---------------------------------------------------------------------
//  CENA 1 e 4: A ESCRIVANINHA DE 1818 (o livro)
// ---------------------------------------------------------------------
function deskCam(s, a) {
  let c;
  if (s < T.t1 + TD) {
    c = keyed([[0, 0, -120, .7], [C.escreveu, 0, -150, .9], [C.frank1 + .3, 0, -170, 1.15]], s);
    c = mixCam(c, { x: 0, y: -170, z: 6 }, easeInCubic((s - (T.t1 - .4)) / (.4 + TD)));
  } else {
    c = keyed([[T.t3, 0, -150, .55], [T.t3 + .9, 0, -170, 1.0], [C.criar, 0, -180, 1.15]], s);
    c = mixCam(c, { x: 0, y: -170, z: 5 }, easeInCubic((s - (T.t4 - .4)) / (.4 + TD)));
  }
  c = breathe(c, a);
  return shake(c, 8 * kick(s - C.escreveu, .4, 20) + 8 * kick(s - C.aviso, .4, 20), a);
}
function drawDesk(s, t, a) {
  CAM = deskCam(s, a);
  screenSpace(); ctx.fillStyle = '#121a2e'; ctx.fillRect(0, 0, W, H);
  applyCam();
  ctx.fillStyle = '#1b2440'; ctx.fillRect(-3000, -2000, 6000, 2400);
  // janela com tempestade
  const flash = Math.max(Math.exp(-Math.max(0, s - C.escreveu) * 5) * (s > C.escreveu), .15 * Math.max(0, Math.sin(a * .9)) ** 30);
  ctx.fillStyle = '#2a3f63'; ctx.beginPath(); ctx.roundRect(380, -760, 420, 520, 30); ctx.fill();
  ctx.fillStyle = `rgb(${lerp(18, 200, flash)},${lerp(35, 220, flash)},${lerp(70, 255, flash)})`; ctx.beginPath(); ctx.roundRect(400, -740, 380, 480, 20); ctx.fill();
  if (flash > .3) bolt(560, -740, 640, -300, 7, 8, `rgba(255,255,255,${flash})`);
  ctx.fillStyle = '#2a3f63'; ctx.fillRect(582, -740, 16, 480); ctx.fillRect(400, -510, 380, 16);
  // escrivaninha
  ctx.fillStyle = '#5b3a2e'; ctx.beginPath(); ctx.roundRect(-900, 60, 1800, 60, 16); ctx.fill();
  ctx.fillStyle = '#4a2f25'; ctx.fillRect(-860, 120, 1720, 900);
  // vela com chama e brilho
  const fl = 1 + .08 * Math.sin(a * 17) + .05 * Math.sin(a * 29);
  const g = ctx.createRadialGradient(-420, -150, 0, -420, -150, 520 * fl);
  g.addColorStop(0, 'rgba(255,217,138,.42)'); g.addColorStop(1, 'rgba(255,217,138,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(-420, -150, 520 * fl, 0, 6.283); ctx.fill();
  ctx.fillStyle = '#f3f7fb'; ctx.beginPath(); ctx.roundRect(-440, -120, 40, 180, 10); ctx.fill();
  ctx.fillStyle = '#ffd98a'; ctx.beginPath(); ctx.ellipse(-420, -150 - 6 * fl, 13 * fl, 30 * fl, .05 * Math.sin(a * 9), 0, 6.283); ctx.fill();
  ctx.fillStyle = '#fff7dc'; ctx.beginPath(); ctx.ellipse(-420, -140, 6, 14, 0, 0, 6.283); ctx.fill();
  // tinteiro e pena
  ctx.fillStyle = '#0b1e33'; ctx.beginPath(); ctx.roundRect(380, -10, 80, 70, 16); ctx.fill();
  ctx.save(); ctx.translate(430, -20); ctx.rotate(-.5 + .04 * Math.sin(a * 2)); ctx.fillStyle = '#f3f7fb'; ctx.beginPath(); ctx.ellipse(0, -110, 22, 110, 0, 0, 6.283); ctx.fill(); ctx.restore();
  // o livro: abre na palavra "escreveu"
  const open = spring(s - (C.escreveu - .1), .5, 11);
  ctx.save(); ctx.translate(0, 40);
  ctx.fillStyle = '#7a2e2e'; ctx.beginPath(); ctx.roundRect(-300, -40, 600, 60, 14); ctx.fill();
  // páginas
  ctx.fillStyle = '#f5e6c8'; ctx.beginPath(); ctx.roundRect(-290, -60 - 300 * open * 0, 290, 70, [14, 0, 0, 14]); ctx.fill();
  ctx.save(); ctx.scale(1, 1);
  ctx.fillStyle = '#efdcb8'; ctx.beginPath(); ctx.moveTo(0, -50); ctx.quadraticCurveTo(-150, -90 * open - 20, -290, -60 * open - 10); ctx.lineTo(-290, 10); ctx.quadraticCurveTo(-150, -10, 0, 10); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#f5e6c8'; ctx.beginPath(); ctx.moveTo(0, -50); ctx.quadraticCurveTo(150, -90 * open - 20, 290, -60 * open - 10); ctx.lineTo(290, 10); ctx.quadraticCurveTo(150, -10, 0, 10); ctx.closePath(); ctx.fill();
  ctx.restore();
  // capa fechada que gira para abrir
  if (open < .98) {
    ctx.save(); ctx.scale(1 - open, 1);
    ctx.fillStyle = '#8a3434'; ctx.beginPath(); ctx.roundRect(0, -70, 300, 90, 14); ctx.fill();
    ctx.restore();
  }
  ctx.restore();
  // linhas de texto nas páginas (preenchidas)
  if (open > .5) { for (let k = 0; k < 4; k++) { ctx.fillStyle = 'rgba(91,58,46,.35)'; ctx.fillRect(-250, -20 - k * 16 * open + 30, 200, 5); ctx.fillRect(40, -20 - k * 16 * open + 30, 200, 5); } }
  screenSpace();
  if (s < T.t1 + TD) {
    pill([{ s: 'FRANKENSTEIN', px: 64, c: COL.white, ls: 10 }, { s: 'MARY SHELLEY · 1818', px: 30, c: COL.gold, ls: 6, w: 600 }], W / 2, 150, s, C.escreveu + .1, T.t1 - .1);
  } else {
    pill([{ s: 'UM AVISO', px: 56, c: COL.gold, ls: 10 }], W / 2, 150, s, C.aviso - .1, T.t4 - .1);
    pill([{ s: 'NÃO BASTA CRIAR', px: 40, c: COL.white, ls: 6 }, { s: 'É PRECISO PENSAR NO QUE SE CRIA', px: 32, c: COL.teal, ls: 4, w: 600 }], W / 2, H - 170, s, C.criar - .2, T.t4 - .1);
  }
}

// ---------------------------------------------------------------------
//  CENA 2: O LABORATÓRIO (e a virada do nome)
// ---------------------------------------------------------------------
const SCI = { x: -420, y: 220 }, CRE = { x: 260, y: 220 };
function labCam(s, a) {
  let c = keyed([[T.t1, 0, -200, .5], [T.t1 + .9, -60, -220, .78], [C.vida, 0, -240, .82], [C.consequencias, -200, -220, .9],
                 [C.criatura1, 220, -260, 1.0], [C.perigosa, 160, -330, .7], [C.detalhe, 0, -260, .72], [C.criatura2, 200, -280, .82], [C.criador, -300, -280, .9], [T.t2, -200, -260, .95]], s);
  if (CUR_T > RW1) c = mixCam(c, { x: -60, y: -300, z: .62 }, easeIO((CUR_T - RW1) / 1.4));
  c = breathe(c, a);
  return shake(c, 22 * kick(s - C.vida, .35, 22) + 10 * kick(s - C.perigosa, .4, 20), a);
}
function nameTag(x, y, s, a) {
  // a etiqueta FRANKENSTEIN: começa na criatura, recebe um X, voa para o cientista
  const k = spring(s - (C.frank2 - .15), .45, 14); if (k <= 0) return;
  const move = easeIO((s - (C.criador - .2)) / .6);
  const cx = lerp(CRE.x, SCI.x, move), cy = lerp(-560, -560, move) - 60 * Math.sin(Math.PI * move);
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(.05 * Math.sin(a * 2)); ctx.scale(k, k);
  ctx.fillStyle = 'rgba(6,20,40,.82)'; ctx.beginPath(); ctx.roundRect(-230, -52, 460, 104, 30); ctx.fill();
  ctx.fillStyle = COL.white; ctx.font = FONT(700, 54); ctx.letterSpacing = '6px'; ctx.textAlign = 'center'; ctx.fillText('FRANKENSTEIN', 3, 19);
  ctx.restore();
  // X vermelho sobre a criatura, ✓ verde no criador
  const kx = spring(s - C.criatura2, .45, 15) * (1 - move);
  if (kx > .02) { ctx.save(); ctx.translate(CRE.x + 300, -560); ctx.scale(kx, kx); ctx.fillStyle = '#ff5f6d'; ctx.rotate(.785); ctx.beginPath(); ctx.roundRect(-46, -11, 92, 22, 11); ctx.roundRect(-11, -46, 22, 92, 11); ctx.fill(); ctx.restore(); }
  const kv = spring(s - (C.criador + .35), .45, 15);
  if (kv > 0) { ctx.save(); ctx.translate(SCI.x + 270, -560); ctx.scale(kv, kv); ctx.fillStyle = '#5fc47a'; ctx.beginPath(); ctx.arc(0, 0, 44, 0, 6.283); ctx.fill(); ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 12; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-20, 2); ctx.lineTo(-4, 18); ctx.lineTo(22, -16); ctx.stroke(); ctx.restore(); }
}
function drawLab(s, t, a) {
  CAM = labCam(s, a);
  screenSpace(); ctx.fillStyle = '#121a2e'; ctx.fillRect(0, 0, W, H);
  applyCam();
  const flash = Math.exp(-Math.max(0, s - C.vida) * 3.5) * (s > C.vida - .05);
  ctx.fillStyle = '#1b2440'; ctx.fillRect(-4000, -3000, 8000, 3240);
  for (let y = -1500; y < 240; y += 120) for (let x = -2000 + ((y / 120) % 2 ? 90 : 0); x < 2000; x += 180) { ctx.fillStyle = 'rgba(143,216,230,.05)'; ctx.beginPath(); ctx.roundRect(x + 6, y + 6, 168, 108, 14); ctx.fill(); }
  ctx.fillStyle = '#141c33'; ctx.fillRect(-4000, 240, 8000, 2000);
  // sombra gigante na parede ("perigosa")
  const shd = smooth(C.perigosa - .4, C.perigosa + .3, s) * (1 - smooth(C.detalhe + .2, C.detalhe + .8, s));
  if (shd > 0) { ctx.save(); ctx.globalAlpha = .55 * shd; ctx.translate(CRE.x + 120, 240); ctx.scale(2.4, 2.4); ctx.filter = 'brightness(0)'; drawCreature(0, 0, 1, s, a, { red: true }); ctx.filter = 'none'; ctx.restore(); }
  // bobina e raios em "vida"
  ctx.fillStyle = '#8a9bb5'; ctx.beginPath(); ctx.roundRect(820, -420, 60, 660, 20); ctx.fill();
  ctx.fillStyle = '#c9d6e3'; ctx.beginPath(); ctx.arc(850, -440, 60, 0, 6.283); ctx.fill();
  if (flash > .05) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; for (let i = 0; i < 3; i++) bolt(850, -440, CRE.x + 60, -40, 11 + i + Math.floor(a * 20), 10 - i * 3, `rgba(143,236,255,${flash})`); ctx.restore(); }
  // mesa de operação
  ctx.fillStyle = '#5c6f8f'; ctx.beginPath(); ctx.roundRect(CRE.x - 300, -10, 600, 40, 14); ctx.fill();
  ctx.fillStyle = '#3d4a63'; ctx.beginPath(); ctx.roundRect(CRE.x - 260, 30, 30, 210, 10); ctx.roundRect(CRE.x + 230, 30, 30, 210, 10); ctx.fill();
  // a criatura: deitada, senta em "vida", se levanta, fica sozinha
  const sit = spring(s - (C.vida + .15), .5, 10), stand = easeIO((s - (C.resultado - .2)) / .8);
  const rot = lerp(-Math.PI / 2, 0, Math.min(1, sit * 1.0));
  const cy = lerp(-20, 220, stand), cx = lerp(CRE.x - 60, CRE.x, stand);
  drawCreature(cx + (1 - sit) * 180, cy, .9, s, a, { rot: rot * (1 - stand), open: smooth(C.vida, C.vida + .5, s), sad: smooth(C.rejeitada, C.confusa, s) * (1 - smooth(C.perigosa - .3, C.perigosa, s)), red: s > C.perigosa - .1 && s < C.detalhe, kicks: [C.vida + .3, C.rejeitada, C.perigosa], lying: sit < .5 });
  // o cientista: puxa a alavanca em "vida", depois vira as costas em "consequências"
  const away = easeIO((s - C.consequencias) / 1.0) * (1 - easeIO((s - C.detalhe) / .8));
  const lever = spring(s - (C.vida - .3), .5, 12) * (1 - easeIO((s - C.consequencias) / .4));
  drawMan(SCI.x - away * 260, SCI.y, 1.05, s, a, { ...COAT, phoneUp: lever, worry: s > C.vida ? .6 : 0, look: away > .5 ? { x: -1200, y: -300 } : { x: CRE.x, y: -300 }, kicks: [C.vida, C.consequencias, C.criador] });
  // alavanca
  ctx.fillStyle = '#8a9bb5'; ctx.beginPath(); ctx.roundRect(SCI.x + 120, -120, 40, 360, 12); ctx.fill();
  ctx.save(); ctx.translate(SCI.x + 140, -120); ctx.rotate(lerp(-.6, .6, lever)); ctx.fillStyle = '#c9d6e3'; ctx.beginPath(); ctx.roundRect(-8, -150, 16, 150, 8); ctx.fill(); ctx.fillStyle = '#ff8a7a'; ctx.beginPath(); ctx.arc(0, -150, 22, 0, 6.283); ctx.fill(); ctx.restore();
  nameTag(0, 0, s, a);
  // clarão em tela cheia no raio
  screenSpace();
  if (flash > .02) { ctx.fillStyle = `rgba(220,245,255,${.55 * flash})`; ctx.fillRect(0, 0, W, H); }
  pill([{ s: 'CRIA VIDA', px: 40, c: COL.white, ls: 7 }], W / 2, 120, s, C.vida, C.consequencias - .1, { pad: 18 });
  pill([{ s: 'SEM PENSAR NAS CONSEQUÊNCIAS', px: 36, c: COL.coral, ls: 5 }], W / 2, 120, s, C.consequencias, C.resultado - .1, { pad: 18 });
  pill([{ s: 'REJEITADA · CONFUSA · PERIGOSA', px: 36, c: COL.white, ls: 5 }], W / 2, H - 120, s, C.rejeitada, C.detalhe - .1, { pad: 18 });
  if (CUR_T < RW0) pill([{ s: 'O DETALHE QUE MUITA GENTE ESQUECE', px: 34, c: COL.gold, ls: 5 }], W / 2, H - 120, s, C.detalhe, T.t2 - .1, { pad: 18 });
}

// ---------------------------------------------------------------------
//  CENA 3: HOJE (IA sem rosto) e CENA 5: a pergunta final
// ---------------------------------------------------------------------
const NET = (() => {   // nós em forma de figura humana
  const r = rng(99), pts = [];
  for (let i = 0; i < 70; i++) {
    const part = r();
    let x, y;
    if (part < .22) { const an = r() * 6.283, rr = Math.sqrt(r()) * 70; x = Math.cos(an) * rr; y = -360 + Math.sin(an) * rr * 1.05; }
    else if (part < .7) { x = (r() - .5) * 150; y = -280 + r() * 190; }
    else if (part < .85) { const d = r() < .5 ? -1 : 1; x = d * (90 + r() * 30); y = -270 + r() * 150; }
    else { const d = r() < .5 ? -1 : 1; x = d * (20 + r() * 30); y = -90 + r() * 90; }
    pts.push({ x, y, ph: r() * 6 });
  }
  const edges = [];
  for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) { const d = Math.hypot(pts[i].x - pts[j].x, pts[i].y - pts[j].y); if (d < 62) edges.push([i, j]); }
  return { pts, edges };
})();
function drawNet(x, y, sc, s, a, o = {}) {
  const col = o.red ? '255,95,109' : '143,236,255';
  const grow = o.grow ?? 1, scatter = o.scatter || 0;
  ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc);
  ctx.globalCompositeOperation = 'lighter';
  const P = NET.pts.map((p, i) => {
    const sx = Math.sin(p.ph * 7) * 900 * scatter, sy = (Math.cos(p.ph * 5) * 500 - 300) * scatter;
    return { x: p.x + sx + 4 * Math.sin(a * 2 + p.ph), y: p.y + sy + 4 * Math.cos(a * 1.7 + p.ph), on: clamp(grow * 1.4 - i / NET.pts.length * .9) };
  });
  ctx.lineWidth = 2.5;
  for (const [i, j] of NET.edges) { const on = Math.min(P[i].on, P[j].on) * (1 - scatter); if (on <= 0) continue; ctx.strokeStyle = `rgba(${col},${.35 * on})`; ctx.beginPath(); ctx.moveTo(P[i].x, P[i].y); ctx.lineTo(P[j].x, P[j].y); ctx.stroke(); }
  for (const p of P) { if (p.on <= 0) continue; const pul = .6 + .4 * Math.sin(a * 4 + p.x); ctx.fillStyle = `rgba(${col},${.9 * p.on * pul})`; ctx.beginPath(); ctx.arc(p.x, p.y, 6 * p.on, 0, 6.283); ctx.fill(); }
  ctx.restore();
}
const X_CAR = 2600, X_LOAN = 5200, X_FACE = 7800, X_END = 10400;
function aiCam(s, a) {
  let c;
  if (s < T.t3 + TD) {
    c = keyed([[T.t2, 0, -220, .55], [T.t2 + .9, 0, -240, .8], [C.inteligencias, 0, -250, .95], [C.sistemas, 0, -230, .7], [C.decidem, 0, -230, .62],
               [C.carro - .2, X_CAR, -150, .75], [C.acidente, X_CAR, -170, .85], [C.algoritmo - .2, X_LOAN, -120, .75], [C.preconceitos, X_LOAN, -140, .85], [C.preconceitos + .75, X_LOAN, -130, .9],
               [C.rosto - .2, X_FACE, -260, .7], [C.rosto + .3, X_FACE, -280, .8], [C.recomendacoes, X_FACE + 120, -240, .78], [C.decisoes, X_FACE, -220, .9]], s);
    c = mixCam(c, { x: X_FACE, y: -230, z: 5 }, easeInCubic((s - (T.t3 - .4)) / (.4 + TD)));
  } else {
    c = keyed([[T.t4, X_END, -250, .5], [T.t4 + .9, X_END, -260, .72], [C.aliadas, X_END - 300, -260, .82], [C.monstros2, X_END + 300, -260, .82]], s);
  }
  c = breathe(c, a);
  return shake(c, 10 * kick(s - C.preconceitos, .4, 20) + 8 * kick(s - C.acidente, .4, 20) + 12 * kick(s - C.monstros2, .4, 20), a);
}
function person(x, y, sc, col, s, t0) {
  const k = spring(s - t0, .45, 14); if (k <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(sc * k, sc * k);
  ctx.fillStyle = col; ctx.beginPath(); ctx.roundRect(-40, -110, 80, 110, 30); ctx.fill();
  ctx.fillStyle = SKIN; ctx.beginPath(); ctx.arc(0, -150, 36, 0, 6.283); ctx.fill();
  ctx.restore();
}
function drawAI(s, t, a) {
  CAM = aiCam(s, a);
  screenSpace(); drawBackground(a, 0);
  applyCam();
  if (s < T.t3 + TD) {
    // 1) de costuras para algoritmos: a criatura antiga vira rede
    const morph = easeIO((s - (C.eletricidade + .1)) / 1.2);
    if (morph < 1) { ctx.save(); ctx.globalAlpha = 1 - morph; drawCreature(0, 120, .9, s, a, { kicks: [C.costuras] }); ctx.restore(); }
    const grow = morph + .6 * smooth(C.sistemas, C.decidem + .5, s);
    drawNet(0, 120, lerp(1.25, 1.7, smooth(C.sistemas, C.decidem, s)), s, a, { grow });
    // ícones riscados: costura e raio
    for (const [ix, t0, kind] of [[-420, C.costuras, 'agulha'], [420, C.eletricidade, 'raio']]) {
      const k = spring(s - t0, .45, 14) * (1 - easeIO((s - C.inteligencias) / .4)); if (k <= .02) continue;
      ctx.save(); ctx.translate(ix, -300); ctx.scale(k, k);
      ctx.fillStyle = 'rgba(6,20,40,.62)'; ctx.beginPath(); ctx.roundRect(-90, -90, 180, 180, 36); ctx.fill();
      ctx.fillStyle = kind === 'raio' ? '#ffd98a' : '#c9d6e3';
      if (kind === 'raio') { ctx.beginPath(); ctx.moveTo(10, -60); ctx.lineTo(-30, 10); ctx.lineTo(0, 10); ctx.lineTo(-14, 60); ctx.lineTo(34, -14); ctx.lineTo(4, -14); ctx.closePath(); ctx.fill(); }
      else { ctx.save(); ctx.rotate(-.7); ctx.beginPath(); ctx.roundRect(-6, -60, 12, 120, 6); ctx.fill(); ctx.restore(); }
      const kx = spring(s - (t0 + .25), .45, 15);
      ctx.fillStyle = '#ff5f6d'; ctx.save(); ctx.rotate(.785); ctx.scale(kx, kx); ctx.beginPath(); ctx.roundRect(-70, -8, 140, 16, 8); ctx.fill(); ctx.restore();
      ctx.restore();
    }
    // 2) carro autônomo: quem proteger?
    if (s > C.carro - 1) {
      const kc = spring(s - (C.carro - .1), .45, 13);
      ctx.save(); ctx.translate(X_CAR, 0);
      ctx.fillStyle = '#2a3f63'; ctx.beginPath(); ctx.moveTo(-60, 300); ctx.lineTo(60, 300); ctx.lineTo(60, -40); ctx.lineTo(420, -400); ctx.lineTo(300, -420); ctx.lineTo(0, -120); ctx.lineTo(-300, -420); ctx.lineTo(-420, -400); ctx.lineTo(-60, -40); ctx.closePath(); ctx.fill();
      const cy = lerp(500, 150, easeOutCubic((s - C.carro + .1) / 1.0));
      ctx.save(); ctx.translate(0, cy); ctx.scale(kc, kc);
      ctx.fillStyle = '#8fd8e6'; ctx.beginPath(); ctx.roundRect(-60, -100, 120, 200, 40); ctx.fill(); ctx.fillStyle = '#0a1c2c'; ctx.beginPath(); ctx.roundRect(-44, -70, 88, 60, 18); ctx.fill();
      ctx.restore();
      // cone do sensor
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; const g = ctx.createRadialGradient(0, cy - 100, 0, 0, cy - 100, 420); g.addColorStop(0, 'rgba(143,236,255,.35)'); g.addColorStop(1, 'rgba(143,236,255,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(0, cy - 100); ctx.lineTo(-260, cy - 520); ctx.lineTo(260, cy - 520); ctx.closePath(); ctx.fill(); ctx.restore();
      person(-360, -410, .9, '#ff8a7a', s, C.escolher); person(360, -410, .9, '#ffd98a', s, C.escolher + .12);
      if (s > C.proteger) { const k = spring(s - C.proteger, .45, 15); ctx.save(); ctx.translate(0, -330); ctx.scale(k, k); ctx.fillStyle = COL.gold; ctx.font = FONT(700, 150); ctx.textAlign = 'center'; ctx.fillText('?', 0, 50); ctx.restore(); }
      ctx.restore();
    }
    // 3) empréstimo e vaga: o feixe do algoritmo lê uma fila de pessoas; uma é recusada por preconceito
    if (s > C.algoritmo - 1) {
      ctx.save(); ctx.translate(X_LOAN, 0);
      ctx.fillStyle = '#2a3f63'; ctx.beginPath(); ctx.roundRect(-150, -560, 300, 260, 44); ctx.fill();
      drawNet(0, -330, .55, s, a, { grow: 1 });
      const cols = ['#8fd8e6', '#ffd98a', '#ff8a7a', '#f3f7fb'], xs = [-480, -160, 160, 480];
      for (let i = 0; i < 4; i++) {
        const t0 = C.algoritmo + .15 + i * .45, ok = i !== 2;
        person(xs[i], 260, 1.1, cols[i], s, C.algoritmo - .1 + i * .08);
        // feixe de leitura
        const u = (s - t0) / .45;
        if (u > 0 && u < 1) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = `rgba(143,236,255,${.25 * Math.sin(Math.PI * u)})`; ctx.beginPath(); ctx.moveTo(-40, -300); ctx.lineTo(40, -300); ctx.lineTo(xs[i] + 90, 270); ctx.lineTo(xs[i] - 90, 270); ctx.closePath(); ctx.fill(); ctx.restore(); }
        const k = spring(s - (t0 + .3), .45, 15);
        if (k > 0) {
          ctx.save(); ctx.translate(xs[i], -40); ctx.scale(k, k);
          ctx.fillStyle = ok ? '#5fc47a' : '#ff5f6d'; ctx.beginPath(); ctx.arc(0, 0, 52, 0, 6.283); ctx.fill();
          ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 13; ctx.lineCap = 'round'; ctx.beginPath();
          if (ok) { ctx.moveTo(-22, 2); ctx.lineTo(-5, 20); ctx.lineTo(24, -18); } else { ctx.moveTo(-18, -18); ctx.lineTo(18, 18); ctx.moveTo(18, -18); ctx.lineTo(-18, 18); }
          ctx.stroke(); ctx.restore();
        }
      }
      // carimbo PRECONCEITO sobre a pessoa recusada
      const ks = spring(s - C.preconceitos, .42, 15);
      if (ks > 0) {
        ctx.save(); ctx.translate(xs[2], 120); ctx.rotate(-.14); const sc2 = lerp(1.8, 1, ks); ctx.scale(sc2, sc2); ctx.globalAlpha = clamp(ks * 2);
        ctx.fillStyle = '#ff5f6d'; ctx.beginPath(); ctx.roundRect(-200, -44, 400, 88, 26); ctx.fill();
        ctx.fillStyle = '#ffffff'; ctx.font = FONT(700, 46); ctx.letterSpacing = '5px'; ctx.textAlign = 'center'; ctx.fillText('PRECONCEITO', 2, 16);
        ctx.restore();
      }
      ctx.restore();
    }
    // 4) sem rosto: a rede se desfaz em recomendações; as decisões têm fios
    if (s > C.diferente - 1) {
      const sc = easeIO((s - C.rosto) / 1.0);
      drawNet(X_FACE, 60, 1.6, s, a, { grow: 1, scatter: sc });
      const kp = spring(s - (C.recomendacoes - .2), .45, 13);
      if (kp > 0) {
        ctx.save(); ctx.translate(X_FACE + 520, -260); ctx.scale(kp, kp);
        ctx.fillStyle = '#18263a'; ctx.beginPath(); ctx.roundRect(-110, -200, 220, 400, 34); ctx.fill();
        for (let k = 0; k < 4; k++) { const yy = -160 + ((k * 90 - (s - C.recomendacoes) * 220) % 360 + 360) % 360; ctx.fillStyle = ['#ff8a7a', '#8fd8e6', '#ffd98a', '#5fc47a'][k]; ctx.beginPath(); ctx.roundRect(-90, yy, 180, 70, 14); ctx.fill(); }
        ctx.restore();
      }
      const km = spring(s - (C.decisoes - .2), .45, 12);
      if (km > 0) {
        const mx = X_FACE - 380, my = 260, sway = Math.sin(a * 2.2);
        ctx.save(); ctx.globalAlpha = km;
        ctx.strokeStyle = 'rgba(143,236,255,.6)'; ctx.lineWidth = 3;
        for (const [hx, hy] of [[-60, -200 + 30 * sway], [60, -200 - 30 * sway], [0, -330]]) { ctx.beginPath(); ctx.moveTo(mx + hx * 1.6, -900); ctx.lineTo(mx + hx, my + hy); ctx.stroke(); }
        ctx.restore();
        drawMan(mx, my, .9 * km, s, a, { shirt: '#ff8a7a', plain: true, look: { x: mx, y: -900 }, phoneUp: .5 + .3 * sway, kicks: [C.decisoes] });
      }
    }
  } else {
    // 5) a pergunta final: aliadas (rede azul) ou monstros (sombra vermelha)
    drawNet(X_END - 380, 160, 1.5, s, a, { grow: smooth(T.t4, C.aliadas, s) + .2 });
    const km = spring(s - (C.monstros2 - .2), .45, 12);
    if (km > 0) { ctx.save(); ctx.globalAlpha = .9 * km; ctx.translate(X_END + 380, 140); ctx.scale(1.1 * km, 1.1 * km); drawCreature(0, 0, 1, s, a, { red: true, kicks: [C.monstros2] }); ctx.restore(); drawNet(X_END + 380, 160, 1.5, s, a, { red: true, grow: km }); }
  }
  screenSpace();
  pill([{ s: 'INTELIGÊNCIAS ARTIFICIAIS', px: 42, c: COL.teal, ls: 6 }], W / 2, 120, s, C.inteligencias, C.carro - .3, { pad: 18 });
  pill([{ s: 'JÁ DECIDEM POR NÓS', px: 40, c: COL.white, ls: 6 }], W / 2, H - 130, s, C.decidem - .1, C.carro - .3, { pad: 18 });
  pill([{ s: 'QUEM PROTEGER', px: 44, c: COL.gold, ls: 7 }], W / 2, 120, s, C.proteger - .1, C.algoritmo - .3, { pad: 18 });
  pill([{ s: 'EMPRÉSTIMO · VAGA', px: 40, c: COL.white, ls: 6 }], W / 2, 120, s, C.emprestimo - .1, C.preconceitos - .1, { pad: 18 });
  pill([{ s: 'REPETE NOSSOS PRECONCEITOS', px: 40, c: COL.coral, ls: 6 }], W / 2, 120, s, C.preconceitos, C.diferente - .3, { pad: 18 });
  pill([{ s: 'SEM ROSTO', px: 44, c: COL.white, ls: 8 }], W / 2, 120, s, C.rosto - .1, C.recomendacoes - .2, { pad: 18 });
  pill([{ s: 'NAS RECOMENDAÇÕES', px: 38, c: COL.teal, ls: 6 }, { s: 'E NAS SUAS DECISÕES', px: 38, c: COL.gold, ls: 6 }].slice(0, s > C.decisoes - .1 ? 2 : 1), W / 2, 130, s, C.recomendacoes - .1, T.t3 - .1);
  pill([{ s: 'ALIADAS', px: 50, c: COL.teal, ls: 8 }], W / 2 - 380 * CAM.z, H - 150, s, C.aliadas - .1, 1e9, { pad: 18 });
  pill([{ s: 'OU MONSTROS', px: 50, c: COL.coral, ls: 8 }], W / 2 + 380 * CAM.z, H - 150, s, C.monstros2 - .2, 1e9, { pad: 18 });
}

// =====================================================================
//  COMPOSIÇÃO
// =====================================================================
const SCENES = { desk: drawDesk, lab: drawLab, ai: drawAI };
const TRANS = [
  { s: T.t1, from: 'desk', to: 'lab', mode: 'open' },
  { s: T.t2, from: 'lab', to: 'ai', mode: 'open' },
  { s: T.t3, from: 'ai', to: 'desk', mode: 'close' },
  { s: T.t4, from: 'desk', to: 'ai', mode: 'open' }
];
function sceneAt(s) { let n = 'desk'; for (const tr of TRANS) if (s >= tr.s + TD) n = tr.to; return n; }
function renderLayer(name, s, t, a, layer) {
  const c = layer.getContext('2d'); ctx = c; c.setTransform(1, 0, 0, 1, 0, 0);
  SCENES[name](s, t, a); c.setTransform(1, 0, 0, 1, 0, 0); ctx = mctx;
  return layer;
}
let CUR_T = 0;
function draw(t) {
  CUR_T = t;
  const a = t, s = storyT(t);
  ctx = mctx; mctx.setTransform(1, 0, 0, 1, 0, 0);
  const tr = TRANS.find(q => s >= q.s && s < q.s + TD);
  if (!tr) {
    renderLayer(sceneAt(s), s, t, a, LA); mctx.drawImage(LA, 0, 0);
  } else {
    const u = (s - tr.s) / TD, maxR = Math.hypot(W, H), f = { x: W / 2, y: H / 2 - 60 };
    if (tr.mode === 'open') {
      renderLayer(tr.from, s, t, a, LA); mctx.drawImage(LA, 0, 0);
      renderLayer(tr.to, s, t, a, LB);
      const R = maxR * easeInCubic(u) + 4;
      mctx.save(); mctx.beginPath(); mctx.arc(f.x, f.y, R, 0, 6.283); mctx.clip(); mctx.drawImage(LB, 0, 0); mctx.restore();
      const rg = mctx.createRadialGradient(f.x, f.y, Math.max(0, R - 26), f.x, f.y, R + 10);
      rg.addColorStop(0, 'rgba(143,216,230,0)'); rg.addColorStop(.7, `rgba(200,240,255,${.5 * (1 - u)})`); rg.addColorStop(1, 'rgba(143,216,230,0)');
      mctx.fillStyle = rg; mctx.beginPath(); mctx.arc(f.x, f.y, R + 10, 0, 6.283); mctx.fill();
    } else {
      renderLayer(tr.to, s, t, a, LA); mctx.drawImage(LA, 0, 0);
      renderLayer(tr.from, s, t, a, LB);
      const k = 1 - easeIO(u), R = maxR * .5 * k + 2;
      const cx = lerp(f.x, W / 2, k), cy = lerp(f.y, H / 2, k);
      mctx.save(); mctx.beginPath(); mctx.arc(cx, cy, R, 0, 6.283); mctx.clip();
      mctx.translate(cx, cy); mctx.scale(Math.max(k, .02), Math.max(k, .02)); mctx.drawImage(LB, -W / 2, -H / 2); mctx.restore();
    }
  }
  ctx = mctx; mctx.setTransform(1, 0, 0, 1, 0, 0);
  drawTitle(t);
  drawRewindFX(t);
  finish(t);
}
function drawTitle(t) {
  const t0 = C.TITLE; if (t < t0) return;
  pill([{ s: 'QUEM É O MONSTRO', px: 110, c: COL.white, ls: 9 }, { s: 'FRANKENSTEIN ERA O CRIADOR', px: 40, c: COL.gold, ls: 7, w: 600 }], W / 2, H - 200, t, t0);
}
let texturesReady = false;
function drawSafe(t) { if (!texturesReady) { buildTextures(); texturesReady = true; } draw(t); }
window.seek = function (t) { drawSafe(clamp(t, 0, DUR)); return true; };
window.renderFrame = function (i) {
  const t = i / FPS, sh = .6 / FPS;
  drawSafe(Math.max(0, t - sh / 4));
  sctx.globalAlpha = 1; sctx.drawImage(cv, 0, 0);
  drawSafe(t + sh / 4);
  mctx.save(); mctx.setTransform(1, 0, 0, 1, 0, 0); mctx.globalAlpha = .5; mctx.drawImage(scratch, 0, 0); mctx.restore();
  return true;
};
window.DUR = DUR; window.FPS = FPS; window.RW = [RW0, RW1, RW_BACK];
document.fonts.load('700 40px Fredoka').then(() => document.fonts.load('600 40px Fredoka')).then(() => { window.READY = true; seek(0); });
</script>
</body>
</html>
