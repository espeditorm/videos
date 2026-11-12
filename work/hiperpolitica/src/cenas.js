//@include lib_char.js
// =====================================================================
//  HIPERPOLÍTICA
// =====================================================================
const T = {
  t1: C.multiplique - .3,    // sofá -> globo (recuo)
  t2: C.historiador - .35,   // globo -> biblioteca (Jäger)
  t3: C.entender - .3,       // biblioteca -> gráfico de dois eixos
  t4: C.sindicatos - .55,    // gráfico -> salão do século 20
  t5: C.nos - .3,            // salão -> gráfico (anos 90, 2008, 2016)
  t6: C.redes - .15,         // gráfico -> rua e hashtags
  t7: C.facil1 - .3,         // rua -> tela dividida (sindicato x like)
  t8: C.por2 - .3,           // tela dividida -> energia que some
  t9: C.jager2 - .3,         // energia -> biblioteca
  t10: C.entao - .3          // biblioteca -> sofá (pergunta final)
};
const TD = .5;
const earthRot = (s, a) => (-35 + a * .5) * D2R;   // Atlântico de frente: Américas, Europa e África
const SUBSOLAR = [150, -5];                         // noite sobre o Atlântico: luzes das cidades acesas
const RED = '#ff5f6d', NAVY = '#0b1e33', GOLD = '#ffd98a', TEAL = '#8fd8e6', CORAL = '#ff8a7a';
const YOU = { pal: { shirt: '#ff8a7a', pants: '#2b3346', hair: '#3b2a2e', hairHi: '#6a4a4e' }, hairStyle: 'topete' };
const JAG = { pal: { shirt: '#2f3b52', pants: '#1f2636', hair: '#c9a36a', hairHi: '#e8c98f', skin: '#f2c2a0' }, longSleeve: true, suit: true, tie: '#ff8a7a', hairStyle: 'curto' };

// ---------- peças reutilizadas ----------
function popAt(s, t0, z = .45, w = 14) { return spring(s - t0, z, w); }
function rr(x, y, w, h, r, c) { ctx.fillStyle = c; ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fill(); }
function txt(str, x, y, px, c, ls = 4, w = 700, align = 'center') { ctx.font = FONT(w, px); ctx.letterSpacing = ls + 'px'; ctx.textAlign = align; ctx.fillStyle = c; ctx.fillText(str, x, y); }
// rosto bravo (o "post que revolta")
function angry(x, y, r, a) {
  ctx.save(); ctx.translate(x, y);
  ctx.fillStyle = RED; ctx.beginPath(); ctx.arc(0, 0, r, 0, 6.283); ctx.fill();
  ctx.fillStyle = '#ffffff';
  for (const d of [-1, 1]) { ctx.save(); ctx.translate(d * r * .36, -r * .12); ctx.rotate(d * .45); ctx.beginPath(); ctx.roundRect(-r * .22, -r * .08, r * .44, r * .16, r * .08); ctx.fill(); ctx.restore(); }
  ctx.beginPath(); ctx.roundRect(-r * .34, r * .3, r * .68, r * .16, r * .08); ctx.fill();
  ctx.restore();
}
// cartão de post: barra de nome, linhas e rosto bravo
function postCard(x, y, w, s, a, o = {}) {
  const h = w * .62;
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot || 0); ctx.scale(o.k ?? 1, o.k ?? 1);
  rr(-w / 2, -h / 2, w, h, w * .08, '#f3f7fb');
  ctx.fillStyle = '#c9d6e3'; ctx.beginPath(); ctx.arc(-w * .36, -h * .28, w * .06, 0, 6.283); ctx.fill();
  rr(-w * .27, -h * .32, w * .32, h * .08, h * .04, '#9fb2c6');
  for (let i = 0; i < 3; i++) rr(-w * .42, -h * .08 + i * h * .16, w * (i === 2 ? .3 : .5), h * .08, h * .04, '#c9d6e3');
  angry(w * .26, h * .08, w * .14, a);
  if (o.share) { rr(w * .18, h * .3, w * .22, h * .14, h * .07, o.share > .5 ? TEAL : '#c9d6e3'); }
  ctx.restore();
}
function drawPhoneSimple(x, y, w, ang = 0) {
  const h = w * 2;
  ctx.save(); ctx.translate(x, y); ctx.rotate(ang);
  rr(-w / 2, -h / 2, w, h, w * .18, '#18263a');
  const g = ctx.createLinearGradient(0, -h / 2, 0, h / 2); g.addColorStop(0, '#2a5a8a'); g.addColorStop(1, '#11304a');
  ctx.fillStyle = g; ctx.beginPath(); ctx.roundRect(-w * .42, -h * .45, w * .84, h * .9, w * .12); ctx.fill();
  ctx.restore();
}

