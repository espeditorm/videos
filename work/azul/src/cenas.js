//@include lib_char.js
// =====================================================================
//  O AZUL FOI A ÚLTIMA COR
// =====================================================================
const T = {
  t1: C.quem - .15,          // mar de Homero -> Gladstone contando
  t2: C.depois1 - .15,       // contagem -> globo (Geiger)
  t3: C.viu - .45,           // globo -> paisagem que ganha cor
  t4: C.egipcios - .45,      // paisagem -> Egito (o azul fica ~1 s na tela)
  t5: C.pra - .3,            // Egito -> céu (pergunta)
  t6: C.linguista2 - .2,     // céu -> parque (Deutscher e a filha)
  t7: C.homero2 - .3         // parque -> mar de Homero (final)
};
const TD = .5;
const earthRot = (s, a) => (52 - a * .55) * D2R;   // Oriente Médio e Índia de frente
const SUBSOLAR = [45, 12];

// ---------- as cores acendem na ordem em que as línguas as nomearam ----------
function unlock(h) {
  if (h === 'vermelho') return 1;   // preto, branco e vermelho já existiam no mundo antigo
  const t = { amarelo: C.amarelo, verde: C.verde, azul: C.azul3 }[h];
  return CUR_T > RW0 ? (h === 'azul' ? 0 : 1) : smooth(t - .05, t + .45, storyT(CUR_T));
}
function hex2rgb(h) { const n = parseInt(h.slice(1), 16); return [n >> 16, (n >> 8) & 255, n & 255]; }
function mixc(a, b, u) { const A = hex2rgb(a), B = hex2rgb(b); return '#' + A.map((v, i) => Math.round(lerp(v, B[i], u)).toString(16).padStart(2, '0')).join(''); }
function grey(h) { const [r, g, b] = hex2rgb(h); const y = Math.round(.3 * r + .59 * g + .11 * b); return '#' + [y, y, y].map(v => v.toString(16).padStart(2, '0')).join(''); }
function col(h, hue, wine) { const u = unlock(hue); return mixc(wine || grey(h), h, u); }   // antes do nome: cinza (ou vinho)
const SEA_BLUE = '#1a66b8', SEA_BLUE2 = '#4dc7eb', WINE = '#5a1f3a', WINE2 = '#8a3a5a';
function seaCols(s) { // o mar de Homero: vinho até o azul ganhar nome; no título final, vira azul
  let u = unlock('azul');
  if (CUR_T > RW1) u = smooth(C.TITLE + .2, C.TITLE + 1.4, CUR_T);
  return [mixc(WINE, SEA_BLUE, u), mixc(WINE2, SEA_BLUE2, u)];
}

