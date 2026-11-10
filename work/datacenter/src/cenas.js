// =====================================================================
//  UMA CIDADE DISSE SIM: Harwood (Dakota do Norte), eleições de 2026
// =====================================================================
const HARWOOD = [-96.98, 46.98], US_CENTER = [-98, 40];
const T = {   // transições (tempo da história)
  t1: C.menos2 - .45,           // globo -> cidade
  t2: C.agora - .1,             // cidade -> varanda do Mark
  t3: C.e_imposto - .1,         // varanda -> cidade (imposto, Fargo)
  t4: C.mas - .1                // cidade -> varanda (não virou fã)
};
const TD = .5;
const earthRot = (s, a) => (-100 - a * .55) * D2R;
const SUBSOLAR = [150, -16];   // noite de eleição nos EUA
function hwW(s, a) { return geoWorld(HARWOOD[0], HARWOOD[1], earthRot(s, a)); }
function usW(s, a) { return geoWorld(US_CENTER[0], US_CENTER[1], earthRot(s, a)); }

// ---------------------------------------------------------------------
//  CENA 1: GLOBO À NOITE, AS VOTAÇÕES
// ---------------------------------------------------------------------
const N_VOTES = 41, GREEN_I = 23;
function voteSlot(i) { const c = i % 9, r = Math.floor(i / 9); return { x: (c - 4) * 92 + (r % 2 ? 46 : 0), y: (r - 2) * 92 }; }
function globeCam(s, a) {
  const us = usW(s, a), hw = hwW(s, a);
  const P = (p, z, dx = 0, dy = 0) => ({ x: p.x + dx / z, y: p.y + dy / z, z });
  let c = mixCam(P(us, 4.4), P(us, 3.6), easeIO(s / C.votam));
  c = mixCam(c, P(us, 2.5, 0, -40), easeIO((s - (C.nao1 - .5)) / 1.4));
  c = mixCam(c, P(hw, 3.4, 0, 60), easeIO((s - (C.uma - .1)) / 1.4));
  c = mixCam(c, P(hw, 70), easeInCubic((s - (T.t1 - .55)) / (.55 + TD)));
  // depois do rewind: afasta para o título
  if (CUR_T > RW1) c = mixCam(c, P(us, 2.2, 0, -60), easeIO((CUR_T - RW1) / 1.6));
  c = breathe(c, a);
  return shake(c, 14 * kick(s - C.nao1, .4, 20) + 10 * kick(s - C.uma, .4, 20), a);
}
function ballot(x, y, sc, state, k, s) {
  // state: 0 urna, 1 NÃO (coral), 2 SIM (verde)
  ctx.save(); ctx.translate(x, y); ctx.scale(sc * k, sc * k);
  const col = state === 2 ? '#5fc47a' : state === 1 ? '#ff8a7a' : '#f3f7fb';
  ctx.fillStyle = 'rgba(6,20,40,.5)'; ctx.beginPath(); ctx.roundRect(-38, -30, 76, 66, 16); ctx.fill();
  ctx.fillStyle = col; ctx.beginPath(); ctx.roundRect(-34, -24, 68, 56, 14); ctx.fill();
  if (state === 0) {
    ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.roundRect(-14, -44, 28, 34, 5); ctx.fill();
    ctx.fillStyle = '#0b1e33'; ctx.beginPath(); ctx.roundRect(-22, -26, 44, 6, 3); ctx.fill();
  } else {
    ctx.fillStyle = state === 2 ? '#0b1e33' : '#ffffff'; ctx.font = FONT(700, 24); ctx.letterSpacing = '2px'; ctx.textAlign = 'center';
    ctx.fillText(state === 2 ? 'SIM' : 'NÃO', 2, 13);
  }
  ctx.restore();
}
function drawGlobe(s, t, a) {
  CAM = globeCam(s, a);
  screenSpace(); drawBackground(a, 0);
  const rot = earthRot(s, a);
  drawEarth(rot, a);
  applyCam();
  const hw = hwW(s, a), hp = ws(hw.x, hw.y);
  // brilho de Harwood
  screenSpace();
  const hk = spring(s - C.uma, .45, 14);
  if (hk > 0) {
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const R = 26 + 10 * Math.sin(a * 4);
    const g = ctx.createRadialGradient(hp.x, hp.y, 0, hp.x, hp.y, R * 2 * hk);
    g.addColorStop(0, 'rgba(160,255,190,1)'); g.addColorStop(1, 'rgba(95,196,122,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(hp.x, hp.y, R * 2 * hk, 0, 6.283); ctx.fill(); ctx.restore();
  }
  // as votações: grade de urnas sobre os EUA, em espaço de tela
  const out = CUR_T > RW0 ? 0 : easeIO((s - (C.uma + .15)) / .5);
  const cx = W / 2, cy = H / 2 - 40;
  for (let i = 0; i < N_VOTES; i++) {
    const t0 = C.votam - .1 + i * .018;
    const k = spring(s - t0, .45, 14); if (k <= 0) continue;
    const sl = voteSlot(i);
    let x = cx + sl.x, y = cy + sl.y;
    const flip = C.nao1 - .15 + (i % 9) * .03 + Math.floor(i / 9) * .02;
    let state = s > flip ? 1 : 0;
    if (i === GREEN_I && s > C.uma) state = 2;
    let sc = 1 + .25 * kick(s - flip, .45, 16);
    let alpha = 1;
    if (i === GREEN_I) {
      sc *= 1 + .5 * spring(s - C.uma, .45, 13);
      const m = CUR_T > RW0 ? 0 : easeIO((s - (C.uma + .3)) / 1.0);
      x = lerp(x, hp.x, m); y = lerp(y, hp.y - 50, m); sc *= lerp(1, .8, m);
    } else alpha = 1 - out;
    if (alpha <= 0) continue;
    ctx.save(); ctx.globalAlpha = alpha; ballot(x, y, sc, state, k, s); ctx.restore();
  }
  pill([{ s: 'ELEIÇÕES DE 2026 · EUA', px: 34, c: COL.teal, ls: 6 }], W / 2, 130, s, C.votam - .2, C.nao1 - .2, { pad: 18 });
  if (CUR_T < RW0) pill([{ s: 'MAIS DE 40 VOTAÇÕES SOBRE', px: 32, c: COL.white, ls: 5 }, { s: 'DATA CENTERS DE IA', px: 32, c: COL.gold, ls: 5 }], W / 2, H - 150, s, C.votacoes - .1, C.uma - .1);
  if (CUR_T < RW0) pill([{ s: 'HARWOOD · DAKOTA DO NORTE', px: 34, c: COL.white, ls: 5 }], hp.x, hp.y - 150, s, C.harwood, T.t1 - .1, { pad: 18 });
}

// ---------------------------------------------------------------------
//  CENA 2: A CIDADE NA PRADARIA
// ---------------------------------------------------------------------
const HZ = 0;                          // horizonte
const HOUSES = [[-900, 1.0, '#ff8a7a'], [-700, .85, '#8fd8e6'], [-520, 1.1, '#ffd98a'], [-300, .9, '#f3f7fb'], [-120, 1.0, '#ff8a7a'], [60, .8, '#8fd8e6']];
const MARK_HOUSE = 3;
const DC = { x0: 380, x1: 1700, h: 170 };   // data center (mundo)
function townCam(s, t, a) {
  const hx = HOUSES[MARK_HOUSE][0];
  let c;
  if (s < T.t2 + TD) {
    c = keyed([[T.t1, -320, -120, 1.5], [T.t1 + .9, -380, -150, 1.05], [C.tres - .2, -300, -170, .95], [C.bilhoes - .3, 500, -200, .62], [C.bilhoes + .5, 560, -200, .58], [T.t2 - .5, hx + 40, -100, .9]], s);
    c = mixCam(c, { x: hx, y: -60, z: 6 }, easeInCubic((s - (T.t2 - .45)) / (.45 + TD)));
  } else {
    c = keyed([[T.t3, hx, -80, 1.6], [T.t3 + .8, -100, -200, .8], [C.seis - .2, -220, 40, .95], [C.muitos - .1, 900, -260, .3], [C.fargo + .2, 2000, -220, .2], [T.t4 - .5, hx + 300, -150, .35]], s);
    c = mixCam(c, { x: hx, y: -60, z: 6 }, easeInCubic((s - (T.t4 - .45)) / (.45 + TD)));
  }
  c = breathe(c, a);
  return shake(c, 12 * kick(s - C.bilhoes, .4, 20) + 8 * kick(s - C.seis, .4, 20), a);
}
function house(x, sc, col, a) {
  ctx.save(); ctx.translate(x, HZ + 40); ctx.scale(sc, sc);
  ctx.fillStyle = 'rgba(80,50,30,.25)'; ctx.beginPath(); ctx.ellipse(0, 4, 110, 12, 0, 0, 6.283); ctx.fill();
  ctx.fillStyle = col; ctx.beginPath(); ctx.roundRect(-80, -110, 160, 112, 10); ctx.fill();
  ctx.fillStyle = '#5b3a2e'; ctx.beginPath(); ctx.moveTo(-100, -100); ctx.lineTo(0, -180); ctx.lineTo(100, -100); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#ffd98a'; ctx.beginPath(); ctx.roundRect(-55, -80, 34, 30, 6); ctx.roundRect(22, -80, 34, 30, 6); ctx.fill();
  ctx.fillStyle = '#3a2a2e'; ctx.beginPath(); ctx.roundRect(-14, -54, 28, 54, 6); ctx.fill();
  ctx.restore();
}
function tree(x, y, sc, a, col) {
  ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc);
  ctx.fillStyle = '#7a5235'; ctx.beginPath(); ctx.roundRect(-8, -60, 16, 62, 6); ctx.fill();
  ctx.fillStyle = col || '#e6735f'; ctx.beginPath(); ctx.arc(2 * Math.sin(a + x), -90, 46, 0, 6.283); ctx.fill();
  ctx.fillStyle = 'rgba(0,0,0,.08)'; ctx.beginPath(); ctx.arc(14, -78, 30, 0, 6.283); ctx.fill();
  ctx.restore();
}
function drawPrairie(s, a, road = true) {
  screenSpace(); ctx.fillStyle = '#4dc7eb'; ctx.fillRect(0, 0, W, H);
  applyCam();
  const sky = ctx.createLinearGradient(0, -2600, 0, HZ);
  sky.addColorStop(0, '#1a66b8'); sky.addColorStop(.65, '#4dc7eb'); sky.addColorStop(1, '#ffe3a8');
  ctx.fillStyle = sky; ctx.fillRect(-9000, -6000, 18000, 6000 + HZ + 2);
  for (let i = 0; i < 10; i++) {
    const x = ((i * 1300 + a * (8 + i)) % 12000) - 6000, y = -1500 + (i * 397) % 900, w = 260 + (i * 91) % 300;
    ctx.fillStyle = 'rgba(255,255,255,.9)'; ctx.beginPath(); ctx.roundRect(x, y, w, 60, 30); ctx.fill();
    ctx.beginPath(); ctx.roundRect(x + w * .25, y - 34, w * .5, 54, 27); ctx.fill();
  }
  // pradaria de outono: faixas douradas e estrada
  ctx.fillStyle = '#e8b64f'; ctx.fillRect(-9000, HZ, 18000, 6000);
  for (let k = 0; k < 14; k++) { ctx.fillStyle = k % 2 ? 'rgba(201,138,94,.18)' : 'rgba(255,240,200,.12)'; ctx.fillRect(-9000, HZ + 6 + k * k * 9, 18000, 6 + k * 3); }
  if (road) {
  ctx.fillStyle = '#8a9bb5'; ctx.beginPath(); ctx.moveTo(-60, HZ); ctx.lineTo(60, HZ); ctx.lineTo(700, HZ + 2400); ctx.lineTo(-700, HZ + 2400); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#ffd98a'; for (let k = 0; k < 12; k++) { const y = HZ + 30 + k * k * 18; ctx.fillRect(-3 - k, y, 6 + 2 * k, 10 + 4 * k); }
  }
}
function drawDataCenter(s, a, ghost = 0, dx = 0) {
  const k = ghost ? 1 : spring(s - C.bilhoes + .15, .5, 11); if (k <= 0) return;
  ctx.save(); ctx.translate(dx, HZ + 4); ctx.scale(1, k);
  if (ghost) ctx.globalAlpha = ghost;
  const { x0, x1, h } = DC;
  ctx.fillStyle = '#b8c7d6'; ctx.beginPath(); ctx.roundRect(x0, -h, x1 - x0, h, 10); ctx.fill();
  ctx.fillStyle = '#d7e2ec'; ctx.beginPath(); ctx.roundRect(x0, -h, x1 - x0, 30, [10, 10, 0, 0]); ctx.fill();
  for (let x = x0 + 40; x < x1 - 40; x += 90) {   // ventiladores no telhado girando
    ctx.fillStyle = '#8a9bb5'; ctx.beginPath(); ctx.roundRect(x - 30, -h - 28, 60, 30, 8); ctx.fill();
    ctx.fillStyle = '#5c6f8f'; ctx.beginPath(); ctx.ellipse(x, -h - 28, 22, 6 + 3 * Math.sin(a * 9 + x), 0, 0, 6.283); ctx.fill();
  }
  for (let x = x0 + 30; x < x1 - 30; x += 60) { ctx.fillStyle = (Math.floor(a * 3 + x) % 3) ? '#8fd8e6' : '#1a66b8'; ctx.beginPath(); ctx.roundRect(x, -h + 60, 34, 10, 5); ctx.fill(); }
  ctx.restore();
}
function waterTower(x, s) {
  ctx.save(); ctx.translate(x, HZ + 30);
  ctx.fillStyle = '#8a9bb5'; for (const d of [-40, 40]) { ctx.beginPath(); ctx.roundRect(d - 6, -220, 12, 220, 6); ctx.fill(); }
  ctx.fillStyle = '#d7e2ec'; ctx.beginPath(); ctx.roundRect(-90, -330, 180, 120, 60); ctx.fill();
  ctx.restore();
  ctx.save(); ctx.translate(x, HZ + 30);
  riseText('HARWOOD', 0, -258, 34, '#1a66b8', s, T.t1 + .3, 1e9, { ls: 3 });
  ctx.restore();
}
function silo(x) {
  ctx.fillStyle = '#c9d6e3'; ctx.beginPath(); ctx.roundRect(x, HZ - 360, 110, 400, [50, 50, 4, 4]); ctx.fill();
  ctx.fillStyle = '#d7e2ec'; ctx.beginPath(); ctx.roundRect(x + 120, HZ - 300, 90, 340, [44, 44, 4, 4]); ctx.fill();
  ctx.fillStyle = '#8a9bb5'; ctx.beginPath(); ctx.roundRect(x - 60, HZ - 200, 70, 240, 6); ctx.fill();
}
function fargo(a) {   // silhueta de cidade grande ao longe, à direita
  const bx = 5200;
  const B = [[0, 380], [120, 520], [230, 300], [330, 640], [460, 420], [560, 760], [700, 480], [820, 560], [930, 340]];
  for (const [ox, h] of B) {
    ctx.fillStyle = '#5c6f8f'; ctx.beginPath(); ctx.roundRect(bx + ox, HZ - h, 100, h + 10, [12, 12, 0, 0]); ctx.fill();
    ctx.fillStyle = 'rgba(255,217,138,.6)'; for (let y = HZ - h + 30; y < HZ - 20; y += 60) { ctx.fillRect(bx + ox + 20, y, 20, 20); ctx.fillRect(bx + ox + 60, y, 20, 20); }
  }
  return { x: bx + 450, y: HZ - 700 };
}
function coinStack(x, n, s, t0, col) {
  for (let i = 0; i < n; i++) {
    const k = spring(s - (t0 + i * .07), .45, 15); if (k <= 0) continue;
    const y = HZ + 330 - i * 52 - (1 - k) * 260;
    ctx.fillStyle = '#c98a5e'; ctx.beginPath(); ctx.roundRect(x - 110, y - 2, 220, 34, 17); ctx.fill();
    ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(x, y, 110, 26, 0, 0, 6.283); ctx.fill();
  }
}
const fmtUSD = v => 'US$ ' + Math.round(v).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
function drawTown(s, t, a) {
  CAM = townCam(s, t, a);
  drawPrairie(s, a);
  applyCam();
  const F = fargo(a);
  drawDataCenter(s, a);
  silo(-1350);
  waterTower(250, s);
  tree(-1050, HZ + 40, 1, a); tree(-620, HZ + 50, .8, a, '#ffd98a'); tree(140, HZ + 45, .9, a); tree(-400, HZ + 46, .7, a, '#ffd98a');
  for (const [x, sc, col] of HOUSES) house(x, sc, col, a);
  // ---- votos ----
  screenSpace();
  if (s < T.t2 + TD) {
    pill([{ s: 'HARWOOD · DAKOTA DO NORTE', px: 40, c: COL.white, ls: 6 }, { s: 'MENOS DE MIL MORADORES', px: 30, c: COL.teal, ls: 5, w: 600 }].slice(0, s > C.menos2 - .1 ? 2 : 1), W / 2, 120, s, T.t1 + .2, C.tres - .2);
    const kb = spring(s - C.tres, .45, 14);
    if (kb > 0) {
      const bx = 520, by = 150, fill = easeOutCubic((s - C.tres - .1) / .9) * (325 / 430);
      ctx.save(); ctx.translate(bx, by); ctx.scale(kb, kb);
      ctx.fillStyle = 'rgba(6,20,40,.62)'; ctx.beginPath(); ctx.roundRect(-420, -70, 840, 150, 40); ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,.12)'; ctx.beginPath(); ctx.roundRect(-380, 22, 760, 30, 15); ctx.fill();
      ctx.fillStyle = '#5fc47a'; ctx.beginPath(); ctx.roundRect(-380, 22, Math.max(30, 760 * fill), 30, 15); ctx.fill();
      ctx.restore();
      riseText(`${Math.round(325 * clamp(fill / (325 / 430)))} DE 430 VOTOS`, bx, by - 6, 40, COL.gold, s, C.tres + .05, T.t2 - .2, { ls: 5 });
    }
    pill([{ s: 'DATA CENTER DE IA', px: 34, c: COL.white, ls: 5 }, { s: 'US$ 3 BILHÕES', px: 46, c: COL.gold, ls: 6 }], 1300, 260, s, C.bilhoes, T.t2 - .2);
  } else {
    // ---- imposto: contador ao vivo e pilhas de moedas ----
    applyCam();
    coinStack(-420, 1, s, C.seis - .1, '#d7e2ec');
    coinStack(-60, 6, s, C.seis, '#ffd98a');
    screenSpace();
    const sq = storyT(Math.round(CUR_T * FPS) / FPS);   // contador quantizado no quadro: sem dígitos borrados
    const v = 1650000 * easeIO((sq - C.imposto) / Math.max(.6, C.dolares - C.imposto + .2));
    if (s > C.imposto - .1 && s < C.muitos + .2) {
      const k = spring(s - C.imposto, .45, 14), sc = lerp(1.7, 1, k);
      ctx.save(); ctx.translate(W / 2, 170); ctx.scale(sc, sc); ctx.globalAlpha = clamp(k * 2) * (1 - easeIO((s - C.muitos) / .3));
      ctx.fillStyle = 'rgba(6,20,40,.62)'; ctx.beginPath(); ctx.roundRect(-430, -86, 860, 176, 50); ctx.fill();
      ctx.font = FONT(700, 92); ctx.letterSpacing = '5px'; ctx.textAlign = 'center';
      ctx.fillStyle = s > C.dolares ? COL.gold : COL.white; ctx.fillText(fmtUSD(v), 0, 50);
      ctx.restore();
      riseText('IMPOSTOS PREVISTOS', W / 2, 60, 28, COL.teal, s, C.imposto, C.muitos - .2, { ls: 5, w: 600 });
    }
    applyCam();
    const p1 = ws(-420, HZ + 250), p6 = ws(-60, HZ + 10);
    screenSpace();
    pill([{ s: 'CIDADE · 2024', px: 26, c: COL.teal, ls: 4 }], p1.x - 40, p1.y - 60, s, C.seis + .1, C.muitos - .1, { pad: 14 });
    pill([{ s: '6X', px: 44, c: COL.gold, ls: 4 }], p6.x + 30, p6.y - 70, s, C.seis + .35, C.muitos - .1, { pad: 14 });
    // ---- Fargo ao lado ----
    applyCam();
    if (s > C.muitos) {
      const u = easeIO((s - C.fargo + .1) / 1.4);
      if (s > C.fargo - .1) {
        ctx.save(); ctx.setLineDash([30, 26]); ctx.lineDashOffset = -a * 80; ctx.lineCap = 'round';
        ctx.strokeStyle = 'rgba(255,217,138,.95)'; ctx.lineWidth = 14;
        const sx = (DC.x0 + DC.x1) / 2, sy = HZ - DC.h - 120;
        ctx.beginPath(); const n = 40;
        for (let i = 0; i <= n * Math.min(1, u * 1.4); i++) { const k = i / n; const x = lerp(sx, F.x, k), y = lerp(sy, F.y, k) - 600 * Math.sin(Math.PI * k); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
        ctx.stroke(); ctx.restore();
        drawDataCenter(s, a, .45 * Math.sin(Math.PI * clamp(u)), (F.x - (DC.x0 + DC.x1) / 2 - 300) * u);
      }
      screenSpace();
      const fp = ws(F.x, F.y);
      pill([{ s: 'FARGO', px: 44, c: COL.white, ls: 7 }, { s: 'A 16 KM', px: 30, c: COL.teal, ls: 5 }], fp.x, fp.y - 60, s, C.fargo - .05, T.t4 - .2);
    }
  }
}