// ---------------------------------------------------------------------
//  CENA 1 e 10: VOCÊ NO SOFÁ
// ---------------------------------------------------------------------
const SOFA = { x: -120, y: 300 };
function sofaCam(s, a) {
  let c;
  if (s < T.t1 + TD) c = keyed([[0, -80, 40, 1.12], [C.post1, 0, -20, 1.28], [C.compartilha, 40, -60, 1.22], [T.t1, 40, -220, .9]], s);
  else c = keyed([[T.t10, 0, 0, .8], [T.t10 + .9, -20, 20, 1.05], [C.post2, 20, 0, 1.22], [C.pergunte, 60, -30, 1.35], [C.compartilhar, 40, -10, 1.28], [C.vem, 20, 0, 1.2]], s);
  if (CUR_T > RW1) c = mixCam(c, { x: 0, y: -40, z: .98 }, easeIO((CUR_T - RW1) / 1.6));
  return breathe(c, a);
}
function drawSofa(s, t, a) {
  CAM = sofaCam(s, a);
  screenSpace(); ctx.fillStyle = '#2a3550'; ctx.fillRect(0, 0, W, H);
  applyCam();
  // sala à noite: parede, janela com a cidade, luminária, tapete
  ctx.fillStyle = '#34405e'; ctx.fillRect(-3000, -2400, 6000, 2700);
  for (let i = -6; i < 7; i++) { ctx.fillStyle = 'rgba(255,255,255,.03)'; ctx.fillRect(i * 260, -2400, 120, 2700); }
  rr(260, -820, 560, 460, 26, '#1d2a4a');
  ctx.save(); ctx.beginPath(); ctx.roundRect(282, -798, 516, 416, 18); ctx.clip();
  const sk = ctx.createLinearGradient(0, -800, 0, -380); sk.addColorStop(0, '#081d2c'); sk.addColorStop(1, '#2a3f6b'); ctx.fillStyle = sk; ctx.fillRect(282, -798, 516, 416);
  const r = rng(7);
  for (let i = 0; i < 9; i++) { const bx = 290 + i * 58, bh = 120 + r() * 200; rr(bx, -380 - bh, 50, bh + 10, 4, '#14223e'); for (let j = 0; j < bh / 30; j++) if (r() < .55) rr(bx + 10 + (j % 2) * 18, -370 - bh + j * 30, 10, 12, 2, `rgba(255,217,138,${.5 + .4 * Math.sin(a * .7 + i + j)})`); }
  ctx.restore();
  rr(530, -820, 20, 460, 6, '#1d2a4a'); rr(260, -600, 560, 16, 6, '#1d2a4a');
  // luminária
  rr(-760, -260, 16, 560, 6, '#1d2433');
  ctx.fillStyle = '#ffd98a'; ctx.beginPath(); ctx.moveTo(-830, -260); ctx.lineTo(-670, -260); ctx.lineTo(-710, -380); ctx.lineTo(-790, -380); ctx.closePath(); ctx.fill();
  const lg = ctx.createRadialGradient(-750, -250, 10, -750, -250, 520); lg.addColorStop(0, 'rgba(255,217,138,.28)'); lg.addColorStop(1, 'rgba(255,217,138,0)'); ctx.fillStyle = lg; ctx.fillRect(-1300, -800, 1100, 1100);
  // chão e tapete
  ctx.fillStyle = '#5b3f36'; ctx.fillRect(-3000, 300, 6000, 1400);
  ctx.fillStyle = '#7a5a8a'; ctx.beginPath(); ctx.ellipse(-80, 420, 700, 90, 0, 0, 6.283); ctx.fill();
  // sofá
  rr(-560, -160, 880, 300, 60, '#2f8a8f');
  rr(-640, -40, 140, 300, 50, '#2a7a80'); rr(240, -40, 140, 300, 50, '#2a7a80');
  rr(-540, 90, 800, 170, 40, '#36a0a6');
  // você, sentado, segurando o celular
  const hov = s > T.t1 ? smooth(C.pergunte - .3, C.pergunte + .2, s) : 0;
  const hand = drawPerson(SOFA.x, SOFA.y, 1, s, a, { ...YOU, sit: true, phoneUp: .42, look: { x: SOFA.x + 120, y: SOFA.y - 120 }, worry: s < T.t1 ? smooth(C.revolta - .2, C.revolta + .2, s) * .8 : smooth(C.revoltar - .2, C.revoltar + .2, s) * .8, kicks: s < T.t1 ? [C.revolta, C.compartilha] : [C.revoltar, C.pergunte] });
  const ph = { x: hand.x - 6, y: hand.y - 40 };
  drawPhoneSimple(ph.x, ph.y, 70, -.08);
  // o post: aparece na tela, tremula de raiva e voa ao compartilhar
  const pT = s < T.t1 + TD ? C.post1 : C.post2, rT = s < T.t1 + TD ? C.revolta : C.revoltar;
  const k = popAt(s, pT - .1);
  if (k > 0) {
    const fly = s < T.t1 + TD ? easeInCubic((s - C.compartilha) / .7) : 0;
    const shk = kick(s - rT, .3, 30) * .12;
    const px = ph.x + 170 + fly * 500, py = ph.y - 150 - fly * 900;
    postCard(px, py, 260, s, a, { k: k * (1 - fly * .3), rot: shk - .04 + fly * .6, share: s < T.t1 + TD ? (s > C.compartilha - .25 ? 1 : 0) : hov });
    // cópias que saem junto (o começo da multiplicação)
    if (fly > 0) for (let i = 0; i < 6; i++) { const u = clamp(fly * 1.4 - i * .12); if (u > 0) postCard(px - 200 + i * 90 - u * 300 * Math.sin(i * 2), py + 300 - u * 900, 120, s, a, { k: u, rot: .3 * Math.sin(i * 5) }); }
    if (hov > 0 && s > T.t1) {
      // o polegar paira sobre o botão: pergunta
      const kq = popAt(s, C.pergunte);
      ctx.save(); ctx.translate(px + 110, py - 130); ctx.scale(kq, kq);
      ctx.fillStyle = GOLD; ctx.beginPath(); ctx.arc(0, 0, 46, 0, 6.283); ctx.fill(); txt('?', 0, 22, 62, NAVY, 0); ctx.restore();
    }
  }
  screenSpace();
  if (s < T.t1 + TD && CUR_T < RW0) { applyCam(); drawPin(SOFA.x - 230, SOFA.y - 330, .9, 'VOCÊ', s, C.voce); screenSpace(); }
  if (s > T.t1 && CUR_T < RW0) pill([{ s: 'DEPOIS DO COMPARTILHAR', px: 46, c: COL.white, ls: 6 }, { s: 'O QUE VEM?', px: 56, c: GOLD, ls: 8 }], W / 2, H - 130, s, C.compartilhar - .1, 1e9);
}