// ---------------------------------------------------------------------
//  CENA 1 e 8: HOMERO DIANTE DO MAR
// ---------------------------------------------------------------------
const HOM = { x: -260, y: 260 };
function seaCam(s, a) {
  let c;
  if (s < T.t1 + TD) c = keyed([[0, -120, -150, 1.25], [C.vinho, 120, -90, .95], [C.azul1, -60, -130, 1.05], [T.t1, -80, -130, 1.1]], s);
  else c = keyed([[T.t7, 0, -100, .6], [T.t7 + .9, -40, -120, .92], [C.nome, 120, -60, .9], [C.enxergar, 60, -100, .85]], s);
  if (CUR_T > RW1) c = mixCam(c, { x: 80, y: -60, z: .78 }, easeIO((CUR_T - RW1) / 1.6));
  return breathe(c, a);
}
function drawSeaScene(s, t, a) {
  CAM = seaCam(s, a);
  screenSpace(); ctx.fillStyle = '#e8e2d4'; ctx.fillRect(0, 0, W, H);
  applyCam();
  const skyTop = mixc('#d9d4c8', '#4dc7eb', unlock('azul')), skyBot = mixc('#f3efe6', '#ffe3a8', unlock('amarelo'));
  const g = ctx.createLinearGradient(0, -1600, 0, 0); g.addColorStop(0, skyTop); g.addColorStop(1, skyBot);
  ctx.fillStyle = g; ctx.fillRect(-5000, -4000, 10000, 4010);
  ctx.fillStyle = col('#ffd98a', 'amarelo'); ctx.beginPath(); ctx.arc(700, -700, 80, 0, 6.283); ctx.fill();
  // o mar
  const [s1, s2] = seaCols(s);
  const sg = ctx.createLinearGradient(0, 0, 0, 500); sg.addColorStop(0, s1); sg.addColorStop(1, s2);
  ctx.fillStyle = sg; ctx.fillRect(-5000, 0, 10000, 3000);
  for (let i = 0; i < 16; i++) { const y = 20 + i * 24, x = ((i * 433 + a * (14 + i)) % 4000) - 2000; ctx.fillStyle = 'rgba(255,255,255,.18)'; ctx.beginPath(); ctx.roundRect(x, y, 160 + (i * 37) % 140, 6, 3); ctx.fill(); }
  // navio grego ao longe
  ctx.save(); ctx.translate(560 + 8 * Math.sin(a * .7), 40 + 4 * Math.sin(a * 1.3));
  ctx.fillStyle = '#3a2a2e'; ctx.beginPath(); ctx.moveTo(-120, -20); ctx.lineTo(120, -20); ctx.lineTo(90, 14); ctx.lineTo(-90, 14); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#c94a3a'; ctx.beginPath(); ctx.moveTo(-6, -170); ctx.lineTo(80, -40); ctx.lineTo(-6, -40); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#3a2a2e'; ctx.fillRect(-8, -180, 8, 160); ctx.restore();
  // rochedo onde Homero está
  ctx.fillStyle = '#7a6a5c'; ctx.beginPath(); ctx.moveTo(-1600, 300); ctx.bezierCurveTo(-900, 180, -300, 200, 80, 300); ctx.lineTo(80, 1400); ctx.lineTo(-1600, 1400); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#6a5a4e'; ctx.beginPath(); ctx.moveTo(-1600, 330); ctx.bezierCurveTo(-900, 230, -300, 250, 80, 320); ctx.lineTo(80, 1400); ctx.lineTo(-1600, 1400); ctx.closePath(); ctx.fill();
  drawPerson(HOM.x, HOM.y, 1, s, a, { pal: { shirt: '#f3efe6', hair: '#e8e8ee', hairHi: '#ffffff', skin: '#e8a585' }, robe: true, beard: 'cheia', hairStyle: 'curto', look: { x: 600, y: 0 }, kicks: [C.vinho, C.azul1], reach: s > C.vinho - .3 && s < C.azul1 + .5 ? { x: HOM.x + 220, y: HOM.y - 260 } : null, reachW: smooth(C.vinho - .4, C.vinho, s) * (1 - smooth(C.azul1 + .1, C.azul1 + .5, s)), handR: 'aberta' });
  // etiqueta AZUL que cola no mar no final
  if (s > T.t7) {
    const k = spring(s - (C.nome - .1), .45, 14);
    if (k > 0) { ctx.save(); ctx.translate(380, 160 - 60 * (1 - k)); ctx.rotate(-.06); ctx.scale(k, k); ctx.fillStyle = '#1a66b8'; ctx.beginPath(); ctx.roundRect(-150, -50, 300, 100, 26); ctx.fill(); ctx.fillStyle = '#ffffff'; ctx.font = FONT(700, 62); ctx.letterSpacing = '8px'; ctx.textAlign = 'center'; ctx.fillText('AZUL', 4, 22); ctx.restore(); }
  }
  screenSpace();
  if (s < T.t1 + TD && CUR_T < RW0) {
    pill([{ s: 'ODISSEIA', px: 44, c: COL.white, ls: 8 }, { s: 'HOMERO · SÉCULO 8 A.C.', px: 26, c: COL.gold, ls: 5, w: 600 }], W / 2, 120, s, C.odisseia, C.vinho - .1);
    pill([{ s: '“MAR COR DE VINHO”', px: 48, c: '#ff8a7a', ls: 6 }], W / 2, 120, s, C.vinho, C.azul1 - .1);
    pill([{ s: 'NENHUM AZUL', px: 48, c: COL.white, ls: 8 }], W / 2, 120, s, C.azul1, T.t1 - .1);
  } else if (CUR_T < RW0) {
    pill([{ s: 'O MESMO MAR', px: 46, c: COL.white, ls: 8 }], W / 2, 120, s, C.mesmo, C.nome - .2);
    pill([{ s: 'SÓ FALTAVA O NOME', px: 46, c: COL.gold, ls: 7 }], W / 2, 120, s, C.nome, 1e9);
  }
}