// ---------------------------------------------------------------------
//  CENA 3: A VARANDA DO MARK
// ---------------------------------------------------------------------
const MK = { x: 0, y: 180 };
function porchCam(s, a) {
  let c;
  if (s < T.t3 + TD) c = keyed([[T.t2, 0, -80, .5], [T.t2 + .8, 60, -120, .82], [C.sua, 260, -170, .78], [C.mark1, 60, -160, .95], [C.topou - .3, 120, -170, 1.05], [T.t3, 100, -170, 1.1]], s);
  else c = keyed([[T.t4, 0, -80, .5], [T.t4 + .8, 120, -140, .85], [C.fa, 160, -150, .98]], s);
  c = breathe(c, a);
  return shake(c, 8 * kick(s - C.topou, .4, 20), a);
}
function drawBill(x, y, s, a, rising, okAt) {
  const k = spring(s - C.sua, .45, 14); if (k <= 0) return;
  const frozen = s > okAt, shakeA = frozen ? 0 : 4 * Math.sin(a * 40) * clamp((s - C.conta1) / .5);
  ctx.save(); ctx.translate(x + shakeA, y); ctx.rotate(-.06); ctx.scale(k, k);
  ctx.fillStyle = 'rgba(6,20,40,.35)'; ctx.beginPath(); ctx.roundRect(-150, -190, 310, 400, 26); ctx.fill();
  ctx.fillStyle = '#f3f7fb'; ctx.beginPath(); ctx.roundRect(-160, -200, 310, 400, 26); ctx.fill();
  ctx.fillStyle = '#ffd98a'; ctx.beginPath(); ctx.moveTo(-10, -170); ctx.lineTo(-50, -90); ctx.lineTo(-12, -90); ctx.lineTo(-34, -20); ctx.lineTo(30, -110); ctx.lineTo(-6, -110); ctx.lineTo(20, -170); ctx.closePath(); ctx.fill();
  for (let i = 0; i < 3; i++) { ctx.fillStyle = '#d7e2ec'; ctx.beginPath(); ctx.roundRect(-120, 20 + i * 34, 200 - i * 40, 14, 7); ctx.fill(); }
  ctx.restore();
  ctx.save(); ctx.translate(x + shakeA, y); ctx.rotate(-.06); ctx.scale(k, k);
  riseText('CONTA DE LUZ', -5, 12 - 60 + 40, 26, '#0b1e33', s, C.sua + .1, 1e9, { ls: 3 });
  const val = 112 + (frozen ? okAt - C.conta1 : Math.max(0, s - C.conta1)) * 38 * rising;
  ctx.font = FONT(700, 56); ctx.letterSpacing = '2px'; ctx.textAlign = 'center';
  ctx.fillStyle = frozen ? '#3a9d62' : '#e6735f'; ctx.fillText('US$ ' + Math.round(val), -5, 175);
  // carimbo "SEM AUMENTO"
  const ks = spring(s - okAt, .42, 15);
  if (ks > 0) {
    ctx.save(); ctx.translate(0, 60); ctx.rotate(-.18); const sc = lerp(1.8, 1, ks); ctx.scale(sc, sc); ctx.globalAlpha = clamp(ks * 2);
    ctx.fillStyle = '#5fc47a'; ctx.beginPath(); ctx.roundRect(-150, -36, 300, 72, 22); ctx.fill();
    ctx.fillStyle = '#ffffff'; ctx.font = FONT(700, 34); ctx.letterSpacing = '3px'; ctx.fillText('SEM AUMENTO', 0, 12);
    ctx.restore();
  }
  ctx.restore();
}
function drawRobot(x, y, s, a, t0) {
  const k = spring(s - t0, .45, 13); if (k <= 0) return;
  const refused = s > C.fa + .15, droop = refused ? easeOutCubic((s - C.fa - .15) / .5) : 0;
  const rx = x + lerp(500, 0, easeOutCubic((s - t0) / .8)) + droop * 120;
  const bob = 6 * Math.sin(a * 5);
  ctx.save(); ctx.translate(rx, y + bob); ctx.scale(k, k);
  ctx.fillStyle = 'rgba(80,50,30,.25)'; ctx.beginPath(); ctx.ellipse(0, 6 - bob, 60, 10, 0, 0, 6.283); ctx.fill();
  ctx.fillStyle = '#8fd8e6'; ctx.beginPath(); ctx.roundRect(-48, -110, 96, 104, 30); ctx.fill();
  ctx.save(); ctx.translate(0, -122); ctx.rotate(droop * .35);
  ctx.fillStyle = '#d7e2ec'; ctx.beginPath(); ctx.roundRect(-44, -70, 88, 70, 26); ctx.fill();
  ctx.fillStyle = '#0b1e33'; ctx.beginPath(); ctx.roundRect(-34, -58, 68, 44, 18); ctx.fill();
  ctx.fillStyle = '#8fd8e6';
  for (const d of [-1, 1]) { ctx.beginPath(); ctx.ellipse(d * 14, -36 + droop * 4, 7, 9 * (1 - droop * .6), 0, 0, 6.283); ctx.fill(); }
  ctx.fillStyle = '#c9d6e3'; ctx.beginPath(); ctx.roundRect(-3, -96, 6, 28, 3); ctx.fill();
  ctx.fillStyle = (Math.floor(a * 3) % 2) ? '#ff8a7a' : '#ffd98a'; ctx.beginPath(); ctx.arc(0, -98, 8, 0, 6.283); ctx.fill();
  ctx.restore();
  // coração oferecido (cai quando ele recusa)
  const hy = -70 + droop * 70, hs = 1 - droop * .4;
  ctx.save(); ctx.translate(-70, hy); ctx.scale(hs, hs); ctx.fillStyle = '#ff8a7a';
  ctx.beginPath(); ctx.moveTo(0, 18); ctx.bezierCurveTo(-34, -6, -22, -34, 0, -16); ctx.bezierCurveTo(22, -34, 34, -6, 0, 18); ctx.fill(); ctx.restore();
  ctx.fillStyle = '#5c6f8f'; ctx.beginPath(); ctx.roundRect(-64, -60, 30, 14, 7); ctx.fill();
  ctx.restore();
}
function drawPorch(s, t, a) {
  CAM = porchCam(s, a);
  drawPrairie(s, a, false);
  applyCam();
  // data center ao fundo, pequeno, no horizonte (continuidade)
  ctx.save(); ctx.translate(900, -2); ctx.scale(.45, .45); drawDataCenter(s, a); ctx.restore();
  // casa do Mark: parede de tábuas, janela, porta, telhado da varanda
  ctx.fillStyle = '#f3f7fb'; ctx.fillRect(-1400, -900, 1100, 1100);
  for (let y = -900; y < 200; y += 44) { ctx.fillStyle = 'rgba(11,30,51,.07)'; ctx.fillRect(-1400, y, 1100, 10); }
  ctx.fillStyle = '#1b3f63'; ctx.beginPath(); ctx.roundRect(-900, -520, 260, 230, 18); ctx.fill();
  ctx.fillStyle = '#ffe3a8'; ctx.beginPath(); ctx.roundRect(-884, -504, 228, 198, 12); ctx.fill();
  ctx.fillStyle = '#5b3a2e'; ctx.beginPath(); ctx.roundRect(-560, -470, 170, 480, 14); ctx.fill();
  ctx.fillStyle = '#ffd98a'; ctx.beginPath(); ctx.arc(-420, -230, 10, 0, 6.283); ctx.fill();
  ctx.fillStyle = '#5b3a2e'; ctx.beginPath(); ctx.moveTo(-1500, -760); ctx.lineTo(900, -760); ctx.lineTo(820, -680); ctx.lineTo(-1500, -680); ctx.closePath(); ctx.fill();
  for (const px of [-260, 560]) { ctx.fillStyle = '#f3f7fb'; ctx.beginPath(); ctx.roundRect(px - 14, -690, 28, 880, 10); ctx.fill(); }
  // piso da varanda
  ctx.fillStyle = '#a86e48'; ctx.fillRect(-1600, 180, 2700, 900);
  for (let k = 0; k < 8; k++) { ctx.fillStyle = k % 2 ? '#9a6440' : '#b5784f'; ctx.fillRect(-1600, 180 + k * 40, 2700, 20); }
  ctx.fillStyle = 'rgba(0,0,0,.15)'; ctx.fillRect(-1600, 180, 2700, 12);
  // Mark
  const segA = s < T.t3 + TD;
  const thumbs = segA ? spring(s - C.topou, .5, 12) : 0;
  const stop = segA ? 0 : spring(s - (C.fa - .1), .5, 12);
  const look = segA ? (s < C.mark1 ? { x: 600, y: -300 } : { x: 300, y: -260 }) : { x: 700, y: 60 };
  const hand = drawMan(MK.x, MK.y, 1, s, a, {
    shirt: '#d94f4f', plaid: true, pants: '#2b4f7a', longPants: true, hair: '#c9d6e3',
    phoneUp: Math.max(thumbs, stop, segA ? .15 : 0), worry: segA ? (s < C.garantiram ? .7 : 0) : 0, relief: segA && s > C.topou,
    look, kicks: [T.t2 + .2, C.sua, C.mark1, C.topou, T.t4 + .2, C.fa], headTilt: stop ? -.08 * Math.sin(a * 10) * stop : 0
  });
  // polegar para cima / mão espalmada
  if (thumbs > .05 || stop > .05) {
    ctx.fillStyle = SKIN;
    ctx.save(); ctx.translate(hand.x, hand.y);
    if (stop > .05) { ctx.beginPath(); ctx.roundRect(-18, -36, 36, 44, 12); ctx.fill(); for (let f = 0; f < 4; f++) { ctx.beginPath(); ctx.roundRect(-17 + f * 9, -56, 8, 26, 4); ctx.fill(); } }
    else { ctx.beginPath(); ctx.roundRect(-16, -14, 32, 30, 10); ctx.fill(); ctx.beginPath(); ctx.roundRect(-6, -44, 13, 34, 6); ctx.fill(); }
    ctx.restore();
  }
  if (segA) drawBill(470, -260, s, a, 1, C.garantiram + .2);
  else drawRobot(420, MK.y, s, a, C.mas + .15);
  screenSpace();
  if (segA) {
    applyCam(); drawPin(MK.x, MK.y - 400, 1, 'VOCÊ', s, C.sua); screenSpace();
    pill([{ s: 'MARK KERKVLIET', px: 42, c: COL.white, ls: 6 }, { s: 'MORADOR HÁ 40 ANOS', px: 28, c: COL.teal, ls: 5, w: 600 }], 470, 140, s, C.mark1 - .05, T.t3 - .1);
    pill([{ s: 'ASSIM QUE FIQUEI TRANQUILO', px: 32, c: COL.white, ls: 4 }, { s: 'COM O CONSUMO DE ENERGIA, TOPEI', px: 32, c: COL.gold, ls: 4 }], W / 2, H - 140, s, C.topou + .05, T.t3 - .1);
  } else {
    pill([{ s: 'NÃO VIROU FÃ DE IA', px: 38, c: COL.white, ls: 6 }], W / 2, H - 130, s, C.fa + .1, 1e9, { pad: 18 });
  }
}