// ---------------------------------------------------------------------
//  CENA 2: MILHÕES DE POSTS PELO MUNDO
// ---------------------------------------------------------------------
const SPOTS = (() => { const r = rng(91), out = []; const boxes = [[-122, -72, 28, 48], [-100, -40, -35, 5], [-10, 30, 38, 58], [-15, 40, 5, 30], [-80, -50, -30, 0], [30, 50, 30, 50]]; while (out.length < 80) { const b = boxes[out.length % boxes.length]; out.push([lerp(b[0], b[1], r()), lerp(b[2], b[3], r()), r()]); } return out; })();
function globeCam(s, a) { return breathe(keyed([[T.t1, 0, -20, 2.6], [T.t1 + 1.2, 0, -10, 1.35], [C.nunca, 40, 0, 1.25], [C.muda, 60, 0, 1.45], [T.t2, 60, 0, 1.6]], s), a); }
function drawGlobe(s, t, a) {
  CAM = globeCam(s, a);
  screenSpace(); drawBackground(a, 0);
  const rot = earthRot(s, a);
  drawEarth(rot, a);
  // posts que pipocam por cima das luzes das cidades, cada vez mais rápido
  const grow = clamp((s - C.multiplique) / (C.todos + .6 - C.multiplique));
  SPOTS.forEach(([lon, lat, ph], i) => {
    if (i / SPOTS.length > grow) return;
    const p = geoWorld(lon, lat, rot, .02); if (p.vis < .1) return;
    const q = ws(p.x, p.y), per = 1.6 + ph, u = ((s * (1 + grow) + ph * 7) % per) / per;
    const k = spring(u * per, .45, 14) * (1 - smooth(.75, 1, u));
    if (k <= 0) return;
    ctx.save(); ctx.translate(q.x, q.y - 40 * u * CAM.z / 1.4); ctx.scale(k * CAM.z / 1.4, k * CAM.z / 1.4);
    rr(-34, -24, 68, 44, 10, '#f3f7fb'); angry(14, -2, 13, a); rr(-26, -12, 26, 7, 3, '#c9d6e3'); rr(-26, 2, 18, 7, 3, '#c9d6e3');
    ctx.beginPath(); ctx.moveTo(-6, 20); ctx.lineTo(0, 32); ctx.lineTo(6, 20); ctx.fillStyle = '#f3f7fb'; ctx.fill();
    ctx.restore();
  });
  // dois medidores: barulho (sobe sem parar) x mudança (parada)
  const ku = popAt(s, C.nunca - .1);
  if (ku > 0) {
    const noise = smooth(C.nunca, C.politica1 + .6, s) * (.92 + .04 * Math.sin(a * 9)), chg = .03 * smooth(C.nada, C.muda, s);
    ctx.save(); ctx.translate(W - 250, H / 2 + 40); ctx.scale(ku, ku);
    [[-95, noise, CORAL, 'POLÍTICA'], [95, chg, TEAL, 'MUDANÇA']].forEach(([dx, v, c, lab], i) => {
      rr(dx - 46, -300, 92, 600, 30, 'rgba(6,20,40,.62)');
      const hh = 560 * v; rr(dx - 36, 290 - hh, 72, Math.max(hh, 10), 24, c);
      if (!window.NO_TEXT) { ctx.save(); ctx.translate(dx, 350); riseText(lab, 0, 0, 22, i ? TEAL : CORAL, s, i ? C.nada : C.nunca, 1e9, { ls: 3 }); ctx.restore(); }
    });
    ctx.restore();
  }
  pill([{ s: 'MILHÕES DE PESSOAS', px: 46, c: COL.white, ls: 7 }, { s: 'TODOS OS DIAS', px: 30, c: GOLD, ls: 6, w: 600 }], W / 2 - 160, 120, s, C.milhoes, C.nunca - .2);
  pill([{ s: 'QUASE NADA MUDA', px: 50, c: COL.white, ls: 8 }], W / 2 - 160, H - 130, s, C.nada - .1, T.t2 - .1);
}