// ---------------------------------------------------------------------
//  CENA 2: GLADSTONE CONTA AS CORES
// ---------------------------------------------------------------------
function countCam(s, a) {
  const c = keyed([[T.t1, 0, -200, .55], [T.t1 + .9, -200, -220, .82], [C.contou, -120, -240, .9], [C.preto, 260, -260, .82], [C.azul2, 380, -240, .9], [T.t2, 380, -240, .95]], s);
  return shake(breathe(c, a), 10 * kick(s - C.nenhuma, .4, 20), a);
}
const BARS = [['PRETO', '#1b1b22', 200, 'preto', 'vermelho'], ['BRANCO', '#f3f7fb', 100, 'branco', 'vermelho'], ['VERMELHO', '#d94f4f', 15, 'vermelho', 'vermelho'], ['AZUL', '#1a66b8', 0, 'azul2', 'azul']];
function drawCount(s, t, a) {
  CAM = countCam(s, a);
  screenSpace(); ctx.fillStyle = '#2a2230'; ctx.fillRect(0, 0, W, H);
  applyCam();
  // biblioteca vitoriana: parede, estante, mesa
  ctx.fillStyle = '#3a2a3a'; ctx.fillRect(-3000, -2000, 6000, 2260);
  for (let i = 0; i < 9; i++) { ctx.fillStyle = i % 2 ? '#4a3346' : '#43303f'; ctx.fillRect(-1400 + i * 300, -900, 300, 1160); }
  ctx.fillStyle = '#5b3a2e'; ctx.fillRect(-3000, 260, 6000, 2000);
  for (let r = 0; r < 3; r++) for (let k = 0; k < 12; k++) { ctx.fillStyle = ['#8a3434', '#3a4a6a', '#6a5a3a', '#2a2a2a'][(k + r) % 4]; ctx.fillRect(-1250 + k * 40, -700 + r * 160, 32, 130); }
  ctx.fillStyle = '#6e4632'; ctx.beginPath(); ctx.roundRect(-760, 40, 760, 40, 12); ctx.fill(); ctx.fillStyle = '#5b3a2e'; ctx.fillRect(-720, 80, 30, 200); ctx.fillRect(-70, 80, 30, 200);
  // livros de Homero na mesa
  ctx.fillStyle = '#efe2c6'; ctx.beginPath(); ctx.roundRect(-560, 6, 300, 36, 8); ctx.fill(); ctx.fillStyle = '#8a3434'; ctx.beginPath(); ctx.roundRect(-540, -26, 260, 34, 8); ctx.fill();
  drawPerson(-380, 260, 1, s, a, { pal: { shirt: '#2a2a3a', pants: '#2a2a3a', hair: '#9aa3ad', hairHi: '#c9d6e3', skin: '#efb293' }, longSleeve: true, suit: true, tie: '#f3f7fb', hairStyle: 'curto', beard: 'costeleta', look: { x: 500, y: -200 }, reach: s > C.contou - .3 && s < C.preto ? { x: -420, y: 10 } : { x: 60, y: -120 }, reachW: smooth(C.contou - .5, C.contou, s), handR: 'aponta', kicks: [C.contou, C.nenhuma] });
  // as contagens: pilhas de fichas de palavras que sobem ao vivo
  const x0 = 120;
  BARS.forEach(([lab, c, n, key, hue], i) => {
    const t0 = C[key], x = x0 + i * 230;
    const sq = storyT(Math.round(CUR_T * FPS) / FPS);
    const v = Math.round(n * easeOutCubic((sq - t0) / .9));
    const hgt = 3 * v * spring(s - t0, .6, 9);
    if (s < t0 - .1) return;
    ctx.fillStyle = 'rgba(0,0,0,.25)'; ctx.beginPath(); ctx.roundRect(x - 70, -600, 140, 640, 26); ctx.fill();
    if (n > 0) { const cc = i === 3 ? c : c; ctx.fillStyle = cc; ctx.beginPath(); ctx.roundRect(x - 56, 26 - hgt, 112, hgt, 18); ctx.fill(); for (let k = 0; k < hgt / 30; k++) { ctx.fillStyle = 'rgba(0,0,0,.12)'; ctx.fillRect(x - 56, 26 - k * 30 - 4, 112, 3); } }
    else { const k = spring(s - C.nenhuma, .42, 15); ctx.save(); ctx.translate(x, -120); ctx.scale(k, k); ctx.fillStyle = 'rgba(26,102,184,.25)'; ctx.beginPath(); ctx.roundRect(-56, -60, 112, 120, 18); ctx.fill(); ctx.restore(); }
    ctx.save(); ctx.translate(x, -660); ctx.fillStyle = COL.white; ctx.font = FONT(700, i === 3 ? 74 : 60); ctx.letterSpacing = '2px'; ctx.textAlign = 'center';
    ctx.fillText(i === 2 ? (v >= n ? '<15' : String(v)) : i === 1 ? String(v) : i === 0 ? (v >= 199 ? '~200' : String(v)) : (s > C.nenhuma ? '0' : ''), 0, 0); ctx.restore();
    ctx.save(); ctx.translate(x, 110); riseText(lab, 0, 0, 30, i === 3 ? '#8fd8e6' : COL.white, s, t0, 1e9, { ls: 4 }); ctx.restore();
  });
  screenSpace();
  pill([{ s: 'WILLIAM GLADSTONE', px: 42, c: COL.white, ls: 6 }, { s: 'BRITÂNICO · 1858', px: 26, c: COL.gold, ls: 5, w: 600 }], W / 2, 110, s, C.william, C.preto - .2);
  pill([{ s: 'AS CORES DE HOMERO', px: 40, c: COL.gold, ls: 6 }], W / 2, H - 110, s, C.preto - .1, T.t2 - .1, { pad: 18 });
}