// =====================================================================
//  COMPOSIÇÃO
// =====================================================================
const SCENES = { globe: drawGlobe, town: drawTown, porch: drawPorch };
const TRANS = [
  { s: T.t1, from: 'globe', to: 'town', mode: 'open' },
  { s: T.t2, from: 'town', to: 'porch', mode: 'open' },
  { s: T.t3, from: 'porch', to: 'town', mode: 'close' },
  { s: T.t4, from: 'town', to: 'porch', mode: 'open' }
];
function sceneAt(s) { let n = 'globe'; for (const tr of TRANS) if (s >= tr.s + TD) n = tr.to; return n; }
function renderLayer(name, s, t, a, layer) {
  const c = layer.getContext('2d'); ctx = c; c.setTransform(1, 0, 0, 1, 0, 0);
  SCENES[name](s, t, a); c.setTransform(1, 0, 0, 1, 0, 0); ctx = mctx;
  return layer;
}
function focusOf(tr, s, a, t) {
  if (tr.from === 'globe') { const saved = CAM; CAM = globeCam(s, a); const h = hwW(s, a); const p = ws(h.x, h.y); CAM = saved; return p; }
  const saved = CAM; CAM = townCam(s, t, a); const p = ws(HOUSES[MARK_HOUSE][0], HZ - 40); CAM = saved; return p;
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
  const t0 = C.contas + .3; if (t < t0) return;
  pill([{ s: 'UMA CIDADE DISSE SIM', px: 110, c: COL.white, ls: 9 }, { s: 'HARWOOD · DAKOTA DO NORTE · 2026', px: 40, c: COL.teal, ls: 7, w: 600 }], W / 2, H - 190, t, t0);
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