// ---------------------------------------------------------------------
//  CENA 3 e 9: A BIBLIOTECA DE JÄGER
// ---------------------------------------------------------------------
function libCam(s, a) {
  let c;
  if (s < T.t3 + TD) c = keyed([[T.t2, -100, -260, .6], [T.t2 + .9, -160, -280, .95], [C.hiper, 0, -300, .85], [C.politizacao, 200, -300, .82], [C.sem1, 260, -300, .9], [T.t3, 260, -300, .95]], s);
  else c = keyed([[T.t9, -100, -260, .6], [T.t9 + .9, -140, -280, .95], [C.sozinho, -200, -260, 1.1], [C.basta, -230, -250, 1.2]], s);
  return shake(breathe(c, a), 9 * kick(s - C.basta, .4, 18) * (s > T.t9), a);
}
function drawLibrary(s, t, a) {
  CAM = libCam(s, a);
  screenSpace(); ctx.fillStyle = '#26324a'; ctx.fillRect(0, 0, W, H);
  applyCam();
  ctx.fillStyle = '#2f3d5a'; ctx.fillRect(-3000, -2000, 6000, 2260);
  // estantes
  for (let sh = 0; sh < 2; sh++) {
    const x0 = -1300 + sh * 1900;
    rr(x0, -900, 620, 1160, 12, '#3b2f3a');
    for (let r2 = 0; r2 < 4; r2++) { rr(x0 + 20, -870 + r2 * 280, 580, 16, 4, '#2a2128'); for (let k = 0; k < 13; k++) rr(x0 + 30 + k * 44, -1100 + r2 * 280 + 250 - (k % 3) * 14, 36, 210 + (k % 3) * 14, 4, ['#ff8a7a', '#8fd8e6', '#ffd98a', '#5fc47a', '#c9d6e3'][(k + r2 + sh) % 5]); }
  }
  ctx.fillStyle = '#4a3a34'; ctx.fillRect(-3000, 260, 6000, 2000);
  // mesa com o livro
  rr(-640, 20, 640, 40, 12, '#6e4632'); rr(-600, 60, 30, 200, 8, '#5b3a2e'); rr(-70, 60, 30, 200, 8, '#5b3a2e');
  const closed = s > T.t9 ? smooth(C.basta - .25, C.basta + .1, s) : 0;
  ctx.save(); ctx.translate(-330, 18);
  if (closed < .5) { const op = 1 - closed * 2; rr(-150 * op - 8, -26, 150 * op + 8, 26, 6, '#f3efe6'); rr(0, -26, 150 * op + 8, 26, 6, '#efe6d2'); rr(-8, -30, 16, 30, 4, '#c94a3a'); }
  else { rr(-110, -40, 220, 40, 8, '#c94a3a'); rr(-100, -34, 200, 8, 4, '#ffd98a'); }
  ctx.restore();
  const hand = drawPerson(-240, 260, 1.05, s, a, { ...JAG, look: s > C.politizacao && s < T.t3 + TD ? { x: 500, y: -300 } : { x: 300, y: -200 }, reach: s > T.t9 ? { x: -330, y: -10 } : (s > C.politizacao ? { x: 200, y: -300 } : null), reachW: s > T.t9 ? smooth(C.sozinho - .6, C.sozinho, s) : smooth(C.politizacao - .4, C.politizacao, s), handR: s > T.t9 ? 'aberta' : 'aponta', smile: s > T.t9 && s < C.sozinho, kicks: s > T.t9 ? [C.inutil, C.basta] : [C.hiper, C.extrema] });
  // quadro: politização x consequências
  if (s < T.t3 + TD) {
    const kb = popAt(s, C.politizacao - .1);
    if (kb > 0) {
      ctx.save(); ctx.translate(420, -260); ctx.scale(kb, kb);
      rr(-300, -380, 600, 600, 30, '#1d2a4a');
      const v1 = easeOutCubic((s - C.extrema) / .8) * (1 + .03 * Math.sin(a * 11)), v2 = .02 * smooth(C.sem1, C.consequencias, s);
      rr(-200, 160 - 470 * v1, 150, Math.max(470 * v1, 12), 22, CORAL);
      rr(50, 160 - 470 * v2, 150, Math.max(470 * v2, 12), 22, TEAL);
      if (s > C.sem1) { const kx = popAt(s, C.consequencias); ctx.save(); ctx.translate(125, 60); ctx.scale(kx, kx); ctx.fillStyle = RED; ctx.beginPath(); ctx.arc(0, 0, 40, 0, 6.283); ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 10; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-14, -14); ctx.lineTo(14, 14); ctx.moveTo(14, -14); ctx.lineTo(-14, 14); ctx.stroke(); ctx.restore(); }
      if (!window.NO_TEXT) { ctx.save(); ctx.translate(-125, 200); riseText('POLITIZAÇÃO', 0, 0, 26, CORAL, s, C.politizacao, 1e9, { ls: 2 }); ctx.restore(); ctx.save(); ctx.translate(125, 200); riseText('CONSEQUÊNCIAS', 0, 0, 24, TEAL, s, C.sem1, 1e9, { ls: 2 }); ctx.restore(); }
      ctx.restore();
    }
  }
  screenSpace();
  if (s < T.t3 + TD) {
    pill([{ s: 'ANTON JÄGER', px: 44, c: COL.white, ls: 6 }, { s: 'HISTORIADOR', px: 26, c: GOLD, ls: 5, w: 600 }], W / 2, 110, s, C.anton - .1, C.hiper - .2);
    pill([{ s: 'HIPERPOLÍTICA', px: 76, c: COL.white, ls: 10 }], W / 2, 120, s, C.hiper, C.politizacao - .1);
    pill([{ s: 'POLITIZAÇÃO EXTREMA', px: 40, c: CORAL, ls: 5 }, { s: 'SEM CONSEQUÊNCIAS POLÍTICAS', px: 30, c: TEAL, ls: 4, w: 600 }], W / 2, H - 130, s, C.politizacao, T.t3 - .1, { pad: 20 });
  } else {
    pill([{ s: 'SE IMPORTAR NÃO É INÚTIL', px: 42, c: COL.white, ls: 5 }], W / 2, 110, s, C.inutil - .4, C.sozinho - .2, { pad: 18 });
    pill([{ s: 'MAS, SOZINHO, NÃO BASTA', px: 46, c: GOLD, ls: 6 }], W / 2, 110, s, C.sozinho, T.t10 - .1, { pad: 18 });
  }
}

