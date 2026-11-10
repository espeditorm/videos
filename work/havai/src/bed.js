// =====================================================================
//  CENA 4: JIM CARREY ACORDA (varanda de frente para a praia)
// =====================================================================
function bathCam(s, a) {
  let c = keyed([[T.t6, 0, -150, .55], [T.t6 + .8, 0, -170, .88], [C.acordou, 20, -190, 1.0], [C.dez - .1, 60, -230, 1.3], [C.FA + .1, 70, -240, 1.42], [C.FA + 1.2, 50, -230, 1.48]], s);
  c = breathe(c, a);
  return shake(c, 6 * kick(s - C.FA, .4, 20), a);
}
function drawBedScene(s, t, a) {
  CAM = bathCam(s, a);
  drawBeach(a, { shadow: false });
  applyCam();
  // varanda de madeira de frente para o mar (sem contornos)
  ctx.fillStyle = '#a86e48'; ctx.fillRect(-4000, 150, 8000, 3000);
  for (let k = 0; k < 9; k++) { ctx.fillStyle = k % 2 ? '#9a6440' : '#b5784f'; ctx.fillRect(-4000, 150 + k * 46, 8000, 23); }
  ctx.fillStyle = 'rgba(0,0,0,.15)'; ctx.fillRect(-4000, 150, 8000, 14);
  // guarda-corpo: corrimão e balaústres preenchidos
  ctx.fillStyle = '#f3f7fb';
  for (let x = -1400; x <= 1400; x += 70) { ctx.beginPath(); ctx.roundRect(x - 7, 20, 14, 132, 7); ctx.fill(); }
  ctx.beginPath(); ctx.roundRect(-1500, 8, 3000, 22, 11); ctx.fill();
  ctx.fillStyle = '#d7e2ec'; ctx.beginPath(); ctx.roundRect(-1500, 26, 3000, 6, 3); ctx.fill();
  // espreguiçadeira: encosto atrás dele
  ctx.fillStyle = '#c98a5e'; ctx.beginPath(); ctx.roundRect(-230, -250, 480, 300, [50, 50, 10, 10]); ctx.fill();
  ctx.fillStyle = '#f3f7fb'; ctx.beginPath(); ctx.roundRect(-200, -220, 420, 250, 40); ctx.fill();
  ctx.fillStyle = '#8fd8e6'; for (let k = 0; k < 4; k++) { ctx.beginPath(); ctx.roundRect(-200, -200 + k * 60, 420, 24, 12); ctx.fill(); }
  // ele, sentado na cama
  const fa = s > C.FA;
  const defl = fa ? (.2 * Math.exp(-(s - C.FA - .1) * 1.4) + kick(s - C.FA - .1, .42, 12) * .1) * (s > C.FA + .08) : 0;
  const look = s < C.dez ? { x: 70, y: -450 } : { x: 120, y: -520 };
  const hand = drawMan(30, 60, 1, s, a, { sit: true, phoneUp: .6, worry: fa ? 0 : .95, relief: fa && s > C.FA + .2, look, kicks: [T.t6 + .2, C.acordou, C.dez], deflate: defl, hug: .5 });
  drawPhone(hand.x + 6, hand.y - 58, 70, s, a, { alert: -10, lines: [{ s: 'MISSILE THREAT', px: 8.6, t: -10 }, { s: 'NOT A DRILL', px: 9, t: -10, c: '#ff8a7a' }], count: C.dez, fa: C.FA, buzz: s > C.FA && s < C.FA + .5 ? 1 : 0 });
  // assento da espreguiçadeira (frente), toalha e pés
  ctx.fillStyle = '#c98a5e'; ctx.beginPath(); ctx.roundRect(-300, -40, 640, 120, 40); ctx.fill();
  ctx.fillStyle = '#ff8a7a'; ctx.beginPath(); ctx.roundRect(-280, -60, 600, 110, 44); ctx.fill();
  ctx.fillStyle = '#ffd98a'; for (let k = 0; k < 5; k++) { ctx.beginPath(); ctx.roundRect(-250 + k * 120, -60, 40, 110, 20); ctx.fill(); }
  ctx.fillStyle = '#a86e48'; ctx.beginPath(); ctx.roundRect(-260, 70, 26, 90, 12); ctx.roundRect(280, 70, 26, 90, 12); ctx.fill();
  ctx.fillStyle = 'rgba(0,0,0,.18)'; ctx.beginPath(); ctx.ellipse(30, 168, 360, 16, 0, 0, 6.283); ctx.fill();
  drawCat(320, -70, .8, s, a, T.t6 + .3, s < C.FA ? hand : { x: 0, y: -300 });
  screenSpace();
  pill([{ s: 'JIM CARREY ESCREVEU', px: 32, c: COL.teal, ls: 5 }], W / 2, 100, s, C.escreveu, C.trinta2 - .1, { pad: 18 });
  pill([{ s: 'ACORDEI NO HAVAÍ', px: 36, c: COL.white, ls: 5 }, { s: 'COM 10 MINUTOS DE VIDA', px: 36, c: COL.gold, ls: 5 }], 1500, 560, s, C.acordou, C.FA - .05);
  pill([{ s: '08:45 · ALARME FALSO', px: 34, c: COL.gold, ls: 5 }], W / 2, H - 110, s, C.FA + .05, C.trinta2 + .3, { pad: 18 });
}
