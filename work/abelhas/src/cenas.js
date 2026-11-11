// =====================================================================
//  SALVA OU CONDENA? Abelhas-robôs
// =====================================================================
const T = {
  t1: C.parece - .1,          // jardim -> globo (recuo)
  t2: C.so - .1,              // globo -> jardim (solução)
  t3: C.pesquisadores - .15,  // jardim -> laboratório
  t4: C.futuro - .1,          // laboratório -> fazenda vertical
  t5: C.agora - .1,           // fazenda -> laboratório (e se...?)
  t6: C.quem - .1             // laboratório -> estúdio (culpa, lista, balança)
};
const TD = .5;
const earthRot = (s, a) => (-40 - a * .55) * D2R;
const SUBSOLAR = [-40, 8];
const HACK = () => C.hackeia;

// ---------------------------------------------------------------------
//  PERSONAGENS: abelha de verdade, abelha-robô (mascote), robô do MIT
// ---------------------------------------------------------------------
function drawBee(x, y, sc, a, ph) {
  ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc); ctx.rotate(.15 * Math.sin(a * 3 + ph));
  const wf = Math.sin(a * 60 + ph);
  ctx.fillStyle = 'rgba(255,255,255,.75)';
  ctx.beginPath(); ctx.ellipse(-6, -16, 12, 7 + 4 * wf, -.5, 0, 6.283); ctx.ellipse(8, -16, 12, 7 - 4 * wf, .5, 0, 6.283); ctx.fill();
  ctx.fillStyle = '#ffd98a'; ctx.beginPath(); ctx.ellipse(0, 0, 22, 15, 0, 0, 6.283); ctx.fill();
  ctx.save(); ctx.beginPath(); ctx.ellipse(0, 0, 22, 15, 0, 0, 6.283); ctx.clip();
  ctx.fillStyle = '#3a2a2e'; for (const sx of [-6, 6]) ctx.fillRect(sx - 3, -16, 6, 32); ctx.restore();
  ctx.fillStyle = '#3a2a2e'; ctx.beginPath(); ctx.arc(22, -2, 8, 0, 6.283); ctx.fill();
  ctx.restore();
}
function drawRoboBee(x, y, sc, s, a, o = {}) {
  let sq = 0; for (const k of (o.kicks || [])) sq += kick(s - k, .45, 14) * .18;
  const bob = 8 * Math.sin(a * 2.4);
  ctx.save(); ctx.translate(x, y + bob); ctx.scale(sc * (1 + sq * .8), sc * (1 - sq)); ctx.rotate(.05 * Math.sin(a * 1.7) + (o.tilt || 0));
  const wf = Math.sin(a * 50);
  // asas de metal translúcidas
  ctx.fillStyle = 'rgba(200,240,255,.55)';
  ctx.save(); ctx.translate(-14, -40); ctx.rotate(-.5 + .25 * wf); ctx.beginPath(); ctx.ellipse(-20, 0, 34, 16, 0, 0, 6.283); ctx.fill(); ctx.restore();
  ctx.save(); ctx.translate(14, -40); ctx.rotate(.5 - .25 * wf); ctx.beginPath(); ctx.ellipse(20, 0, 34, 16, 0, 0, 6.283); ctx.fill(); ctx.restore();
  // corpo com listras
  ctx.fillStyle = '#c9d6e3'; ctx.beginPath(); ctx.roundRect(-44, -36, 88, 74, 34); ctx.fill();
  ctx.save(); ctx.beginPath(); ctx.roundRect(-44, -36, 88, 74, 34); ctx.clip();
  ctx.fillStyle = '#ffd98a'; ctx.fillRect(-44, -10, 88, 14); ctx.fillRect(-44, 16, 88, 12);
  ctx.restore();
  // visor e olhos
  const hacked = o.hacked || 0;
  ctx.fillStyle = '#0a1c2c'; ctx.beginPath(); ctx.roundRect(-30, -30, 60, 26, 13); ctx.fill();
  const lx = o.look ? clamp((o.look.x - x) / 300, -1, 1) * 6 : 0, ly = o.look ? clamp((o.look.y - y) / 300, -1, 1) * 3 : 0;
  const bl = blink(a, .2);
  const ec = hacked > .5 ? '#ff5f6d' : '#8fecff';
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (const d of [-1, 1]) {
    const g = ctx.createRadialGradient(d * 12 + lx, -17 + ly, 0, d * 12 + lx, -17 + ly, 16);
    g.addColorStop(0, ec); g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(d * 12 + lx, -17 + ly, 16, 0, 6.283); ctx.fill();
  }
  ctx.restore();
  ctx.fillStyle = ec;
  for (const d of [-1, 1]) { ctx.beginPath(); ctx.ellipse(d * 12 + lx, -17 + ly, 5, 6 * (1 - bl * .9) * (hacked > .5 ? .55 : 1), 0, 0, 6.283); ctx.fill(); }
  // antena com luz piscando
  ctx.fillStyle = '#8a9bb5'; ctx.beginPath(); ctx.roundRect(-2, -62, 4, 28, 2); ctx.fill();
  ctx.fillStyle = (Math.floor(a * 2.5) % 2) ? (hacked > .5 ? '#ff5f6d' : '#8fd8e6') : '#ffd98a'; ctx.beginPath(); ctx.arc(0, -64, 6, 0, 6.283); ctx.fill();
  // ferrão
  ctx.fillStyle = '#8a9bb5'; ctx.beginPath(); ctx.moveTo(-8, 36); ctx.lineTo(8, 36); ctx.lineTo(0, 52); ctx.closePath(); ctx.fill();
  // braço que aponta para si mesmo
  if (o.point) {
    ctx.fillStyle = '#c9d6e3'; ctx.save(); ctx.translate(40, 10); ctx.rotate(lerp(.6, 2.6, o.point));
    ctx.beginPath(); ctx.roundRect(-5, 0, 10, 34, 5); ctx.fill(); ctx.beginPath(); ctx.arc(0, 36, 8, 0, 6.283); ctx.fill(); ctx.restore();
  }
  ctx.restore();
}
function drawMitBot(x, y, sc, a, tether = true) {
  if (tether) { ctx.fillStyle = 'rgba(201,214,227,.7)'; ctx.fillRect(x - 1.5, y - 2000, 3, 2000 - 20 * sc); }
  ctx.save(); ctx.translate(x, y + 6 * Math.sin(a * 3)); ctx.scale(sc, sc);
  for (let k = 0; k < 4; k++) {
    const ang = k * Math.PI / 2 + Math.PI / 4;
    ctx.save(); ctx.rotate(ang);
    ctx.fillStyle = '#8a9bb5'; ctx.beginPath(); ctx.roundRect(0, -4, 44, 8, 4); ctx.fill();
    ctx.translate(44, 0);
    const wf = Math.sin(a * 70 + k);
    ctx.fillStyle = 'rgba(200,240,255,.6)'; ctx.beginPath(); ctx.ellipse(22, 0, 26, 10 + 6 * wf, 0, 0, 6.283); ctx.fill();
    ctx.restore();
  }
  ctx.fillStyle = '#ffd98a'; ctx.beginPath(); ctx.roundRect(-16, -16, 32, 32, 10); ctx.fill();
  ctx.fillStyle = '#ff8a7a'; ctx.beginPath(); ctx.arc(0, 0, 6, 0, 6.283); ctx.fill();
  ctx.restore();
}