// ---------------------------------------------------------------------
//  CENA 4 e 6: OS DOIS EIXOS (o ponto anda pelas eras)
// ---------------------------------------------------------------------
const OX = -520, OY = 330, AXW = 1040, AXH = 860;   // origem e tamanho dos eixos no mundo
const ERAS = [   // [deixa, x (organizar 0..1), y (importar 0..1), rótulo]
  ['seculo', .86, .86, 'SÉCULO 20'], ['despencaram', .12, .12, 'ANOS 90'], ['raiva1', .12, .64, '2008'], ['dezesseis', .1, .97, '2016']
];
function dotAt(s) {
  let x = ERAS[0][1], y = ERAS[0][2];
  for (let i = 1; i < ERAS.length; i++) { const u = easeIO((s - C[ERAS[i][0]]) / .9); x = lerp(x, ERAS[i][1], u); y = lerp(y, ERAS[i][2], u); }
  return { x: OX + x * AXW, y: OY - y * AXH };
}
function chartCam(s, a) {
  let c;
  if (s < T.t4 + TD) c = keyed([[T.t3, 0, -60, .5], [T.t3 + .9, 0, -60, .72], [C.seculo, 40, -80, .75], [T.t4, 200, -300, 1.0]], s);
  else c = keyed([[T.t5, 0, -60, .85], [T.t5 + .9, 0, -60, .72], [C.raiva1, -40, -100, .75], [C.dezesseis, -100, -180, .8], [C.redes, -200, -300, 1.0], [T.t6, -300, -380, 1.3]], s);
  const amp = s > C.dezesseis ? 4 + 10 * smooth(C.dezesseis, C.redes, s) : 0;
  return shake(breathe(c, a), amp, a);
}
function drawChart(s, t, a) {
  CAM = chartCam(s, a);
  screenSpace(); drawBackground(a, .25);
  applyCam();
  // queda do muro de Berlim (anos 90) e gráfico da crise de 2008, ao fundo
  if (s > T.t5 && s < C.crise + 2) {
    const fall = smooth(C.muro, C.muro + .9, s), al = 1 - smooth(C.despencaram + .5, C.despencaram + 1.2, s);
    if (al > 0) { ctx.save(); ctx.globalAlpha = al * popAt(s, C.queda - .3); const r = rng(5);
      for (let row = 0; row < 6; row++) for (let k = 0; k < 6; k++) { const bx = 620 + k * 92 + (row % 2) * 46, by = -40 - row * 52, d = r(); const f = clamp(fall * 1.6 - d * .6); ctx.save(); ctx.translate(bx, by + 900 * f * f); ctx.rotate(f * (d - .5) * 3); rr(-42, -22, 84, 44, 6, row % 2 ? '#9aa3ad' : '#b9c2cc'); ctx.restore(); }
      ctx.restore(); }
    const kc = popAt(s, C.crise - .1) * (1 - smooth(C.raiva1 + .6, C.raiva1 + 1.2, s));
    if (kc > 0) { ctx.save(); ctx.globalAlpha = kc; ctx.lineWidth = 16; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = RED;
      const pts = [[560, -500], [660, -560], [740, -520], [820, -600], [900, -560], [960, -200], [1040, 60], [1120, 20]], u = clamp((s - C.crise) / .9) * (pts.length - 1);
      ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i <= Math.floor(u); i++) ctx.lineTo(pts[i][0], pts[i][1]); const fi = Math.floor(u), fr = u - fi; if (fi < pts.length - 1) ctx.lineTo(lerp(pts[fi][0], pts[fi + 1][0], fr), lerp(pts[fi][1], pts[fi + 1][1], fr)); ctx.stroke(); ctx.restore(); }
  }
  // eixos: barras arredondadas que crescem
  const ky = easeOutCubic((s - C.dois_eixos()) / .6), kx = easeOutCubic((s - C.dois_eixos() - .25) / .6);
  rr(OX - 10, OY - AXH * ky, 20, AXH * ky + 10, 10, 'rgba(143,216,230,.85)');
  rr(OX - 10, OY - 10, AXW * kx + 10, 20, 10, 'rgba(143,216,230,.85)');
  // grade suave
  for (let i = 1; i < 4; i++) { ctx.fillStyle = 'rgba(143,216,230,.08)'; ctx.fillRect(OX, OY - AXH * i / 4 * ky - 2, AXW * kx, 4); ctx.fillRect(OX + AXW * i / 4 * kx - 2, OY - AXH * ky, 4, AXH * ky); }
  // rótulos dos eixos
  const noOrg = s > T.t5 ? kick(s - C.nao1, .35, 22) : 0;
  if (!window.NO_TEXT) {
    ctx.save(); ctx.translate(OX - 60, OY - AXH / 2); ctx.rotate(-Math.PI / 2); riseText('O QUANTO A GENTE SE IMPORTA', 0, 0, 34, CORAL, s, C.importa - .3, 1e9, { ls: 4 }); ctx.restore();
    ctx.save(); ctx.translate(OX + AXW / 2 + noOrg * 30, OY + 80); riseText('O QUANTO A GENTE SE ORGANIZA', 0, 0, 34, s > C.nao1 - .1 && s < C.dezesseis ? RED : TEAL, s, C.organiza - .3, 1e9, { ls: 4 }); ctx.restore();
  }
  // o ponto e o rastro das eras
  if (s > C.seculo - .1) {
    ERAS.forEach(([key, ex, ey, lab], i) => {
      if (s < C[key] - .1 || window.NO_TEXT) return;
      const px = OX + ex * AXW, py = OY - ey * AXH, k = popAt(s, C[key] + .3);
      ctx.save(); ctx.translate(px, py); ctx.scale(k, k); ctx.globalAlpha = i === ERAS.length - 1 || s < (C[ERAS[i + 1]?.[0]] ?? 1e9) ? 1 : .45;
      ctx.fillStyle = 'rgba(255,255,255,.2)'; ctx.beginPath(); ctx.arc(0, 0, 18, 0, 6.283); ctx.fill();
      ctx.font = FONT(700, 34); ctx.letterSpacing = '4px'; const tw = ctx.measureText(lab).width + 50, side = ex > .5 ? -1 : 1;
      rr(side > 0 ? 40 : -40 - tw, -36, tw, 60, 30, 'rgba(6,20,40,.7)'); txt(lab, side > 0 ? 40 + tw / 2 : -40 - tw / 2, 8, 34, GOLD, 4);
      ctx.restore();
    });
    const d = dotAt(s), k = popAt(s, C.seculo), rage = s > C.raiva1 ? smooth(C.raiva1, C.raiva2 + .5, s) : 0;
    const jit = rage * 8;
    ctx.save(); ctx.translate(d.x + jit * Math.sin(a * 53), d.y + jit * Math.cos(a * 41)); ctx.scale(k, k);
    const gg = ctx.createRadialGradient(0, 0, 0, 0, 0, 110 + 60 * rage); gg.addColorStop(0, `rgba(255,95,109,${.25 + .35 * rage})`); gg.addColorStop(1, 'rgba(255,95,109,0)'); ctx.fillStyle = gg; ctx.beginPath(); ctx.arc(0, 0, 170, 0, 6.283); ctx.fill();
    ctx.fillStyle = rage > .3 ? RED : GOLD; ctx.beginPath(); ctx.arc(0, 0, 34, 0, 6.283); ctx.fill();
    ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.arc(-9, -9, 9, 0, 6.283); ctx.fill();
    ctx.restore();
    // pessoas indo embora (anos 90)
    if (s > C.pessoas2 - .2 && s < C.crise + .5) {
      const u = (s - C.pessoas2 + .2) / 2.2;
      for (let i = 0; i < 5; i++) { const al = 1 - smooth(.7, 1, u); if (al <= 0) break; const x = OX + 150 + i * 70 + u * 900, y = OY - 30; ctx.save(); ctx.globalAlpha = al; ctx.translate(x, y); ctx.fillStyle = '#c9d6e3'; ctx.beginPath(); ctx.arc(0, -70, 16, 0, 6.283); ctx.fill(); rr(-14, -52, 28, 46, 12, '#c9d6e3'); ctx.restore(); }
      const kh = popAt(s, C.casa - .1); if (kh > 0) { ctx.save(); ctx.translate(OX + 1100, OY - 10); ctx.scale(kh, kh); rr(-70, -100, 140, 100, 8, '#ffd98a'); ctx.fillStyle = CORAL; ctx.beginPath(); ctx.moveTo(-90, -96); ctx.lineTo(0, -170); ctx.lineTo(90, -96); ctx.closePath(); ctx.fill(); rr(-18, -60, 36, 60, 6, '#8a5a3c'); ctx.restore(); }
    }
    // Trump e Brexit: etiquetas que estouram ao lado do ponto
    [['TRUMP', C.trump, -1], ['BREXIT', C.brexit, 1]].forEach(([lab, t0, sd]) => {
      if (window.NO_TEXT) return;
      const k2 = popAt(s, t0 - .05) * (1 - smooth(T.t6 - .2, T.t6, s)); if (k2 <= 0) return;
      ctx.save(); ctx.translate(d.x + 220 + (sd > 0 ? 260 : 0), d.y - 90 + sd * 60); ctx.scale(k2, k2); ctx.rotate(sd * .05);
      ctx.font = FONT(700, 40); ctx.letterSpacing = '5px'; const tw = ctx.measureText(lab).width + 60; rr(-tw / 2, -40, tw, 72, 36, sd > 0 ? '#3a5fcf' : RED); txt(lab, 0, 13, 40, '#ffffff', 5); ctx.restore();
    });
  }
  screenSpace();
  pill([{ s: 'DOIS EIXOS', px: 46, c: COL.white, ls: 8 }], W / 2, 110, s, C.eixos - .2, C.seculo - .2);
  pill([{ s: 'POLÍTICA DE MASSAS', px: 42, c: GOLD, ls: 6 }], W / 2, 110, s, C.alto, T.t4 - .1);
  pill([{ s: 'A POLÍTICA VIROU GESTÃO', px: 42, c: COL.white, ls: 6 }], W / 2, 110, s, C.gestao - .1, C.crise - .2);
  pill([{ s: 'A RAIVA VOLTOU', px: 46, c: CORAL, ls: 7 }, { s: 'AS ORGANIZAÇÕES, NÃO', px: 32, c: COL.white, ls: 5, w: 600 }], W / 2, 120, s, C.raiva1, C.dezesseis - .2);
  pill([{ s: 'A RAIVA ACELEROU NAS REDES', px: 44, c: CORAL, ls: 6 }], W / 2, H - 130, s, C.acelerou - .2, T.t6 - .1);
}
C.dois_eixos = () => cue('dois', 1);