// ---------------------------------------------------------------------
//  CENA 3: GEIGER PROCURA O AZUL PELO MUNDO
// ---------------------------------------------------------------------
const TEXTS = [['BÍBLIA HEBRAICA', 35, 31.5, 'biblia'], ['ALCORÃO', 41, 24, 'alcorao'], ['VEDAS', 78, 22, 'vedas']];
function globeCam(s, a) {
  const c = keyed([[T.t2, 0, -40, 3.4], [T.t2 + 1.2, 0, -60, 1.55], [C.vedas, 40, -60, 1.75], [T.t3, 30, -60, 1.9]], s);
  return breathe(c, a);
}
function drawGlobe(s, t, a) {
  CAM = globeCam(s, a);
  screenSpace(); drawBackground(a, 0);
  const rot = earthRot(s, a);
  drawEarth(rot, a);
  applyCam();
  TEXTS.forEach(([lab, lon, lat, key], i) => {
    const t0 = C[key]; if (s < t0 - .1) return;
    const p = geoWorld(lon, lat, rot); if (p.vis < 0) return;
    const q = ws(p.x, p.y), k = spring(s - t0, .45, 14);
    screenSpace();
    ctx.save(); ctx.translate(q.x, q.y); ctx.scale(k, k);
    ctx.fillStyle = '#efe2c6'; ctx.beginPath(); ctx.roundRect(-34, -84, 68, 84, 10); ctx.fill(); ctx.fillStyle = '#c9b89a'; for (let j = 0; j < 4; j++) ctx.fillRect(-24, -70 + j * 16, 48, 5);
    ctx.fillStyle = '#ffd98a'; ctx.beginPath(); ctx.arc(0, 0, 9, 0, 6.283); ctx.fill();
    ctx.restore();
    pill([{ s: lab, px: 24, c: COL.white, ls: 4 }], q.x, q.y - 120, s, t0, T.t3 - .1, { pad: 12 });
    // sem azul: marca vermelha
    const kx = spring(s - (C.achou - .1 + i * .08), .45, 15);
    if (kx > 0) { ctx.save(); ctx.translate(q.x + 40, q.y - 60); ctx.scale(kx, kx); ctx.fillStyle = '#ff5f6d'; ctx.beginPath(); ctx.arc(0, 0, 22, 0, 6.283); ctx.fill(); ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-8, -8); ctx.lineTo(8, 8); ctx.moveTo(8, -8); ctx.lineTo(-8, 8); ctx.stroke(); ctx.restore(); }
    applyCam();
  });
  screenSpace();
  pill([{ s: 'LAZARUS GEIGER', px: 42, c: COL.white, ls: 6 }, { s: 'LINGUISTA · 1868', px: 26, c: COL.gold, ls: 5, w: 600 }], W / 2, 110, s, C.lazarus, T.t3 - .1);
  pill([{ s: 'NENHUM AZUL', px: 44, c: '#ff8a7a', ls: 8 }], W / 2, H - 130, s, C.achou - .1, T.t3 - .1, { pad: 18 });
}

