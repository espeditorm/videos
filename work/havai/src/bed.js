// =====================================================================
//  CENA 4: JIM CARREY ACORDA (quarto)
// =====================================================================
function bathCam(s, a) {
  let c = keyed([[T.t6, 0, -150, .55], [T.t6 + .8, 0, -170, .88], [C.acordou, 20, -190, 1.0], [C.dez - .1, 60, -230, 1.3], [C.FA + .1, 70, -240, 1.42], [C.FA + 1.2, 50, -230, 1.48]], s);
  c = breathe(c, a);
  return shake(c, 6 * kick(s - C.FA, .4, 20), a);
}
function drawBedScene(s, t, a) {
  CAM = bathCam(s, a);
  screenSpace(); drawBackground(a, 0);
  applyCam();
  // parede do quarto com janela de manhã (sem contornos)
  ctx.fillStyle = '#123150'; ctx.beginPath(); ctx.roundRect(-780, -760, 1560, 900, 60); ctx.fill();
  const wg = ctx.createLinearGradient(0, -660, 0, -300);
  wg.addColorStop(0, '#4dc7eb'); wg.addColorStop(1, '#ffd98a');
  ctx.fillStyle = '#1b3f63'; ctx.beginPath(); ctx.roundRect(-640, -680, 380, 400, 34); ctx.fill();
  ctx.fillStyle = wg; ctx.beginPath(); ctx.roundRect(-620, -660, 340, 360, 24); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,.85)'; ctx.beginPath(); ctx.roundRect(-590, -560, 110, 26, 13); ctx.roundRect(-520, -590, 90, 24, 12); ctx.fill();
  ctx.fillStyle = '#3a9d62'; ctx.beginPath(); ctx.ellipse(-450, -300, 200, 70, 0, Math.PI, 0); ctx.fill();
  ctx.fillStyle = '#1b3f63'; ctx.beginPath(); ctx.roundRect(-458, -680, 16, 400, 8); ctx.fill();
  ctx.fillStyle = 'rgba(4,10,24,.45)'; ctx.beginPath(); ctx.ellipse(40, 160, 520, 26, 0, 0, 6.283); ctx.fill();
  // cabeceira e travesseiro
  ctx.fillStyle = '#c98a5e'; ctx.beginPath(); ctx.roundRect(-300, -380, 680, 330, [60, 60, 10, 10]); ctx.fill();
  ctx.fillStyle = '#a86e48'; ctx.beginPath(); ctx.roundRect(-260, -340, 600, 40, 20); ctx.fill();
  ctx.fillStyle = '#f3f7fb'; ctx.beginPath(); ctx.roundRect(-180, -230, 420, 110, 50); ctx.fill();
  // ele, sentado na cama
  const fa = s > C.FA;
  const defl = fa ? (.2 * Math.exp(-(s - C.FA - .1) * 1.4) + kick(s - C.FA - .1, .42, 12) * .1) * (s > C.FA + .08) : 0;
  const look = s < C.dez ? { x: 70, y: -450 } : { x: 120, y: -520 };
  const hand = drawMan(30, 60, 1, s, a, { sit: true, phoneUp: .6, worry: fa ? 0 : .95, relief: fa && s > C.FA + .2, look, kicks: [T.t6 + .2, C.acordou, C.dez], deflate: defl, hug: .5 });
  drawPhone(hand.x + 6, hand.y - 58, 70, s, a, { alert: -10, lines: [{ s: 'MISSILE THREAT', px: 8.6, t: -10 }, { s: 'NOT A DRILL', px: 9, t: -10, c: '#ff8a7a' }], count: C.dez, fa: C.FA, buzz: s > C.FA && s < C.FA + .5 ? 1 : 0 });
  // cobertor (frente) e gato no pé da cama
  ctx.fillStyle = '#ff8a7a'; ctx.beginPath(); ctx.roundRect(-340, -70, 760, 210, [70, 70, 30, 30]); ctx.fill();
  ctx.fillStyle = '#ff9f8f'; ctx.beginPath(); ctx.roundRect(-340, -70, 760, 50, [70, 70, 20, 20]); ctx.fill();
  ctx.fillStyle = '#e6735f'; ctx.beginPath(); ctx.roundRect(-340, 100, 760, 40, [0, 0, 30, 30]); ctx.fill();
  drawCat(330, -60, .8, s, a, T.t6 + .3, s < C.FA ? hand : { x: 0, y: -300 });
  screenSpace();
  pill([{ s: 'JIM CARREY ESCREVEU', px: 32, c: COL.teal, ls: 5 }], W / 2, 100, s, C.escreveu, C.trinta2 - .1, { pad: 18 });
  pill([{ s: 'ACORDEI NO HAVAÍ', px: 36, c: COL.white, ls: 5 }, { s: 'COM 10 MINUTOS DE VIDA', px: 36, c: COL.gold, ls: 5 }], 1500, 560, s, C.acordou, C.FA - .05);
  pill([{ s: '08:45 · ALARME FALSO', px: 34, c: COL.gold, ls: 5 }], W / 2, H - 110, s, C.FA + .05, C.trinta2 + .3, { pad: 18 });
}