// ---------------------------------------------------------------------
//  CENA 5: O SALÃO DO SÉCULO 20
// ---------------------------------------------------------------------
const SIGNS = [['SINDICATO', 'sindicatos', CORAL], ['PARTIDO', 'partidos', '#3a5fcf'], ['IGREJA', 'igrejas', '#9a6ad0'], ['CLUBE', 'clubes', '#2f8a8f']];
const CROWD = (() => { const r = rng(33), out = []; for (let row = 0; row < 3; row++) for (let i = 0; i < 7; i++) out.push({ x: -840 + i * 280 + (row % 2) * 140 + r() * 40, y: 260 + row * 120, sc: .62 + row * .08, d: r(), shirt: ['#ff8a7a', '#ffd98a', '#8fd8e6', '#5fc47a', '#c9d6e3', '#9a6ad0'][Math.floor(r() * 6)], hair: ['#3b2a2e', '#1b1b22', '#c9a36a', '#9aa3ad'][Math.floor(r() * 4)], st: ['curto', 'franja', 'coque', 'chanel', 'topete', 'careca'][Math.floor(r() * 6)] }); return out; })();
function hallCam(s, a) { return breathe(keyed([[T.t4, 0, -300, .6], [T.t4 + .9, -200, -380, .78], [C.clubes, 200, -380, .78], [C.multidoes, 0, -120, .68], [T.t5, 0, -120, .72]], s), a); }
function drawHall(s, t, a) {
  CAM = hallCam(s, a);
  screenSpace(); ctx.fillStyle = '#6a4a3a'; ctx.fillRect(0, 0, W, H);
  applyCam();
  ctx.fillStyle = '#8a5f45'; ctx.fillRect(-3000, -2000, 6000, 2300);
  for (let i = -8; i < 9; i++) rr(i * 300 - 20, -1400, 40, 1700, 8, '#7a523c');
  ctx.fillStyle = '#5b3a2e'; ctx.fillRect(-3000, 260, 6000, 2000);
  // faixas: uma por instituição, na sua palavra
  SIGNS.forEach(([lab, key, c], i) => {
    const k = popAt(s, C[key] - .05); if (k <= 0) return;
    const x = -900 + i * 600, y = -620;
    ctx.save(); ctx.translate(x, y - 80 * (1 - k)); ctx.scale(k, k); ctx.rotate(.03 * Math.sin(a * 1.3 + i));
    rr(-250, -80, 500, 160, 22, c);
    if (!window.NO_TEXT) txt(lab, 0, 22, 62, '#ffffff', 6);
    ctx.restore();
  });
  // a multidão chega
  CROWD.forEach((p, i) => {
    const t0 = C.multidoes - .4 + p.d * .7, k = popAt(s, t0);
    if (k <= 0) return;
    ctx.save(); ctx.globalAlpha = clamp(k * 2);
    drawPerson(p.x, p.y + 60 * (1 - clamp(k)), p.sc, s, a + i, { pal: { shirt: p.shirt, hair: p.hair, hairHi: p.hair }, hairStyle: p.st, look: { x: 0, y: -600 }, smile: true, reach: i % 3 === 0 ? { x: p.x + 40, y: p.y - 420 * p.sc } : null, handR: 'punho', kicks: [C.semana] });
    ctx.restore();
  });
  screenSpace();
  pill([{ s: 'SÉCULO 20', px: 46, c: COL.white, ls: 8 }], W / 2, H - 120, s, T.t4 + .2, C.multidoes - .2);
  pill([{ s: 'MULTIDÕES TODA SEMANA', px: 44, c: GOLD, ls: 6 }], W / 2, H - 120, s, C.multidoes, T.t5 - .1);
}