// ---------------------------------------------------------------------
//  CENA 1: O JARDIM
// ---------------------------------------------------------------------
const FLOWERS = (() => { const r = rng(12), a = []; const cols = ['#ff8a7a', '#ffd98a', '#8fd8e6', '#f3f7fb', '#ff8a7a', '#ffd98a', '#8fd8e6', '#ff8a7a', '#ffd98a']; for (let i = 0; i < 9; i++) a.push({ x: -880 + i * 220 + (r() - .5) * 60, h: 180 + r() * 160, c: cols[i], ph: r() * 6 }); return a; })();
const REVIVE = 4;
function wilt(s) { return smooth(C.mais + .3, C.flores + .6, s); }
function gardenCam(s, a) {
  let c;
  if (s < T.t1 + TD) {
    c = keyed([[0, 0, -260, 1.25], [C.mais, 0, -250, 1.1], [C.flores + .2, 0, -200, .95], [C.comida - .1, 0, 80, .95], [C.tres, 0, 120, 1.0], [T.t1, 0, 60, .9]], s);
  } else {
    const fx = FLOWERS[REVIVE].x;
    c = keyed([[T.t2, 0, -100, .7], [T.t2 + .8, fx * .5, -220, .95], [C.robos, fx, -320, 1.35], [T.t3 - .4, fx, -330, 1.5]], s);
    c = mixCam(c, { x: fx, y: -330, z: 6 }, easeInCubic((s - (T.t3 - .4)) / (.4 + TD)));
  }
  if (CUR_T > RW1) c = mixCam(c, { x: FLOWERS[REVIVE].x, y: -260, z: .85 }, easeIO((CUR_T - RW1) / 1.6));
  c = breathe(c, a);
  return shake(c, 8 * kick(s - C.mais, .4, 20), a);
}
function drawGarden(s, t, a) {
  CAM = gardenCam(s, a);
  screenSpace(); ctx.fillStyle = '#4dc7eb'; ctx.fillRect(0, 0, W, H);
  applyCam();
  const w = wilt(s);
  const sky = ctx.createLinearGradient(0, -1800, 0, 0);
  sky.addColorStop(0, w > .5 ? '#2d6f9a' : '#1a66b8'); sky.addColorStop(1, w > .5 ? '#d7d0b0' : '#ffe3a8');
  ctx.fillStyle = sky; ctx.fillRect(-6000, -4000, 12000, 4100);
  ctx.fillStyle = 'rgba(255,247,220,.9)'; ctx.beginPath(); ctx.arc(700, -900, 90, 0, 6.283); ctx.fill();
  // colinas
  ctx.fillStyle = w > .5 ? '#8aa86a' : '#5fc47a'; ctx.beginPath(); ctx.ellipse(-700, 120, 1600, 420, 0, Math.PI, 0); ctx.fill();
  ctx.fillStyle = w > .5 ? '#7a9a5c' : '#48ad6b'; ctx.beginPath(); ctx.ellipse(900, 160, 1700, 380, 0, Math.PI, 0); ctx.fill();
  ctx.fillStyle = w > .5 ? '#6f8f52' : '#3a9d62'; ctx.fillRect(-6000, 120, 12000, 3000);
  // flores
  const revived = spring(s - (C.robos + .5), .5, 11) * (s > T.t2 ? 1 : 0);
  FLOWERS.forEach((f, i) => {
    const ww = i === REVIVE ? w * (1 - revived) : w;
    ctx.save(); ctx.translate(f.x, 140);
    ctx.fillStyle = ww > .5 ? '#7a8a5c' : '#48ad6b'; ctx.beginPath(); ctx.roundRect(-6, -f.h, 12, f.h, 6); ctx.fill();
    ctx.beginPath(); ctx.ellipse(-24, -f.h * .45, 26, 10, -.5, 0, 6.283); ctx.fill();
    ctx.translate(0, -f.h); ctx.rotate(ww * 1.3 + .05 * Math.sin(a + f.ph));
    const col = ww > .5 ? '#b8a88a' : f.c;
    for (let k = 0; k < 6; k++) { const an = k * 1.047; ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(Math.cos(an) * 30, Math.sin(an) * 30, 24 * (1 - ww * .3), 16, an, 0, 6.283); ctx.fill(); }
    ctx.fillStyle = ww > .5 ? '#8a7a5c' : '#ffd98a'; ctx.beginPath(); ctx.arc(0, 0, 20, 0, 6.283); ctx.fill();
    ctx.restore();
  });
  // abelhas: somem uma a uma em "mais"
  for (let i = 0; i < 8; i++) {
    const f = FLOWERS[(i * 2) % 9];
    const gone = C.mais + i * .08;
    const k = s < gone ? 1 : 1 - spring(s - gone, .5, 16);
    if (k <= .01 && s > gone + .5) continue;
    const bx = f.x + 80 * Math.sin(a * (.9 + i * .13) + i), by = 140 - f.h - 60 + 40 * Math.sin(a * (1.3 + i * .1) + i * 2);
    if (k > .02) drawBee(bx, by, 1.1 * Math.max(0, k), a, i);
    if (s > gone && s < gone + .4) { ctx.fillStyle = `rgba(255,255,255,${.7 * (1 - (s - gone) / .4)})`; ctx.beginPath(); ctx.arc(bx, by, 10 + 60 * (s - gone), 0, 6.283); ctx.fill(); }
  }
  // mesa com 4 culturas e contador de 75%
  if (s < T.t1 + TD) {
    const kt = spring(s - (C.comida - .2), .5, 12);
    if (kt > 0) {
      ctx.save(); ctx.translate(0, lerp(900, 0, kt));
      ctx.fillStyle = '#a86e48'; ctx.beginPath(); ctx.roundRect(-700, 330, 1400, 60, 20); ctx.fill();
      ctx.fillStyle = '#8a5a3c'; ctx.beginPath(); ctx.roundRect(-640, 390, 40, 300, 12); ctx.roundRect(600, 390, 40, 300, 12); ctx.fill();
      const items = [['#e6735f', 'maca'], ['#ff5f6d', 'morango'], ['#5fc47a', 'abacate'], ['#ffd98a', 'trigo']];
      items.forEach(([col, kind], i) => {
        const dim = i < 3 ? easeIO((s - (C.tres + .15 + i * .12)) / .4) : 0;
        const x = -480 + i * 320, y = 260;
        ctx.save(); ctx.globalAlpha = 1 - dim * .65; ctx.translate(x, y); ctx.scale(1 - dim * .15, 1 - dim * .15);
        ctx.fillStyle = dim > .5 ? '#9aa3ad' : col;
        if (kind === 'morango') { ctx.beginPath(); ctx.moveTo(0, 70); ctx.bezierCurveTo(-70, 10, -60, -60, 0, -50); ctx.bezierCurveTo(60, -60, 70, 10, 0, 70); ctx.fill(); ctx.fillStyle = '#3a9d62'; ctx.beginPath(); ctx.ellipse(0, -52, 34, 12, 0, 0, 6.283); ctx.fill(); }
        else if (kind === 'abacate') { ctx.beginPath(); ctx.ellipse(0, 0, 52, 70, 0, 0, 6.283); ctx.fill(); ctx.fillStyle = dim > .5 ? '#c9d6e3' : '#f5e6a8'; ctx.beginPath(); ctx.ellipse(0, 6, 36, 52, 0, 0, 6.283); ctx.fill(); ctx.fillStyle = '#8a5a3c'; ctx.beginPath(); ctx.arc(0, 16, 20, 0, 6.283); ctx.fill(); }
        else if (kind === 'trigo') { ctx.fillStyle = dim > .5 ? '#9aa3ad' : '#c98a5e'; ctx.fillRect(-4, -70, 8, 140); ctx.fillStyle = col; for (let k = 0; k < 6; k++) { ctx.beginPath(); ctx.ellipse(-12, -60 + k * 16, 12, 7, -.6, 0, 6.283); ctx.ellipse(12, -60 + k * 16, 12, 7, .6, 0, 6.283); ctx.fill(); } }
        else { ctx.beginPath(); ctx.arc(0, 6, 62, 0, 6.283); ctx.fill(); ctx.fillStyle = '#3a9d62'; ctx.beginPath(); ctx.ellipse(16, -60, 22, 10, -.5, 0, 6.283); ctx.fill(); }
        ctx.restore();
      });
      ctx.restore();
    }
    screenSpace();
    const sq = storyT(Math.round(CUR_T * FPS) / FPS);
    if (s > C.tres - .1) {
      const k = spring(s - C.tres, .45, 14), v = Math.round(75 * easeIO((sq - C.tres) / (C.quatro - C.tres + .6)));
      ctx.save(); ctx.translate(W / 2, 170); const sc = lerp(1.7, 1, k); ctx.scale(sc, sc); ctx.globalAlpha = clamp(k * 2);
      ctx.fillStyle = 'rgba(6,20,40,.62)'; ctx.beginPath(); ctx.roundRect(-170, -80, 340, 160, 48); ctx.fill();
      ctx.font = FONT(700, 100); ctx.letterSpacing = '4px'; ctx.textAlign = 'center'; ctx.fillStyle = COL.gold; ctx.fillText(v + '%', 0, 36);
      ctx.restore();
      pill([{ s: 'DAS CULTURAS DE FRUTOS E SEMENTES', px: 30, c: COL.white, ls: 4 }, { s: 'DEPENDEM DE POLINIZADORES', px: 30, c: COL.teal, ls: 4 }, { s: 'FONTE: FAO', px: 20, c: COL.white, ls: 4, w: 600 }], W / 2, 350, s, C.quatro, T.t1 - .1);
    }
    pill([{ s: 'UM MUNDO SEM ABELHAS', px: 40, c: COL.white, ls: 7 }], W / 2, 110, s, C.mais + .1, C.comida - .3);
  } else {
    applyCam();
    const fx = FLOWERS[REVIVE].x, fy = 140 - FLOWERS[REVIVE].h;
    const kin = spring(s - (C.robos - .25), .45, 12);
    if (kin > 0) drawRoboBee(lerp(fx + 500, fx + 10, easeOutCubic((s - C.robos + .25) / .8)), fy - 80, 1.4 * kin, s, a, { kicks: [C.robos, C.robos + .5], look: { x: fx, y: fy } });
    screenSpace();
    if (CUR_T < RW0) pill([{ s: 'ABELHAS-ROBÔS', px: 52, c: COL.gold, ls: 8 }], W / 2, 130, s, C.robos, T.t3 - .2);
  }
}