// ---------------------------------------------------------------------
//  CENA 4: A PAISAGEM GANHA COR NA ORDEM DAS PALAVRAS
// ---------------------------------------------------------------------
function orderCam(s, a) {
  const c = keyed([[T.t3, 0, -260, .5], [T.t3 + .9, 0, -240, .72], [C.vermelho2, -200, -230, .8], [C.amarelo, 200, -260, .78], [C.verde, -100, -200, .8], [C.azul3, 0, -300, .62], [T.t4, 0, -300, .66]], s);
  return shake(breathe(c, a), 8 * kick(s - C.azul3, .4, 18), a);
}
const DOTS = [['PRETO', '#1b1b22', 'preto2', 'vermelho'], ['BRANCO', '#f3f7fb', 'branco2', 'vermelho'], ['VERMELHO', '#d94f4f', 'vermelho2', 'vermelho'], ['AMARELO', '#ffd34d', 'amarelo', 'amarelo'], ['VERDE', '#3a9d62', 'verde', 'verde'], ['AZUL', '#1a66b8', 'azul3', 'azul']];
function drawOrder(s, t, a) {
  CAM = orderCam(s, a);
  screenSpace(); ctx.fillStyle = '#e8e2d4'; ctx.fillRect(0, 0, W, H);
  applyCam();
  const sky = ctx.createLinearGradient(0, -1700, 0, 0); sky.addColorStop(0, col('#4dc7eb', 'azul', '#d4cfc4')); sky.addColorStop(1, col('#bfe9f5', 'azul', '#efebe2'));
  ctx.fillStyle = sky; ctx.fillRect(-5000, -4000, 10000, 4010);
  ctx.fillStyle = col('#ffd34d', 'amarelo'); ctx.beginPath(); ctx.arc(760, -820, 110, 0, 6.283); ctx.fill();
  const [s1, s2] = [col('#1a66b8', 'azul', '#4a4a52'), col('#4dc7eb', 'azul', '#6a6a72')];
  const sg = ctx.createLinearGradient(0, -40, 0, 200); sg.addColorStop(0, s1); sg.addColorStop(1, s2); ctx.fillStyle = sg; ctx.fillRect(-5000, -40, 10000, 300);
  ctx.fillStyle = col('#f5c75f', 'amarelo'); ctx.fillRect(-5000, 220, 10000, 120);
  ctx.fillStyle = col('#48ad6b', 'verde'); ctx.beginPath(); ctx.moveTo(-5000, 300); ctx.bezierCurveTo(-1200, 180, -400, 240, 0, 300); ctx.bezierCurveTo(600, 360, 1400, 200, 5000, 320); ctx.lineTo(5000, 3000); ctx.lineTo(-5000, 3000); ctx.closePath(); ctx.fill();
  // flores vermelhas (o vermelho já tinha nome)
  for (let i = 0; i < 14; i++) { const x = -1300 + i * 200 + 40 * Math.sin(i * 7), y = 420 + (i % 3) * 60; ctx.fillStyle = col('#3a9d62', 'verde'); ctx.fillRect(x - 3, y, 6, 50); ctx.fillStyle = '#d94f4f'; ctx.beginPath(); ctx.arc(x, y, 18, 0, 6.283); ctx.fill(); }
  // a fileira de cores: cada uma acende na sua palavra
  DOTS.forEach(([lab, c, key, hue], i) => {
    const t0 = C[key], k = spring(s - t0, .45, 14), x = -750 + i * 300, y = -560;
    ctx.fillStyle = 'rgba(6,20,40,.25)'; ctx.beginPath(); ctx.arc(x, y, 90, 0, 6.283); ctx.fill();
    if (k > 0) { ctx.save(); ctx.translate(x, y); ctx.scale(k, k); ctx.fillStyle = c; ctx.beginPath(); ctx.arc(0, 0, 80, 0, 6.283); ctx.fill(); ctx.restore(); ctx.save(); ctx.translate(x, y + 150); riseText(lab, 0, 0, 34, i === 5 ? '#1a66b8' : '#1b2433', s, t0, 1e9, { ls: 4 }); ctx.restore(); }
  });
  // ondas de cor saindo do círculo azul
  if (s > C.azul3) { const u = (s - C.azul3) / 1.2; if (u < 1) { ctx.save(); ctx.globalAlpha = .35 * (1 - u); ctx.fillStyle = '#4dc7eb'; ctx.beginPath(); ctx.arc(750, -560, 80 + 1600 * easeOutCubic(u), 0, 6.283); ctx.fill(); ctx.restore(); } }
  screenSpace();
  pill([{ s: 'A ORDEM DAS CORES NAS LÍNGUAS', px: 38, c: '#1b2433', ls: 5 }], W / 2, 110, s, C.padrao - .1, C.preto2 - .2, { pad: 18 });
  pill([{ s: 'O AZUL CHEGA POR ÚLTIMO', px: 42, c: COL.white, ls: 6 }], W / 2, H - 130, s, C.azul3 + .1, T.t4 - .1, { pad: 18 });
}