// ---------------------------------------------------------------------
//  CENA 7: A RUA E AS HASHTAGS
// ---------------------------------------------------------------------
const TAGS = [['#BASTA', -520, -620], ['#ACORDA', 200, -720], ['#AGORAVAI', 620, -560], ['#JUSTIÇA', -180, -860], ['#FORA', 900, -820], ['#VERGONHA', -880, -820]];
function streetCam(s, a) { return breathe(keyed([[T.t6, 0, -400, .5], [T.t6 + .9, 0, -360, .66], [C.protestos, 0, -200, .72], [C.semanas, 0, -260, .66], [T.t7, 0, -300, .7]], s), a); }
function drawStreet(s, t, a) {
  CAM = streetCam(s, a);
  screenSpace(); ctx.fillStyle = '#1d2a4a'; ctx.fillRect(0, 0, W, H);
  applyCam();
  const sk = ctx.createLinearGradient(0, -1600, 0, 0); sk.addColorStop(0, '#102348'); sk.addColorStop(1, '#3a4f7a'); ctx.fillStyle = sk; ctx.fillRect(-4000, -3000, 8000, 3010);
  const r = rng(12); for (let i = 0; i < 14; i++) { const bx = -1800 + i * 270, bh = 400 + r() * 500; rr(bx, -bh, 240, bh + 10, 8, i % 2 ? '#26365a' : '#2c3e66'); for (let j = 0; j < bh / 80 - 1; j++) for (let q = 0; q < 3; q++) if (r() < .5) rr(bx + 30 + q * 70, -bh + 40 + j * 80, 40, 44, 4, 'rgba(255,217,138,.55)'); }
  ctx.fillStyle = '#3a3f4f'; ctx.fillRect(-4000, 0, 8000, 2000); ctx.fillStyle = '#4a5064'; ctx.fillRect(-4000, 0, 8000, 40);
  // multidão com cartazes: chega em "protestos", vai embora em "semanas"
  const leave = smooth(C.semanas - .2, C.outro, s);
  CROWD.forEach((p, i) => {
    const k = popAt(s, C.protestos - .2 + p.d * .6); if (k <= 0) return;
    const side = p.x < 0 ? -1 : 1, x = p.x + side * leave * 1800;
    ctx.save(); ctx.globalAlpha = clamp(k * 2) * (1 - smooth(.6, 1, leave));
    const hand = drawPerson(x, p.y + 20, p.sc, s, a + i * .7, { pal: { shirt: p.shirt, hair: p.hair, hairHi: p.hair }, hairStyle: p.st, look: { x: x, y: -900 }, reach: { x: x + 30, y: p.y - 430 * p.sc }, handR: 'punho', kicks: [C.lotam] });
    rr(hand.x - 4, hand.y - 70 * p.sc, 8, 80 * p.sc, 4, '#8a5a3c');
    rr(hand.x - 75 * p.sc, hand.y - 140 * p.sc, 150 * p.sc, 80 * p.sc, 10, ['#f3f7fb', '#ffd98a', '#ff8a7a'][i % 3]);
    ctx.restore();
  });
  // hashtags: estouram em bolhas; depois de semanas, todas trocam por um assunto novo
  TAGS.forEach(([lab, x, y], i) => {
    const t0 = i === 0 ? C.hashtags - .05 : C.explodem + i * .12, k = popAt(s, t0) * (1 - smooth(C.outro - .25, C.outro + .05, s));
    const fl = 14 * Math.sin(a * 1.4 + i);
    if (k > 0) { ctx.save(); ctx.translate(x, y + fl); ctx.scale(k, k); ctx.font = FONT(700, 54); ctx.letterSpacing = '4px'; const tw = ctx.measureText(lab).width + 70; rr(-tw / 2, -50, tw, 90, 45, i % 2 ? CORAL : '#3a5fcf'); if (!window.NO_TEXT) txt(lab, 0, 18, 54, '#ffffff', 4); ctx.restore(); }
  });
  const kn = popAt(s, C.outro);
  if (kn > 0) { ctx.save(); ctx.translate(0, -700); ctx.scale(kn, kn); ctx.font = FONT(700, 64); ctx.letterSpacing = '5px'; const lab = '#OUTROASSUNTO', tw = ctx.measureText(lab).width + 80; rr(-tw / 2, -58, tw, 104, 52, GOLD); if (!window.NO_TEXT) txt(lab, 0, 22, 64, NAVY, 5); ctx.restore(); }
  screenSpace();
  pill([{ s: 'EM POUCAS SEMANAS', px: 44, c: COL.white, ls: 6 }], W / 2, H - 120, s, C.semanas - .3, T.t7 - .1);
}

// ---------------------------------------------------------------------
//  CENA 8: SINDICATO x LIKE
// ---------------------------------------------------------------------
function splitCam(s, a) { return breathe(keyed([[T.t7, 0, -100, .6], [T.t7 + .9, 0, -100, .8], [C.sindicato, -300, -100, .9], [C.paciencia, -300, -100, .95], [C.like, 380, -100, 1.0], [T.t8, 380, -100, 1.05]], s), a); }
function drawSplit(s, t, a) {
  CAM = splitCam(s, a);
  screenSpace(); ctx.fillStyle = '#1d2a4a'; ctx.fillRect(0, 0, W, H);
  applyCam();
  rr(-1400, -900, 1380, 1500, 0, '#8a5f45'); rr(20, -900, 1380, 1500, 0, '#26365a');
  rr(-20, -900, 40, 1500, 0, GOLD);
  // esquerda: o que um sindicato pede
  const items = [['REUNIÃO', 'reuniao'], ['MENSALIDADE', 'mensalidade'], ['ANOS', 'anos2']];
  items.forEach(([lab, key], i) => {
    const k = popAt(s, C[key] - .05); if (k <= 0) return;
    const x = -1060 + i * 380, y = -260;
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k);
    rr(-150, -170, 300, 300, 40, 'rgba(6,20,40,.4)');
    if (i === 0) { for (let c2 = 0; c2 < 3; c2++) { rr(-110 + c2 * 80, -40, 60, 70, 10, '#ffd98a'); rr(-110 + c2 * 80, -90, 60, 50, 10, '#ffe8b8'); } }
    if (i === 1) { ctx.fillStyle = GOLD; ctx.beginPath(); ctx.arc(0, -30, 80, 0, 6.283); ctx.fill(); txt('$', 0, 0, 90, '#8a5f45', 0); }
    if (i === 2) { const n = Math.floor(clamp((s - C.anos2) / 1.2) * 20); rr(-90, -120, 180, 170, 20, '#f3f7fb'); rr(-90, -120, 180, 46, 20, CORAL); txt(String(1 + n), 0, 20, 84, NAVY, 0); }
    if (!window.NO_TEXT) { ctx.save(); ctx.translate(0, 105); riseText(lab, 0, 0, 30, '#ffffff', s, C[key], 1e9, { ls: 3 }); ctx.restore(); }
    ctx.restore();
  });
  // direita: um like
  ctx.save(); ctx.translate(560, -120);
  drawPhoneSimple(0, 0, 260, 0);
  postCard(0, -90, 200, s, a, { k: 1 });
  const kl = popAt(s, C.like + .1), tap = kick(s - C.like - .05, .4, 18);
  ctx.save(); ctx.translate(0, 120); ctx.scale(1 + .4 * kl - .1 * tap, 1 + .4 * kl - .1 * tap);
  ctx.fillStyle = kl > .1 ? CORAL : '#9fb2c6'; ctx.beginPath(); ctx.moveTo(0, 30); ctx.bezierCurveTo(-70, -20, -40, -70, 0, -36); ctx.bezierCurveTo(40, -70, 70, -20, 0, 30); ctx.fill();
  ctx.restore();
  // cronômetro de 1 segundo
  const kt = popAt(s, C.segundo - .05);
  if (kt > 0) { ctx.save(); ctx.translate(250, -260); ctx.scale(kt, kt); ctx.fillStyle = GOLD; ctx.beginPath(); ctx.arc(0, 0, 80, 0, 6.283); ctx.fill(); txt('1 s', 0, 18, 52, NAVY, 2); ctx.restore(); }
  ctx.restore();
  screenSpace();
  pill([{ s: 'FÁCIL DE ENTRAR', px: 46, c: COL.white, ls: 7 }, { s: 'FÁCIL DE SAIR', px: 46, c: GOLD, ls: 7 }], W / 2, 140, s, C.facil1, C.sindicato - .2);
  pill([{ s: 'SINDICATO', px: 40, c: COL.white, ls: 6 }], W * .27, H - 120, s, C.sindicato, T.t8 - .1, { pad: 18 });
  pill([{ s: 'LIKE', px: 40, c: COL.white, ls: 6 }], W * .75, H - 120, s, C.like, T.t8 - .1, { pad: 18 });
}