// ---------------------------------------------------------------------
//  CENA 2: O GLOBO (escala)
// ---------------------------------------------------------------------
function globeCam(s, a) {
  let c = keyed([[T.t1, 0, -60, 4.5], [T.t1 + 1.2, 0, -20, 1.45], [T.t2, 0, -10, 1.6]], s);
  c = mixCam(c, { x: 0, y: -120, z: 9 }, easeInCubic((s - (T.t2 - .45)) / (.45 + TD)));
  return breathe(c, a);
}
function drawGlobe(s, t, a) {
  CAM = globeCam(s, a);
  screenSpace(); drawBackground(a, 0);
  drawEarth(earthRot(s, a), a);
  pill([{ s: 'UMA PREOCUPAÇÃO REAL', px: 44, c: COL.white, ls: 7 }], W / 2, H - 140, s, C.real - .1, T.t2 - .1);
}

// ---------------------------------------------------------------------
//  CENA 3: O LABORATÓRIO
// ---------------------------------------------------------------------
function labCam(s, a) {
  let c;
  if (s < T.t4 + TD) {
    c = keyed([[T.t3, 0, -200, .5], [T.t3 + .8, 0, -180, .9], [C.clipe - .2, -80, -170, 1.25], [C.dezessete, 40, -180, 1.1], [T.t4 - .4, 0, -180, 1.2]], s);
    c = mixCam(c, { x: 0, y: -180, z: 7 }, easeInCubic((s - (T.t4 - .4)) / (.4 + TD)));
  } else {
    c = keyed([[T.t5, 0, -180, .55], [T.t5 + .9, 0, -200, 1.0], [C.mit2, 0, -190, 1.3], [T.t6 - .4, 0, -190, 1.35]], s);
    c = mixCam(c, { x: 0, y: -190, z: 6 }, easeInCubic((s - (T.t6 - .4)) / (.4 + TD)));
  }
  c = breathe(c, a);
  return shake(c, 10 * kick(s - C.mit2, .4, 20), a);
}
function drawLab(s, t, a) {
  CAM = labCam(s, a);
  screenSpace(); drawBackground(a, 0);
  applyCam();
  const second = s > T.t5;
  // bancada e luz de estúdio
  const g = ctx.createRadialGradient(0, -200, 40, 0, -200, 900);
  g.addColorStop(0, second ? 'rgba(255,95,109,.28)' : 'rgba(143,216,230,.26)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, -200, 900, 0, 6.283); ctx.fill();
  ctx.fillStyle = '#1b2f4f'; ctx.beginPath(); ctx.roundRect(-900, 40, 1800, 80, 24); ctx.fill();
  ctx.fillStyle = '#12233b'; ctx.fillRect(-860, 120, 1720, 900);
  ctx.fillStyle = 'rgba(4,10,24,.45)'; ctx.beginPath(); ctx.ellipse(0, 48, 120, 12, 0, 0, 6.283); ctx.fill();
  drawMitBot(0, -180, 1.6, a);
  // clipe de papel para comparar
  if (!second) {
    const kc = spring(s - (C.clipe - .1), .45, 14);
    if (kc > 0) {
      ctx.save(); ctx.translate(-330, 0); ctx.scale(kc, kc);
      ctx.strokeStyle = '#d7e2ec'; ctx.lineWidth = 9; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(-60, -10); ctx.lineTo(60, -10); ctx.arc(60, 8, 18, -Math.PI / 2, Math.PI / 2); ctx.lineTo(-50, 26); ctx.arc(-50, 12, 14, Math.PI / 2, Math.PI * 1.5); ctx.lineTo(48, -2); ctx.arc(48, 8, 10, -Math.PI / 2, Math.PI / 2); ctx.lineTo(-30, 18); ctx.stroke();
      ctx.restore();
    }
  } else {
    // cadeado se abre sobre o robô
    const kl = spring(s - C.mit2, .45, 14), open = easeOutCubic((s - C.mit2 - .3) / .5);
    if (kl > 0) {
      ctx.save(); ctx.translate(190, -330); ctx.scale(kl, kl);
      ctx.fillStyle = '#ff8a7a'; ctx.beginPath(); ctx.roundRect(-46, -20, 92, 74, 16); ctx.fill();
      ctx.fillStyle = '#c9d6e3'; ctx.save(); ctx.translate(30, -20); ctx.rotate(-open * .9); ctx.translate(-30, 0);
      ctx.beginPath(); ctx.roundRect(-34, -60, 14, 60, 7); ctx.roundRect(20, -60, 14, 60, 7); ctx.roundRect(-34, -66, 68, 14, 7); ctx.fill(); ctx.restore();
      ctx.fillStyle = '#0b1e33'; ctx.beginPath(); ctx.arc(0, 10, 9, 0, 6.283); ctx.fill();
      ctx.restore();
    }
  }
  screenSpace();
  if (!second) {
    pill([{ s: 'MIT · 2025', px: 40, c: COL.white, ls: 7 }, { s: 'ROBÔ-INSETO QUE IMITA O VOO DAS ABELHAS', px: 28, c: COL.teal, ls: 4, w: 600 }], W / 2, 120, s, C.mit1 - .05, C.clipe - .3);
    pill([{ s: 'MENOS QUE UM CLIPE', px: 34, c: COL.gold, ls: 5 }], 520, 760, s, C.clipe, T.t4 - .2, { pad: 18 });
    if (s > C.dezessete - .1) {
      const sq = storyT(Math.round(CUR_T * FPS) / FPS);
      const sec = 1020 * easeIO((sq - C.dezessete) / 1.6);
      const k = spring(s - C.dezessete, .45, 14), sc = lerp(1.7, 1, k);
      ctx.save(); ctx.translate(1420, 230); ctx.scale(sc, sc); ctx.globalAlpha = clamp(k * 2) * (1 - easeIO((s - (T.t4 - .3)) / .3));
      ctx.fillStyle = 'rgba(6,20,40,.62)'; ctx.beginPath(); ctx.roundRect(-210, -76, 420, 152, 46); ctx.fill();
      ctx.font = FONT(700, 96); ctx.letterSpacing = '4px'; ctx.textAlign = 'center'; ctx.fillStyle = sec >= 1019 ? COL.gold : COL.white;
      ctx.fillText(`${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(Math.floor(sec % 60)).padStart(2, '0')}`, 0, 34);
      ctx.restore();
      riseText('DE VOO', 1420, 360, 30, COL.teal, s, C.dezessete + .1, T.t4 - .3, { ls: 5, w: 600 });
      pill([{ s: 'AINDA PRESO A UM CABO DE ENERGIA', px: 24, c: COL.teal, ls: 4 }], 1420, 440, s, C.dezessete + .5, T.t4 - .3, { pad: 14 });
    }
  } else {
    pill([{ s: 'E SE ALGUÉM HACKEASSE?', px: 44, c: COL.coral, ls: 6 }], W / 2, 130, s, C.mit2 - .1, T.t6 - .2);
  }
}

// ---------------------------------------------------------------------
//  CENA 4: A FAZENDA VERTICAL (e o lado sombrio)
// ---------------------------------------------------------------------
const FARM_BEES = (() => { const r = rng(77), a = []; for (let i = 0; i < 14; i++) a.push({ x: -800 + r() * 1600, y: -560 + Math.floor(r() * 3) * 280, ph: r() * 6, sp: .6 + r() * .6 }); return a; })();
function farmCam(s, a) {
  let c = keyed([[T.t4, 0, -300, .5], [T.t4 + .9, 0, -320, .82], [C.sombrio, 0, -320, .9], [C.black1, 0, -300, .8], [C.hackeia, 0, -320, .9], [C.armas, 0, -300, 1.35], [T.t5, 0, -300, 1.5]], s);
  c = breathe(c, a);
  return shake(c, 10 * kick(s - C.sombrio, .4, 18) + 26 * kick(s - C.armas, .35, 22) + 14 * kick(s - C.hackeia, .4, 20), a);
}
function drawFarm(s, t, a) {
  CAM = farmCam(s, a);
  screenSpace(); ctx.fillStyle = '#0b1e33'; ctx.fillRect(0, 0, W, H);
  applyCam();
  const dark = smooth(C.sombrio - .1, C.sombrio + .6, s), hack = smooth(C.hackeia - .1, C.hackeia + .5, s);
  const flick = dark > 0 && dark < 1 ? (Math.sin(a * 47) > 0 ? 1 : .4) : 1;
  ctx.fillStyle = '#152b46'; ctx.fillRect(-3000, -2000, 6000, 4000);
  // prateleiras com luz de LED e morangueiros
  for (let lv = 0; lv < 3; lv++) {
    const y = -460 + lv * 280;
    const led = `rgba(${hack > .5 ? '255,95,109' : '255,120,220'},${(.75 - dark * .55) * flick})`;
    ctx.fillStyle = '#2a3f63'; ctx.beginPath(); ctx.roundRect(-1000, y - 150, 2000, 16, 8); ctx.fill();
    ctx.fillStyle = led; ctx.beginPath(); ctx.roundRect(-980, y - 134, 1960, 8, 4); ctx.fill();
    const g = ctx.createLinearGradient(0, y - 130, 0, y + 10); g.addColorStop(0, led); g.addColorStop(1, 'rgba(255,120,220,0)');
    ctx.fillStyle = g; ctx.globalAlpha = .25; ctx.fillRect(-980, y - 130, 1960, 140); ctx.globalAlpha = 1;
    ctx.fillStyle = '#34507a'; ctx.beginPath(); ctx.roundRect(-1000, y, 2000, 26, 8); ctx.fill();
    for (let x = -940; x < 960; x += 120) {
      ctx.fillStyle = '#3a9d62'; ctx.beginPath(); ctx.ellipse(x, y - 24, 46, 22, 0, 0, 6.283); ctx.fill();
      ctx.fillStyle = '#f3f7fb'; ctx.beginPath(); ctx.arc(x - 16, y - 46, 9, 0, 6.283); ctx.fill();
      ctx.fillStyle = '#ff5f6d'; ctx.beginPath(); ctx.ellipse(x + 18, y - 8, 11, 14, 0, 0, 6.283); ctx.fill();
    }
  }
  // abelhas-robôs: polinizam, depois viram enxame
  for (const b of FARM_BEES) {
    let x = b.x + 60 * Math.sin(a * b.sp + b.ph), y = b.y - 70 + 30 * Math.sin(a * 1.4 * b.sp + b.ph);
    const sw = easeIO((s - C.hackeia - .2) / 1.2);
    const ang = b.ph + a * 2.2, rr = 130 + 40 * Math.sin(b.ph * 3);
    x = lerp(x, Math.cos(ang) * rr, sw); y = lerp(y, -300 + Math.sin(ang) * rr * .6, sw);
    drawRoboBee(x, y, .85 + sw * .25, s, a + b.ph, { hacked: hack, look: { x: 0, y: -300 } });
  }
  // vinheta vermelha nas armas
  screenSpace();
  if (s > C.armas - .1) {
    const k = easeIO((s - C.armas + .1) / .4);
    const vg = ctx.createRadialGradient(W / 2, H / 2, H * .3, W / 2, H / 2, H);
    vg.addColorStop(0, 'rgba(255,95,109,0)'); vg.addColorStop(1, `rgba(255,95,109,${.35 * k})`);
    ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  }
  // glitch: faixas deslocadas no sombrio e no hackeia
  const gk = Math.exp(-Math.max(0, s - C.sombrio) * 4) * (s > C.sombrio) + Math.exp(-Math.max(0, s - C.hackeia) * 3) * (s > C.hackeia);
  if (gk > .02) {
    const r = rng(Math.floor(CUR_T * 30) + 3);
    for (let i = 0; i < 8; i++) { const y = r() * H, h = 6 + r() * 40, dx = (r() - .5) * 120 * gk; ctx.drawImage(ctx.canvas, 0, y, W, h, dx, y, W, h); }
  }
  pill([{ s: 'FAZENDAS INDOOR', px: 40, c: COL.white, ls: 7 }], W / 2, 120, s, C.fazendas - .05, C.sombrio - .2);
  pill([{ s: 'BLACK MIRROR', px: 46, c: COL.white, ls: 9 }, { s: 'HATED IN THE NATION · 2016', px: 28, c: COL.teal, ls: 5, w: 600 }], W / 2, 130, s, C.black1 - .05, C.hackeia - .2);
  pill([{ s: 'ALGUÉM HACKEIA O SISTEMA', px: 40, c: COL.coral, ls: 6 }], W / 2, H - 130, s, C.hackeia, T.t5 - .2);
}

// ---------------------------------------------------------------------
//  CENA 5: O ESTÚDIO (culpa, lista, balança, pergunta)
// ---------------------------------------------------------------------
function studioCam(s, a) {
  let c = keyed([[T.t6, 0, -100, .55], [T.t6 + .8, 0, -60, .85], [C.nos, 120, -40, .92], [C.abelha - .2, 0, -60, .85],
                 [C.abelha + .3, 2400, -60, .9], [C.cresce + .2, 2400, -60, .7], [C.tecnologia1 - .2, 4800, -60, .9], [C.riscos2, 4800, -60, .95],
                 [C.ponto - .1, 4800, -300, 1.6], [C.questionar + .3, 4800, -320, 2.0]], s);
  c = breathe(c, a);
  return shake(c, 10 * kick(s - C.nos, .4, 20) + 8 * kick(s - C.carro, .4, 20), a);
}
function card(x, y, label, icon, s, t0, col) {
  const k = spring(s - t0, .45, 14); if (k <= 0) return;
  const drop = (1 - clamp((s - t0) / .3)) * -300;
  ctx.save(); ctx.translate(x, y + drop); ctx.rotate(.04 * Math.sin(x)); ctx.scale(k, k);
  ctx.fillStyle = 'rgba(6,20,40,.62)'; ctx.beginPath(); ctx.roundRect(-190, -230, 380, 460, 40); ctx.fill();
  ctx.save(); ctx.translate(0, -50); icon(); ctx.restore();
  ctx.restore();
  ctx.save(); ctx.translate(x, y + drop); ctx.scale(k, k);
  riseText(label, 0, 170, 40, col, s, t0 + .1, 1e9, { ls: 5 });
  ctx.restore();
}
const IC = {
  fabrica() { ctx.fillStyle = '#8a9bb5'; ctx.beginPath(); ctx.roundRect(-110, -20, 220, 110, 10); ctx.fill(); ctx.beginPath(); ctx.moveTo(-110, -20); ctx.lineTo(-50, -70); ctx.lineTo(-50, -20); ctx.lineTo(10, -70); ctx.lineTo(10, -20); ctx.closePath(); ctx.fill(); ctx.fillStyle = '#c9d6e3'; ctx.beginPath(); ctx.roundRect(50, -120, 34, 100, 6); ctx.fill(); ctx.fillStyle = '#ffd98a'; for (let k = 0; k < 3; k++) { ctx.beginPath(); ctx.roundRect(-90 + k * 70, 20, 40, 30, 6); ctx.fill(); } },
  hacker() { ctx.fillStyle = '#2a3f63'; ctx.beginPath(); ctx.arc(0, -40, 60, Math.PI, 0); ctx.lineTo(70, 80); ctx.lineTo(-70, 80); ctx.closePath(); ctx.fill(); ctx.fillStyle = '#0a1c2c'; ctx.beginPath(); ctx.ellipse(0, -30, 36, 40, 0, 0, 6.283); ctx.fill(); ctx.fillStyle = '#8fecff'; ctx.beginPath(); ctx.roundRect(-80, 50, 160, 70, 10); ctx.fill(); },
  nos() { const cs = ['#ff8a7a', '#8fd8e6', '#ffd98a']; [-70, 0, 70].forEach((x, i) => { ctx.fillStyle = cs[i]; ctx.beginPath(); ctx.roundRect(x - 34, 10, 68, 90, 30); ctx.fill(); ctx.fillStyle = SKIN; ctx.beginPath(); ctx.arc(x, -30, 32, 0, 6.283); ctx.fill(); }); }
};
function warnIcon(x, y, sc, kind) {
  ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc);
  ctx.fillStyle = 'rgba(6,20,40,.62)'; ctx.beginPath(); ctx.roundRect(-150, -130, 300, 260, 40); ctx.fill();
  if (kind === 'carro') {
    ctx.fillStyle = '#8fd8e6'; ctx.beginPath(); ctx.roundRect(-110, -10, 220, 60, 22); ctx.fill(); ctx.beginPath(); ctx.roundRect(-64, -60, 128, 60, [30, 30, 4, 4]); ctx.fill();
    ctx.fillStyle = '#1b2433'; ctx.beginPath(); ctx.arc(-62, 54, 22, 0, 6.283); ctx.arc(62, 54, 22, 0, 6.283); ctx.fill();
    ctx.fillStyle = '#0a1c2c'; ctx.beginPath(); ctx.roundRect(-40, -50, 80, 34, 12); ctx.fill();
  } else if (kind === 'drone') {
    ctx.fillStyle = '#8a9bb5'; ctx.beginPath(); ctx.roundRect(-40, -20, 80, 40, 14); ctx.fill();
    for (const d of [-1, 1]) { ctx.beginPath(); ctx.roundRect(d * 40 - (d > 0 ? 0 : 60), -6, 60, 12, 6); ctx.fill(); ctx.fillStyle = 'rgba(200,240,255,.6)'; ctx.beginPath(); ctx.ellipse(d * 100, -14, 46, 8, 0, 0, 6.283); ctx.fill(); ctx.fillStyle = '#8a9bb5'; }
  } else {
    ctx.fillStyle = '#ff8a7a'; ctx.beginPath(); ctx.moveTo(0, -80); ctx.lineTo(80, 60); ctx.lineTo(-80, 60); ctx.closePath(); ctx.fill();
    ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.roundRect(-7, -36, 14, 56, 7); ctx.fill(); ctx.beginPath(); ctx.arc(0, 40, 9, 0, 6.283); ctx.fill();
  }
  ctx.restore();
}
function drawStudio(s, t, a) {
  CAM = studioCam(s, a);
  screenSpace(); drawBackground(a, 0);
  applyCam();
  // culpa: três cartas e o pino VOCÊ
  card(-480, 0, 'FABRICANTE', IC.fabrica, s, C.fabricante, COL.white);
  card(0, 0, 'HACKER', IC.hacker, s, C.hacker, COL.coral);
  card(480, 0, 'NÓS', IC.nos, s, C.nos, COL.gold);
  drawPin(480, -270, 1.1, 'VOCÊ', s, C.nos + .1);
  // a abelhinha procura o culpado e aponta para si mesma
  const point = spring(s - (C.culpado + .2), .5, 12) * (1 - easeIO((s - C.fabricante) / .3));
  drawRoboBee(-60, -330 + 20 * Math.sin(a), 1.2, s, a, { look: s < C.fabricante ? { x: -200 + 400 * Math.sin(a * 3), y: -430 } : { x: 600, y: -100 }, point, kicks: [C.culpado + .2, C.fabricante, C.hacker, C.nos], tilt: point * .15 });
  if (point > .3) { ctx.save(); ctx.translate(40, -460); ctx.scale(point, point); ctx.fillStyle = COL.gold; ctx.font = FONT(700, 70); ctx.textAlign = 'center'; ctx.fillText('?', 0, 0); ctx.restore(); }
  // lista que só cresce
  const L0 = 2400;
  if (s > C.abelha - .3) {
    const items = [['carro', C.carro], ['drone', C.drone]];
    items.forEach(([k, t0], i) => { const kk = spring(s - t0, .45, 14); if (kk > 0) warnIcon(L0 - 200 + i * 400, -80, kk, k); });
    const n = Math.floor(clamp((s - C.lista) / 1.6) * 40);
    for (let i = 0; i < n; i++) { const col = i % 10, row = Math.floor(i / 10); const kk = spring(s - (C.lista + i * .04), .45, 15); if (kk > 0) warnIcon(L0 - 650 + col * 145, 230 + row * 130, .42 * kk, 'aviso'); }
  }
  // balança: tecnologia x riscos
  const B0 = 4800;
  const kb = spring(s - (C.tecnologia1 - .1), .45, 13);
  if (kb > 0) {
    const tilt = .16 * Math.sin(a * 1.6) * (1 - smooth(C.quanto, C.riscos2, s)) - .22 * smooth(C.quanto, C.riscos2 + .3, s);
    ctx.save(); ctx.translate(B0, 120); ctx.scale(kb, kb);
    ctx.fillStyle = '#8a9bb5'; ctx.beginPath(); ctx.roundRect(-16, -320, 32, 330, 12); ctx.fill(); ctx.beginPath(); ctx.roundRect(-140, 0, 280, 30, 15); ctx.fill();
    ctx.save(); ctx.translate(0, -320); ctx.rotate(tilt);
    ctx.fillStyle = '#c9d6e3'; ctx.beginPath(); ctx.roundRect(-460, -12, 920, 24, 12); ctx.fill();
    for (const d of [-1, 1]) {
      ctx.save(); ctx.translate(d * 430, 0); ctx.rotate(-tilt);
      ctx.fillStyle = '#c9d6e3'; ctx.fillRect(-3, 0, 6, 160);
      ctx.fillStyle = d < 0 ? '#8fd8e6' : '#ff8a7a'; ctx.beginPath(); ctx.ellipse(0, 170, 170, 34, 0, 0, Math.PI); ctx.fill();
      if (d < 0) drawRoboBee(0, 110, .7, s, a, {}); else warnIcon(0, 100, .4, 'aviso');
      ctx.restore();
    }
    ctx.restore(); ctx.restore();
    applyCam();
    const pL = ws(B0 - 430, 120 - 100), pR = ws(B0 + 430, 120 - 100);
    screenSpace();
    pill([{ s: 'TECNOLOGIA', px: 34, c: COL.teal, ls: 6 }], pL.x, pL.y + 260 * CAM.z, s, C.tecnologia1, C.ponto - .2, { pad: 16 });
    pill([{ s: 'RISCOS', px: 34, c: COL.coral, ls: 6 }], pR.x, pR.y + 260 * CAM.z, s, C.quanto, C.ponto - .2, { pad: 16 });
    applyCam();
  }
  // close final na abelhinha: ela olha para quem assiste
  if (s > C.ponto - .4) {
    const k = spring(s - (C.ponto - .3), .45, 12);
    drawRoboBee(B0, -320, 1.6 * k, s, a, { look: { x: B0, y: 100 }, kicks: [C.questionar] });
  }
  screenSpace();
  pill([{ s: 'QUEM SERIA O CULPADO', px: 40, c: COL.white, ls: 6 }], W / 2, 110, s, C.culpado - .1, C.abelha - .3);
  pill([{ s: 'E A LISTA SÓ CRESCE', px: 40, c: COL.gold, ls: 6 }], W / 2, 110, s, C.cresce - .2, C.tecnologia1 - .3);
}