// ---------------------------------------------------------------------
//  CENA 5: OS EGÍPCIOS E A TINTA AZUL
// ---------------------------------------------------------------------
function egyptCam(s, a) { return breathe(keyed([[T.t4, 0, -200, .55], [T.t4 + .9, 120, -180, .9], [C.tinta, 260, -160, 1.15], [T.t5, 260, -170, 1.2]], s), a); }
function drawEgypt(s, t, a) {
  CAM = egyptCam(s, a);
  screenSpace(); ctx.fillStyle = '#ffe3a8'; ctx.fillRect(0, 0, W, H);
  applyCam();
  const sky = ctx.createLinearGradient(0, -1500, 0, 0); sky.addColorStop(0, '#4dc7eb'); sky.addColorStop(1, '#ffe3a8'); ctx.fillStyle = sky; ctx.fillRect(-5000, -4000, 10000, 4010);
  ctx.fillStyle = '#e8b64f'; ctx.beginPath(); ctx.moveTo(-1400, 10); ctx.lineTo(-800, -620); ctx.lineTo(-200, 10); ctx.fill(); ctx.fillStyle = '#d9a23f'; ctx.beginPath(); ctx.moveTo(-800, -620); ctx.lineTo(-200, 10); ctx.lineTo(-560, 10); ctx.fill();
  ctx.fillStyle = '#f5c75f'; ctx.fillRect(-5000, 0, 10000, 3000);
  drawPerson(80, 260, 1, s, a, { pal: { shirt: '#f3efe6', hair: '#1b1b22', hairHi: '#3a3a4a', skin: '#c98a5e' }, dress: true, hairStyle: 'chanel', look: { x: 420, y: 160 }, reach: { x: 330, y: 150 }, reachW: smooth(C.fabricar - .4, C.fabricar, s), handR: 'punho', kicks: [C.egipcios, C.tinta] });
  // tigela com pigmento azul que vai ficando mais intenso (moendo)
  const grind = smooth(C.fabricar - .2, C.tinta + .4, s);
  ctx.fillStyle = '#8a5a3c'; ctx.beginPath(); ctx.ellipse(380, 190, 120, 40, 0, 0, Math.PI); ctx.fill(); ctx.fillRect(260, 150, 240, 42);
  ctx.fillStyle = mixc('#9aa3ad', '#1a66b8', grind); ctx.beginPath(); ctx.ellipse(380, 150, 112, 28, 0, 0, 6.283); ctx.fill();
  ctx.save(); ctx.translate(330 + 30 * Math.sin(a * 6) * (s > C.fabricar), 120); ctx.rotate(-.5); ctx.fillStyle = '#c9b89a'; ctx.beginPath(); ctx.roundRect(-14, -90, 28, 110, 12); ctx.fill(); ctx.restore();
  // amuleto de escaravelho azul
  const ks = spring(s - C.tinta, .45, 14);
  if (ks > 0) { ctx.save(); ctx.translate(620, -180); ctx.scale(ks, ks); ctx.fillStyle = '#1a66b8'; ctx.beginPath(); ctx.ellipse(0, 0, 60, 76, 0, 0, 6.283); ctx.fill(); ctx.fillStyle = '#4dc7eb'; ctx.beginPath(); ctx.ellipse(-20, -10, 18, 40, -.2, 0, 6.283); ctx.ellipse(20, -10, 18, 40, .2, 0, 6.283); ctx.fill(); ctx.fillStyle = '#ffd98a'; ctx.beginPath(); ctx.arc(0, -76, 18, 0, 6.283); ctx.fill(); ctx.restore(); }
  screenSpace();
  pill([{ s: 'A EXCEÇÃO: EGITO', px: 42, c: '#1b2433', ls: 6 }], W / 2, 110, s, T.t4 + .3, C.tinta - .2, { pad: 18 });
  pill([{ s: 'AZUL EGÍPCIO', px: 44, c: COL.white, ls: 7 }, { s: 'PIGMENTO SINTÉTICO · ~2500 A.C.', px: 26, c: '#8fd8e6', ls: 4, w: 600 }], W / 2, 120, s, C.tinta, T.t5 - .1);
}

