// =====================================================================
//  lib_motion.js: princípios de motion design (LottieFiles, MIT) como funções puras do tempo
//  Para os motores da /video-explicativo: todas recebem dt = s - deixa (segundos) e devolvem números.
//  Depende de: clamp, lerp, spring, kick, easeIO, easeOutCubic, easeInCubic (lib_utils.js)
// =====================================================================

// ---------- personalidade do projeto (uma por vídeo, usada em 80% das animações) ----------
// Playful é o padrão para ilustração; os tempos estão em segundos e já adaptados à fala.
const MOTION = {
  playful:   { z: .45, w: 14, over: .18, settle: .45, pre: .12, ant: .10 },
  energetic: { z: .40, w: 18, over: .25, settle: .35, pre: .09, ant: .12 },
  premium:   { z: .70, w: 10, over: .00, settle: .60, pre: .00, ant: .00 },
  corporate: { z: .60, w: 13, over: .03, settle: .45, pre: .06, ant: .04 }
};
let MP = MOTION.playful;

// ---------- emoção da cena -> curva (tabela de emoção para movimento) ----------
const EMO = {
  alegria:  { z: .42, w: 14, amp: 1.0 },   // quica, passa do ponto, sobe em arco
  calma:    { z: .80, w: 6,  amp: .5 },    // lento, contínuo, sem overshoot
  urgencia: { z: .55, w: 22, amp: .8 },    // seco, rápido, em linha reta
  tristeza: { z: .85, w: 5,  amp: .6 },    // lento, cai para baixo
  surpresa: { z: .38, w: 20, amp: 1.2 },   // estoura para fora
  tensao:   { z: .50, w: 18, amp: .9 },    // curto, duro, tremido
  alivio:   { z: .35, w: 8,  amp: .7 }     // mola mole que assenta
};

// ---------- antecipação: o recuo começa ANTES da palavra, e o pico da ação cai na palavra ----------
// devolve o progresso 0 -> 1 com um mergulho negativo (-ant) logo antes de dt = 0
function anticipate(dt, o = MP) {
  if (o.pre <= 0 || dt >= 0) return Math.max(dt >= 0 ? spring(dt, o.z, o.w) : 0, 0);
  if (dt < -o.pre) return 0;
  return -o.ant * Math.sin(Math.PI * (dt + o.pre) / o.pre);   // recua e volta a 0 exatamente na palavra
}
// pop de entrada com antecipação e squash & stretch: devolve { sx, sy } (volume preservado)
function popIn(dt, o = MP) {
  const k = Math.max(0, dt < 0 ? 0 : spring(dt, o.z, o.w));
  const sq = kick(dt - .02, o.z, o.w + 2) * o.over;     // estica na chegada, achata no assentamento
  return { sx: k * (1 - sq * .6), sy: k * (1 + sq) };
}
// impacto de uma ação num elemento que já está na tela (pulo, golpe, carimbo): squash na palavra
function squash(dt, o = MP) {
  const pre = dt < 0 && dt > -o.pre ? Math.sin(Math.PI * (dt + o.pre) / o.pre) * o.ant : 0;   // agacha antes
  const hit = kick(dt, o.z, o.w) * (.16 + o.over * .4);                                     // achata e volta
  const s = pre + hit;
  return { sx: 1 + s * .8, sy: 1 - s };
}

// ---------- continuação e ação sobreposta: partes que chegam depois do corpo ----------
// lag 0,05-0,15 s; mola mais mole que a principal. Use para antena, cabelo, braços, sombra, etiqueta
function follow(dt, lag = .1, o = MP) { return spring(dt - lag, Math.max(.25, o.z - .15), o.w * .7); }
// balanço de apêndice depois de cada parada do corpo (soma dos impulsos atrasados)
function overlap(s, stops, amp = 1, lag = .08) { let v = 0; for (const t of stops) v += kick(s - t - lag, .3, 9); return v * amp; }

// ---------- ação secundária: 30-50% da amplitude, 0,05-0,10 s depois, curva diferente ----------
function secondary(dt, amp = .4, lag = .07) { return amp * easeOutCubic((dt - lag) / .35); }

// ---------- entrada mais longa que saída; saída acelera (ease-in) ----------
const ENTER = .55, EXIT = ENTER / 1.4;
function enterK(dt) { return easeOutQuint(dt / ENTER); }
function exitK(dt) { return 1 - easeInCubic(dt / EXIT); }

// ---------- arcos: nada se move em linha reta (curvatura 10-20% da distância) ----------
function arc(p0, p1, u, bend = .15, up = -1) {
  const dx = p1.x - p0.x, dy = p1.y - p0.y, d = Math.hypot(dx, dy) || 1;
  const off = Math.sin(Math.PI * u) * d * bend;
  return { x: lerp(p0.x, p1.x, u) + (-dy / d) * off * up, y: lerp(p0.y, p1.y, u) + (dx / d) * off * up };
}

// ---------- escalonamento com a regra de 1/3: no máximo ~1/3 dos elementos se movem ao mesmo tempo ----------
// devolve o atraso do item i de n, espalhado em `span` segundos (os primeiros mais rápidos)
function stagger(i, n, span = .6) { const u = n > 1 ? i / (n - 1) : 0; return span * (1 - (1 - u) ** 1.6); }
function staggerSpan(n, each = .25) { return Math.max(.3, each * n / 3); }

// ---------- destaque do herói: o resto escurece para 40-60% enquanto o herói age ----------
function stageDim(s, t0, t1, depth = .5) {
  const inK = easeOutCubic((s - t0 + .1) / .25), outK = easeInCubic((s - t1) / .3);
  return 1 - depth * clamp(inK) * (1 - clamp(outK));     // multiplique o globalAlpha dos coadjuvantes
}

// ---------- três camadas: principal, secundária e ambiente ----------
// ambiente: vida de fundo que nunca para (respiração, brilho, flutuação), seno sem emendas
function ambient(a, f = .4, amp = 1, ph = 0) { return amp * Math.sin(a * f * 2 * Math.PI + ph); }