// =====================================================================
//  COMPOSIÇÃO
// =====================================================================
const SCENES = { garden: drawGarden, globe: drawGlobe, lab: drawLab, farm: drawFarm, studio: drawStudio };
const TRANS = [
  { s: T.t1, from: 'garden', to: 'globe', mode: 'close' },
  { s: T.t2, from: 'globe', to: 'garden', mode: 'open' },
  { s: T.t3, from: 'garden', to: 'lab', mode: 'open' },
  { s: T.t4, from: 'lab', to: 'farm', mode: 'open' },
  { s: T.t5, from: 'farm', to: 'lab', mode: 'close' },
  { s: T.t6, from: 'lab', to: 'studio', mode: 'open' }
];
function sceneAt(s) { let n = 'garden'; for (const tr of TRANS) if (s >= tr.s + TD) n = tr.to; return n; }
function renderLayer(name, s, t, a, layer) {
  const c = layer.getContext('2d'); ctx = c; c.setTransform(1, 0, 0, 1, 0, 0);
  SCENES[name](s, t, a); c.setTransform(1, 0, 0, 1, 0, 0); ctx = mctx;
  return layer;
}
function focusOf(tr, s, a, t) { return { x: W / 2, y: H / 2 - 60 }; }
let CUR_T = 0;
function draw(t) {
  CUR_T = t;
  const a = t, s = storyT(t);
  ctx = mctx; mctx.setTransform(1, 0, 0, 1, 0, 0);
  const tr = TRANS.find(q => s >= q.s && s < q.s + TD);
  if (!tr) {
    renderLayer(sceneAt(s), s, t, a, LA); mctx.drawImage(LA, 0, 0);
  } else {
    const u = (s - tr.s) / TD, maxR = Math.hypot(W, H);
    const f = focusOf(tr, s, a, t);
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
  pill([{ s: 'SALVA OU CONDENA', px: 112, c: COL.white, ls: 9 }, { s: 'ABELHAS-ROBÔS', px: 44, c: COL.gold, ls: 8 }], W / 2, 210, t, t0);
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