// ---------------------------------------------------------------------
//  CENA 6 e 7: DE QUE COR É O CÉU? (Deutscher e a filha no parque)
// ---------------------------------------------------------------------
function parkCam(s, a) {
  let c;
  if (s < T.t6 + TD) c = keyed([[T.t5, 0, -500, .7], [T.t5 + .7, 0, -900, .55], [C.ceu1, 0, -1000, .5], [T.t6, 0, -700, .6]], s);
  else c = keyed([[T.t6, 0, -300, .55], [T.t6 + .9, -60, -260, .85], [C.cores2, 160, -260, .9], [C.ceu2, 0, -500, .62], [C.perguntou, -60, -260, .95], [C.demorou, -120, -220, 1.15], [C.branco3, -120, -230, 1.3], [T.t7, -100, -230, 1.3]], s);
  return breathe(c, a);
}
function drawPark(s, t, a) {
  CAM = parkCam(s, a);
  screenSpace(); ctx.fillStyle = '#4dc7eb'; ctx.fillRect(0, 0, W, H);
  applyCam();
  const sky = ctx.createLinearGradient(0, -2600, 0, 0); sky.addColorStop(0, '#1a66b8'); sky.addColorStop(.7, '#4dc7eb'); sky.addColorStop(1, '#d4f1f9');
  ctx.fillStyle = sky; ctx.fillRect(-5000, -5000, 10000, 5010);
  for (let i = 0; i < 8; i++) { const x = ((i * 900 + a * (10 + i)) % 7000) - 3500, y = -1900 + (i * 377) % 1400, w = 300 + (i * 97) % 260; ctx.fillStyle = 'rgba(255,255,255,.92)'; ctx.beginPath(); ctx.roundRect(x, y, w, 70, 35); ctx.fill(); ctx.beginPath(); ctx.roundRect(x + w * .25, y - 40, w * .5, 70, 35); ctx.fill(); }
  ctx.fillStyle = '#48ad6b'; ctx.fillRect(-5000, 0, 10000, 3000); ctx.fillStyle = '#3a9d62'; ctx.beginPath(); ctx.ellipse(-900, 10, 900, 120, 0, Math.PI, 0); ctx.fill();
  // árvore
  ctx.fillStyle = '#7a5235'; ctx.fillRect(560, -360, 50, 380); ctx.fillStyle = '#3a9d62'; ctx.beginPath(); ctx.arc(585, -420, 180, 0, 6.283); ctx.fill(); ctx.fillStyle = '#48ad6b'; ctx.beginPath(); ctx.arc(540, -460, 120, 0, 6.283); ctx.fill();
  if (s > T.t6) {
    // o pai mostra cartões de cor; depois aponta para o céu
    const pointSky = smooth(C.ceu2 - .6, C.ceu2 - .1, s);
    const card = s < C.ceu2 - .6 ? Math.floor(clamp((s - C.ensinou) / .45, 0, 2.99)) : -1;
    const hand = drawPerson(-80, 260, 1.05, s, a, { pal: { shirt: '#ff8a7a', pants: '#2b3346', hair: '#3b2a2e', hairHi: '#6a4a4e' }, hairStyle: 'curto', smile: s < C.perguntou, look: pointSky > .5 ? { x: 200, y: -1200 } : { x: -400, y: 100 }, reach: pointSky > 0 ? { x: 150, y: -420 } : { x: -10, y: -10 }, reachW: Math.max(pointSky, card >= 0 ? 1 : 0), handR: pointSky > .5 ? 'aponta' : 'punho', kicks: [C.ensinou, C.ceu2] });
    if (card >= 0) { const cc = ['#d94f4f', '#ffd34d', '#1a66b8'][card], lab = ['VERMELHO', 'AMARELO', 'AZUL'][card]; ctx.save(); ctx.translate(hand.x, hand.y - 60); ctx.fillStyle = '#f3f7fb'; ctx.beginPath(); ctx.roundRect(-70, -90, 140, 160, 16); ctx.fill(); ctx.fillStyle = cc; ctx.beginPath(); ctx.arc(0, -20, 46, 0, 6.283); ctx.fill(); ctx.fillStyle = '#1b2433'; ctx.font = FONT(700, 20); ctx.letterSpacing = '2px'; ctx.textAlign = 'center'; ctx.fillText(lab, 0, 52); ctx.restore(); }
    // a filha (menor, cabeça grande): pensa... e responde "branco"
    const think = smooth(C.perguntou, C.demorou, s) * (1 - smooth(C.branco3 - .2, C.branco3, s));
    drawPerson(-420, 260, .62, s, a + 1.3, { pal: { shirt: '#ffd34d', hair: '#3b2a2e', hairHi: '#6a4a4e' }, dress: true, hairStyle: 'chanel', look: pointSky > .5 && s < C.branco3 ? { x: -300, y: -1400 } : { x: -80, y: -200 }, headTilt: think * .12 * Math.sin(a * 1.5), smile: s > C.branco3, kicks: [C.branco3] });
    if (think > .05) { ctx.save(); ctx.globalAlpha = think; ctx.fillStyle = '#f3f7fb'; for (let i = 0; i < 3; i++) { const on = (Math.floor(a * 3) % 3) >= i; ctx.globalAlpha = think * (on ? 1 : .35); ctx.beginPath(); ctx.arc(-470 + i * 46, -330, 16, 0, 6.283); ctx.fill(); } ctx.restore(); }
    const kb = spring(s - C.branco3, .45, 14);
    if (kb > 0) { ctx.save(); ctx.translate(-560, -380); ctx.scale(kb, kb); ctx.fillStyle = '#f3f7fb'; ctx.beginPath(); ctx.roundRect(-150, -70, 300, 120, 40); ctx.fill(); ctx.beginPath(); ctx.moveTo(60, 40); ctx.lineTo(110, 90); ctx.lineTo(100, 40); ctx.fill(); ctx.fillStyle = '#1b2433'; ctx.font = FONT(700, 52); ctx.letterSpacing = '5px'; ctx.textAlign = 'center'; ctx.fillText('BRANCO', 0, 8); ctx.restore(); }
  }
  screenSpace();
  if (s < T.t6 + TD) { applyCam(); drawPin(0, -900, 1.4, 'VOCÊ', s, C.voce); screenSpace(); pill([{ s: 'DE QUE COR É O CÉU', px: 48, c: COL.white, ls: 7 }], W / 2, H - 150, s, C.ceu1 - .3, T.t6 - .1); }
  else {
    pill([{ s: 'GUY DEUTSCHER', px: 42, c: COL.white, ls: 6 }, { s: 'LINGUISTA', px: 26, c: COL.gold, ls: 5, w: 600 }], W / 2, 110, s, C.guy, C.ceu2 - .3);
    pill([{ s: 'NUNCA DISSE A COR DO CÉU', px: 38, c: COL.white, ls: 5 }], W / 2, 110, s, C.ceu2 - .2, C.perguntou - .1, { pad: 18 });
  }
}