// ---------------------------------------------------------------------
//  CENA 9: A ENERGIA QUE SOME
// ---------------------------------------------------------------------
const SPARKS = (() => { const r = rng(55), o = []; for (let i = 0; i < 70; i++) o.push([r() * 1800 - 900, r(), r()]); return o; })();
function boxesCam(s, a) { return breathe(keyed([[T.t8, 0, -100, .55], [T.t8 + .9, 0, -150, .72], [C.lei, -100, -250, .8], [C.voto, 100, -250, .8], [T.t9, 0, -250, .85]], s), a); }
function drawBoxes(s, t, a) {
  CAM = boxesCam(s, a);
  screenSpace(); drawBackground(a, .4);
  applyCam();
  // celulares embaixo soltando faíscas que sobem e se apagam no meio do caminho
  for (let i = 0; i < 9; i++) drawPhoneSimple(-1000 + i * 250, 560, 90, .1 * Math.sin(i));
  SPARKS.forEach(([x0, ph, sp]) => {
    const per = 1.6 + sp, u = ((s - T.t8 + ph * per) % per) / per;
    const x = x0 + 60 * Math.sin(a * 2 + ph * 9), y = 480 - u * 900;
    const al = Math.sin(u * Math.PI) * (1 - smooth(.55, .8, u));
    if (al <= 0) return;
    ctx.fillStyle = `rgba(255,217,138,${al})`; ctx.beginPath(); ctx.arc(x, y, 10 + 8 * sp, 0, 6.283); ctx.fill();
  });
  // três caixas que continuam vazias
  [['LEI', 'lei'], ['SALÁRIO', 'salario'], ['VOTO', 'voto']].forEach(([lab, key], i) => {
    const k = popAt(s, C[key] - .05); if (k <= 0) return;
    const x = -520 + i * 520, y = -620;
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k);
    rr(-170, -140, 340, 260, 28, 'rgba(255,255,255,.12)'); rr(-150, -120, 300, 220, 22, 'rgba(6,20,40,.6)');
    if (!window.NO_TEXT) { ctx.save(); ctx.translate(0, 200); riseText(lab, 0, 0, 44, COL.white, s, C[key], 1e9, { ls: 6 }); ctx.restore(); }
    txt('0', 0, 30, 110, 'rgba(255,255,255,.25)', 0);
    ctx.restore();
  });
  screenSpace();
  pill([{ s: 'TANTA ENERGIA', px: 46, c: GOLD, ls: 7 }], W / 2, H - 120, s, C.energia - .1, T.t9 - .1);
}

// =====================================================================
//  COMPOSIÇÃO
// =====================================================================
const SCENES = { sofa: drawSofa, globe: drawGlobe, lib: drawLibrary, chart: drawChart, hall: drawHall, street: drawStreet, split: drawSplit, boxes: drawBoxes };
const TRANS = [
  { s: T.t1, from: 'sofa', to: 'globe', mode: 'close' },
  { s: T.t2, from: 'globe', to: 'lib', mode: 'open' },
  { s: T.t3, from: 'lib', to: 'chart', mode: 'open' },
  { s: T.t4, from: 'chart', to: 'hall', mode: 'open' },
  { s: T.t5, from: 'hall', to: 'chart', mode: 'close' },
  { s: T.t6, from: 'chart', to: 'street', mode: 'open' },
  { s: T.t7, from: 'street', to: 'split', mode: 'open' },
  { s: T.t8, from: 'split', to: 'boxes', mode: 'close' },
  { s: T.t9, from: 'boxes', to: 'lib', mode: 'open' },
  { s: T.t10, from: 'lib', to: 'sofa', mode: 'open' }
];
function sceneAt(s) { let n = 'sofa'; for (const tr of TRANS) if (s >= tr.s + TD) n = tr.to; return n; }
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
  pill([{ s: 'HIPERPOLÍTICA', px: 104, c: COL.white, ls: 10 }, { s: 'MUITA POLITIZAÇÃO, POUCA CONSEQUÊNCIA', px: 36, c: TEAL, ls: 5, w: 600 }], W / 2, 190, t, t0);
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
