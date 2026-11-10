// ---------- utilidades ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, u) => a + (b - a) * u;
const easeIO = u => (u = clamp(u), u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2);
const easeOutQuint = u => 1 - Math.pow(1 - clamp(u), 5);
const easeOutCubic = u => 1 - Math.pow(1 - clamp(u), 3);
const easeInCubic = u => clamp(u) ** 3;
const smooth = (a, b, x) => { const u = clamp((x - a) / (b - a)); return u * u * (3 - 2 * u); };
const ramp = (t, t0, d) => clamp((t - t0) / d);
// mola amortecida (damping .45, freq 14): 0 -> 1 com overshoot
function spring(dt, z = .45, w = 14) {
  if (dt <= 0) return 0;
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * dt) * (Math.cos(wd * dt) + (z * w / wd) * Math.sin(wd * dt));
}
// impulso amortecido (0 -> pico -> 0), para squash & stretch e tremidas
function kick(dt, z = .42, w = 16) {
  if (dt <= 0) return 0;
  return Math.exp(-z * w * dt) * Math.sin(w * Math.sqrt(1 - z * z) * dt);
}
function rng(seed) { let s = seed >>> 0 || 1; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; }
const fmtInt = n => Math.floor(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
function fmtDec(x, d) { return x.toFixed(d).replace('.', ','); }