// =====================================================================
//  COMPOSIÇÃO
// =====================================================================
const SCENES = { sea: drawSeaScene, count: drawCount, globe: drawGlobe, order: drawOrder, egypt: drawEgypt, park: drawPark };
const TRANS = [
  { s: T.t1, from: 'sea', to: 'count', mode: 'open' },
  { s: T.t2, from: 'count', to: 'globe', mode: 'close' },
  { s: T.t3, from: 'globe', to: 'order', mode: 'open' },
  { s: T.t4, from: 'order', to: 'egypt', mode: 'open' },
  { s: T.t5, from: 'egypt', to: 'park', mode: 'open' },
  { s: T.t7, from: 'park', to: 'sea', mode: 'open' }
];
function sceneAt(s) { let n = 'sea'; for (const tr of TRANS) if (s >= tr.s + TD) n = tr.to; return n; }
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
  if (!tr) { renderLayer(sceneAt(s), s, t, a, LA); mctx.drawImage(LA, 0, 0); }
  else {
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
      const k = 1 - easeIO(u), R = maxR * .5 * k + 2, cx = lerp(f.x, W / 2, k), cy = lerp(f.y, H / 2, k);
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
  pill([{ s: 'O AZUL FOI A ÚLTIMA COR', px: 96, c: COL.white, ls: 8 }, { s: 'POR QUE HOMERO NUNCA DISSE AZUL', px: 38, c: '#8fd8e6', ls: 6, w: 600 }], W / 2, 190, t, t0);
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
