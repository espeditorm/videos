"""Relógio da história: um estado por quadro (24 fps, 90 s, 43 planos, grade de 150 bpm).
Cada quadro guarda pose do robô, câmera, todos os elos da corrente, cidade, clima, efeitos e deixas de som.
Saída: states.pkl (lista de 2160 dicionários) + cues.json (cortes e batidas para a trilha).
"""
import math, json, pickle, sys
import numpy as np
import rig, world as WD
from rig import rx, ry, rz, euler, M4

FPS = 24; DUR = 90.0; NF = int(DUR * FPS)
E8 = 0.2                                  # colcheia a 150 bpm
def ef(n_eighths): return int(round(n_eighths * E8 * FPS))   # colcheia -> quadro

# ------------------------------------------------------------------ planos (duração em colcheias)
SHOTS = [  # (colcheias, nome)
    (20, 'sunrise_wide'), (15, 'city_close'), (10, 'underside'), (10, 'chain_down'), (10, 'anchor'),
    (15, 'port_dock'), (10, 'mech_face'), (10, 'lighthouse'),
    (10, 'storm_west'), (10, 'spout_forms'), (8, 'city_wind'), (7, 'gull_looks'), (5, 'strike_chain'),
    (10, 'discharge'), (8, 'anchor_glow'), (5, 'pin_shears'), (7, 'chain_free'), (10, 'city_drifts'),
    (8, 'chain_sweeps'), (12, 'crane_smash'),
    (5, 'strike_antenna'), (10, 'visor_lights'), (10, 'hand_closes'), (15, 'rises'), (6, 'gull_flies'),
    (12, 'wades'), (9, 'climbs'), (15, 'runs'), (6, 'foot_slam'), (9, 'past_lighthouse'), (9, 'chain_ahead'),
    (12, 'leap'), (6, 'catch'), (16, 'dragged'),
    (12, 'swing_round'), (12, 'wraps'), (12, 'holds'), (18, 'spout_passes'), (10, 'spout_recedes'),
    (12, 'clouds_tear'), (12, 'gull_returns'), (10, 'visor_dims'), (12, 'final_wide'),
]
assert len(SHOTS) == 43 and sum(s[0] for s in SHOTS) == 450
SHOT_T0 = np.cumsum([0] + [s[0] for s in SHOTS])[:-1] * E8
SHOT_F0 = [ef(sum(s[0] for s in SHOTS[:i])) for i in range(43)] + [NF]
def shot_of(f):
    for i in range(43):
        if SHOT_F0[i] <= f < SHOT_F0[i + 1]: return i
    return 42
def ts(name, e=0):   # início do plano + colcheias
    i = [s[1] for s in SHOTS].index(name); return SHOT_T0[i] + e * E8

# ------------------------------------------------------------------ eventos (segundos, na grade de colcheias)
EV = dict(
    strike_chain=ts('strike_chain', 1), discharge_reach=ts('anchor_glow', 2), pin_shear=ts('pin_shears', 1),
    whip=ts('chain_free', 1), crane_hit=ts('crane_smash', 2), strike_antenna=ts('strike_antenna', 1),
    visor_on=ts('visor_lights', 3), hand_close=ts('hand_closes', 3),
)
STEP0 = ts('rises', 12)                    # primeira pisada (47,4 s)
STEP_DT = 0.6                              # uma semínima pontuada no 12/8
N_STEPS = 25                               # 47,4 ... 61,8 (impulso do salto)
EV.update(first_plant=STEP0, takeoff=STEP0 + 24 * STEP_DT, catch=ts('catch', 2), splash=ts('dragged', 2),
          haul=ts('swing_round', 0), wrap_lock=ts('wraps', 6), taut=ts('holds', 2), spout_close=ts('spout_passes', 9),
          sun_break=ts('clouds_tear', 2), gull_land=ts('gull_returns', 9), visor_off=ts('visor_dims', 4),
          gull_off=ts('gull_flies', 2), wade_hit=STEP0 + 5 * STEP_DT, climb_hit=STEP0 + 9 * STEP_DT,
          slam_hit=STEP0 + 16 * STEP_DT)
HITS = ['strike_chain', 'discharge_reach', 'pin_shear', 'whip', 'crane_hit', 'strike_antenna', 'visor_on',
        'hand_close', 'first_plant', 'wade_hit', 'climb_hit', 'slam_hit', 'takeoff', 'catch', 'splash',
        'wrap_lock', 'taut', 'sun_break']
assert len(HITS) == 18

# ------------------------------------------------------------------ utilidades
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def smooth(a, b, x):
    u = clamp((x - a) / (b - a)); return u * u * (3 - 2 * u)
def eio(u):
    u = clamp(u); return 4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2
def lerp(a, b, u): return a + (b - a) * u
def twos(f): return (f // 2) * 2           # animação em dois quadros
def tq(f): return twos(f) / FPS

def ground_zv(x, y):
    """Versão vetorizada de ground_z."""
    x = np.asarray(x, float); y = np.asarray(y, float); D = WD.DOCK; B = WD.BW
    z = WD.seabed_z(x, y)
    z = np.where(y < WD.QUAY_Y, 4.0, z)
    z = np.where((x > D['x0']) & (x < D['x1']) & (y > D['y0']) & (y < D['y1']), D['floor'], z)
    z = np.where((np.abs(x - B['x']) < B['half']) & (y > B['y0']) & (y < B['y1']), B['top'], z)
    z = np.where(np.hypot(x - WD.LIGHTHOUSE[0], y - WD.LIGHTHOUSE[1]) < WD.LH_PLAT_R, WD.LH_PLAT_Z, z)
    return z

def ground_z(x, y):
    """Altura do chão real onde um pé pode pousar."""
    D = WD.DOCK
    if D['x0'] < x < D['x1'] and D['y0'] < y < D['y1']: return D['floor']
    if y < WD.QUAY_Y: return 4.0
    B = WD.BW
    if abs(x - B['x']) < B['half'] and B['y0'] < y < B['y1']: return B['top']
    if math.hypot(x - WD.LIGHTHOUSE[0], y - WD.LIGHTHOUSE[1]) < WD.LH_PLAT_R: return WD.LH_PLAT_Z
    return float(WD.seabed_z(x, y))

# ------------------------------------------------------------------ cidade
CITY_PATH = [(0.0, (0.0, 160.0)), (EV['pin_shear'], (0.0, 160.0)), (EV['crane_hit'], (-28.0, 176.0)),
             (EV['takeoff'], (-58.0, 236.0)), (EV['wrap_lock'], (-78.0, 268.0)), (EV['taut'], (-84.0, 274.0)),
             (DUR, (-84.0, 274.0))]
def city_xy(t):
    for (t0, a), (t1, b) in zip(CITY_PATH[:-1], CITY_PATH[1:]):
        if t <= t1:
            u = (t - t0) / max(1e-6, t1 - t0)
            # deriva começa devagar (inércia) e para com um tranco na trava
            u = u * u * (3 - 2 * u) if t0 >= EV['wrap_lock'] - 1e-6 else (u ** 1.6 if t0 < EV['crane_hit'] else u)
            return np.array(a) + (np.array(b) - np.array(a)) * u
    return np.array(CITY_PATH[-1][1])
def city_mat(t):
    xy = city_xy(t)
    bob = 1.2 * math.sin(t * 0.35)
    tilt = 0.012 * smooth(EV['pin_shear'], EV['pin_shear'] + 3, t) * (1 - smooth(EV['taut'], EV['taut'] + 4, t))
    jolt = 0.006 * math.exp(-max(0, t - EV['taut']) * 1.5) * (t > EV['taut']) * math.sin((t - EV['taut']) * 9)
    R = rx(tilt + jolt) @ ry(-tilt * 0.6)
    return M4(R, (xy[0], xy[1], bob))
def collar_pos(t):
    m = city_mat(t); return m[:3, :3] @ np.array([0, 0, WD.COLLAR_Z]) + m[:3, 3]

# ------------------------------------------------------------------ tromba d'água
SPOUT = [(EV['strike_chain'] - 5.2, (-900.0, 300.0)), (EV['takeoff'], (-520.0, 340.0)), (EV['spout_close'], (-262.0, 404.0)),
         (DUR, (60.0, 900.0))]
def spout_state(t):
    pts = SPOUT
    if t <= pts[0][0]: xy = pts[0][1]
    else:
        xy = pts[-1][1]
        for (t0, a), (t1, b) in zip(pts[:-1], pts[1:]):
            if t <= t1:
                u = (t - t0) / (t1 - t0); xy = (lerp(a[0], b[0], u), lerp(a[1], b[1], u)); break
    w = smooth(pts[0][0], pts[0][0] + 3.5, t) * (1 - smooth(EV['sun_break'] + 1, EV['sun_break'] + 5, t))
    return dict(x=xy[0], y=xy[1], w=w, spin=t * 1.7)

# ------------------------------------------------------------------ clima e luz
def storm_x(t):
    """Massa de nuvens índigo: chega do oeste, depois rasga para o leste."""
    a = -3200 + 3200 * smooth(ts('storm_west'), ts('strike_chain'), t)
    return a + 4200 * smooth(EV['sun_break'] - 0.4, EV['sun_break'] + 5, t)
def cover(t):
    """Quanto o sol está tapado (causa visível: a massa de nuvens sobre o sol, que nasce a leste)."""
    sx = storm_x(t)
    return smooth(-1600, -200, sx) * (1 - smooth(500, 1800, sx))
def sun_euler(t):
    el = math.radians(4 + 9 * t / DUR); az = math.radians(-8)    # nasce a leste, um pouco ao sul
    # direção para onde a luz VAI: do leste para o oeste e para baixo
    d = np.array([-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el)])
    # sol do Blender aponta para -Z local
    z = -d; x = np.cross([0, 0, 1], z); x /= np.linalg.norm(x); y = np.cross(z, x)
    R = np.stack([x, y, z], 1)
    sy = math.asin(-R[2, 0]); sx_ = math.atan2(R[2, 1], R[2, 2]); sz = math.atan2(R[1, 0], R[0, 0])
    return (sx_, sy, sz), d

AMBIENT_BOLTS = [24.3, 25.1, 33.5, 36.6, 44.6, 50.3, 55.1, 58.7, 66.2, 69.9, 74.4, 77.9]
def flash(t):
    """Clarões só existem com um raio visível no céu (ambiente) ou nos golpes."""
    v = 0.0
    for b in [EV['strike_chain'], EV['strike_antenna']]:
        d = t - b
        if -1 / FPS < d < 0.5: v = max(v, 1.0 if d < 2 / FPS else math.exp(-(d - 2 / FPS) * 9))
    for b in AMBIENT_BOLTS:
        d = t - b
        if -1 / FPS < d < 0.3: v = max(v, 0.45 * math.exp(-max(d, 0) * 12))
    return v

# ------------------------------------------------------------------ Unit 07: coreografia
DOCK_ROOT = np.array([-60.0, -182.0, WD.DOCK['floor'] + 5.2])
def seated_local():
    L = {}
    L['spine'] = rx(0.20); L['chest'] = rx(0.10)
    L['neck'] = rx(-0.42) @ rz(0.08); L['head'] = rx(-0.10) @ ry(0.05)
    for sd, s in rig.SIDES.items():
        L[f'hip{sd}'] = rz(s * 0.12) @ rx(1.50)
        L[f'knee{sd}'] = rx(-0.28)
        L[f'ankle{sd}'] = rx(0.95)
        L[f'shoulder{sd}'] = rz(s * 0.38) @ rx(0.10)
        L[f'elbow{sd}'] = rx(0.25)
        L[f'wrist{sd}'] = rx(0.15)
    L = rig.hand_curl(L, 'R', 0.2); L = rig.hand_curl(L, 'L', 0.25)
    return L

# ---------- rota de pisadas
ROUTE = [(-60.0, -170.0), (-60.0, -60.0), (40.0, -18.0), (150.0, 26.0), (170.0, 52.0), (170.0, 238.0)]
def _route_points():
    pts = np.array(ROUTE); seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)])
    return pts, cum
def route_at(s):
    pts, cum = _route_points(); s = clamp(s, 0, cum[-1])
    i = min(len(seg := np.diff(cum)) - 1, int(np.searchsorted(cum, s, side='right') - 1))
    u = (s - cum[i]) / seg[i]; p = pts[i] + (pts[i + 1] - pts[i]) * u
    d = (pts[i + 1] - pts[i]) / seg[i]; return p, d
_pts, _cum = _route_points(); ROUTE_LEN = _cum[-1]
# pisadas: k = 0..24, lado alterna (começa com o esquerdo)
PLANTS = []
for k in range(N_STEPS):
    s = ROUTE_LEN * (k + 1) / N_STEPS * 0.985 + 4
    if k == 0: s = 20.0
    p, d = route_at(s)
    side = 'L' if k % 2 == 0 else 'R'
    nrm = np.array([d[1], -d[0]])               # direita da direção
    off = 7.0 * (1 if side == 'R' else -1)
    q = p + nrm * off
    z = ground_z(q[0], q[1])
    PLANTS.append(dict(t=STEP0 + k * STEP_DT, side=side, pos=np.array([q[0], q[1], z + rig.SOLE_BELOW_ANKLE]), yaw=math.atan2(-d[0], d[1])))
# pés iniciais (sentado, antes de levantar): calculados da pose sentada
def _seated_W():
    return rig.fk(DOCK_ROOT, np.eye(3), seated_local())
_SW = _seated_W()
FOOT0 = {sd: _SW[f'ankle{sd}'][:3, 3].copy() for sd in 'LR'}
FOOTR0 = {sd: _SW[f'ankle{sd}'][:3, :3].copy() for sd in 'LR'}

def yaw_R(yaw): return rz(yaw)
def foot_track(sd, t):
    """Posição/rotação do tornozelo do lado sd, com pisadas plantadas (não deslizam) e balanço em arco."""
    mine = [p for p in PLANTS if p['side'] == sd]
    # antes da primeira pisada deste pé: posição sentada, depois recolhe sob o corpo
    prev = dict(t=-1e9, pos=FOOT0[sd], R=FOOTR0[sd])
    for p in mine:
        if t < p['t']:
            lift = p['t'] - 0.55                       # o pé decola 0,55 s antes de pousar (balanço)
            if sd == 'L' and p is mine[0]: lift = ts('rises', 2)
            if sd == 'R' and p is mine[0]: lift = ts('rises', 6)
            if t <= lift: return prev['pos'], prev['R'], 1.0
            u = eio((t - lift) / (p['t'] - lift))
            a, b = prev['pos'], p['pos']
            pos = a + (b - a) * u
            clear = max(ground_z(*a[:2]), ground_z(*b[:2]), WD.DOCK['top'] if (a[1] < -60) else -99) + 6.0 + rig.SOLE_BELOW_ANKLE
            pos[2] = max(pos[2], lerp(max(a[2], b[2]), clear + 4.0, math.sin(math.pi * u)))
            Rb = yaw_R(p['yaw'])
            Ra = prev['R']
            R = Ra if u < 0.5 else Rb
            R = _slerpR(Ra, Rb @ rx(-0.25 * math.sin(math.pi * u)), u)
            return pos, R, 0.0
        prev = dict(t=p['t'], pos=p['pos'], R=yaw_R(p['yaw']))
    return prev['pos'], prev['R'], 1.0

def _slerpR(A, B, u):
    from scipy.spatial.transform import Rotation as Rot, Slerp
    r = Rot.from_matrix(np.stack([A, B])); return Slerp([0, 1], r)([u]).as_matrix()[0]

def walk_root(t):
    """Pelve durante a caminhada: entre os pés, à frente da pisada, balanço vertical na batida."""
    fl, Rl, _ = foot_track('L', t); fr, Rr, _ = foot_track('R', t)
    mid = (fl + fr) / 2
    # direção de avanço da rota perto daqui
    k = clamp((t - STEP0) / (STEP_DT * (N_STEPS - 1)), 0, 1)
    p, d = route_at(ROUTE_LEN * k)
    yaw = math.atan2(-d[0], d[1])
    lowest = min(fl[2], fr[2]) - rig.SOLE_BELOW_ANKLE
    phase = ((t - STEP0) / STEP_DT) % 1.0
    bob = -2.4 * math.exp(-phase * 6) + 0.8 * math.sin(phase * math.pi)
    reach = 33.5                                       # quadril -> tornozelo confortável
    z = min(fl[2], fr[2]) + reach + 3.0 - 6.5 + bob
    z = min(z, min(fl[2], fr[2]) + 34.0)
    pos = np.array([mid[0] + d[0] * 3.0, mid[1] + d[1] * 3.0, z])
    lean = 0.10 + 0.12 * smooth(ts('runs'), ts('runs', 4), t)
    R = rz(yaw) @ rx(-lean)
    return pos, R, yaw

def leap_state(t):
    """Salto: parábola do impulso até cair no mar; pega o último elo em 'catch'."""
    t0, t1 = EV['takeoff'], EV['splash']
    p0, R0, yaw0 = walk_root(t0)
    land = np.array([126.0, 334.0, float(WD.seabed_z(126, 334)) + 30.0])
    u = clamp((t - t0) / (t1 - t0))
    pos = p0 + (land - p0) * u
    pos[2] = lerp(p0[2], land[2], u) + 4 * 62.0 * u * (1 - u)
    yaw = math.atan2(-(land[0] - p0[0]), land[1] - p0[1])
    R = rz(yaw) @ rx(-0.15 - 0.25 * math.sin(math.pi * u))
    return pos, R

def mech_state(t, chain_end=None, chain_prev=None):
    """Pose completa (juntas no mundo) no tempo t (já quantizado em dois)."""
    L = seated_local(); feet = None; hands = {}
    eye = smooth(EV['visor_on'] - 0.05, EV['visor_on'] + 0.15, t) * (1 - smooth(EV['visor_off'], EV['visor_off'] + 0.9, t))
    if t < ts('rises'):
        root, R = DOCK_ROOT.copy(), np.eye(3)
        # desperta: cabeça sobe, mão fecha com tranco
        w = smooth(EV['visor_on'] + 0.2, EV['visor_on'] + 1.2, t)
        L['neck'] = rx(lerp(-0.42, -0.12, w)) @ rz(lerp(0.08, 0.0, w)); L['head'] = rx(lerp(-0.10, 0.04, w))
        hc = smooth(EV['hand_close'] - 0.25, EV['hand_close'], t)
        L = rig.hand_curl(L, 'R', lerp(0.2, 1.0, hc), lerp(0.2, 0.9, hc))
        L['spine'] = rx(lerp(0.20, 0.10, smooth(EV['hand_close'], ts('rises'), t)))
        W = rig.fk(root, R, L)
        return W, eye, root, R
    if t < EV['takeoff']:
        # levantar e caminhar/correr com pés plantados
        rise = smooth(ts('rises'), STEP0 + 0.4, t)
        wr, wR, yaw = walk_root(max(t, STEP0))
        root = DOCK_ROOT + (wr - DOCK_ROOT) * eio(rise)
        if t < STEP0 + 0.4:
            root = DOCK_ROOT + (wr - DOCK_ROOT) * eio(rise); root[2] = lerp(DOCK_ROOT[2], wr[2], eio(rise) ** 0.8)
        R = rig._look(np.array([0, 0, -1.0]), np.array([0, 1.0, 0])) if False else (wR if rise > 0.999 else _slerpR(np.eye(3), wR, eio(rise)))
        L = {}
        L['spine'] = rx(lerp(0.2, 0.06, rise)); L['chest'] = rx(lerp(0.10, 0.04, rise))
        L['neck'] = rx(lerp(-0.12, -0.10, rise)); L['head'] = rx(0.04)
        ph = ((t - STEP0) / (2 * STEP_DT)) * math.tau
        swing = 0.42 * rise * (1 + 0.5 * smooth(ts('runs'), ts('runs', 4), t))
        for sd, s in rig.SIDES.items():
            sgn = 1 if sd == 'R' else -1
            L[f'shoulder{sd}'] = rz(s * lerp(0.38, 0.20, rise)) @ rx(sgn * swing * math.sin(ph))
            L[f'elbow{sd}'] = rx(lerp(0.25, 0.7, rise))
            L[f'wrist{sd}'] = rx(0.1)
        L = rig.hand_curl(L, 'R', 1.0, 0.9); L = rig.hand_curl(L, 'L', lerp(0.25, 0.8, rise), 0.7)
        feet = {sd: foot_track(sd, t)[:2] for sd in 'LR'}
        L, W = rig.solve_pose(root, R, L, feet=feet)
        return W, eye, root, R
    if t < EV['splash'] + 0.01:
        root, R = leap_state(t)
        L = {}
        L['spine'] = rx(0.05); L['chest'] = rx(-0.08); L['neck'] = rx(0.15)
        u = clamp((t - EV['takeoff']) / (EV['splash'] - EV['takeoff']))
        for sd, s in rig.SIDES.items():
            L[f'hip{sd}'] = rx(0.9 * math.sin(math.pi * u) + (0.3 if sd == 'L' else -0.1)) @ rz(s * 0.12)
            L[f'knee{sd}'] = rx(-1.3 * math.sin(math.pi * min(1, u * 1.3)) - 0.1)
            L[f'ankle{sd}'] = rx(0.4)
            L[f'shoulder{sd}'] = rz(s * 0.3) @ rx(0.4)
            L[f'elbow{sd}'] = rx(0.6)
        L = rig.hand_curl(L, 'L', 0.6)
        W = rig.fk(root, R, L)
        # braço direito estica para cima/frente até o elo; depois segura
        grab = 1.0 if t >= EV['catch'] else smooth(EV['takeoff'] + 0.3, EV['catch'], t)
        sh = W['shoulderR'][:3, 3]
        reach = R @ np.array([0.25, 0.65, 0.72]); reach /= np.linalg.norm(reach)
        tgt = sh + reach * 33.0
        if chain_end is not None and t >= EV['catch'] - 0.4:
            tgt = lerp(tgt, chain_end - R @ np.array([0, 0, -5.0]) * 0, smooth(EV['catch'] - 0.4, EV['catch'], t))
        Rh = R @ rx(2.6)
        hands = {'R': (tgt, Rh, R @ np.array([1.0, -0.4, 0]))}
        L = rig.hand_curl(L, 'R', 1.0 if t >= EV['catch'] else 0.15, 1.0 if t >= EV['catch'] else 0.2)
        L, W = rig.solve_pose(root, R, L, hands=hands)
        return W, eye, root, R
    # arrastado pelo mar e depois puxa a corrente em volta do farol
    return haul_state(t, eye)

HAUL_PATH = [(0.0, (126.0, 334.0)), (1.0, (112.0, 352.0)), (2.4, (128.0, 316.0)), (3.7, (132.0, 270.0)),
             (5.0, (150.0, 232.0)), (6.4, (176.0, 214.0))]
def haul_state(t, eye):
    t0 = EV['splash']; tt = t - t0
    pts = HAUL_PATH
    xy = np.array(pts[-1][1])
    for (a0, a), (a1, b) in zip(pts[:-1], pts[1:]):
        if tt <= a1:
            u = eio((tt - a0) / (a1 - a0)); xy = np.array(a) + (np.array(b) - np.array(a)) * u; break
    # olha para a cidade (noroeste) e se inclina para trás, segurando
    c = collar_pos(t)[:2]
    look = c - xy; yaw = math.atan2(-look[0], look[1])
    gz = ground_z(*xy)
    strain = smooth(EV['wrap_lock'], EV['taut'], t)
    dragged = 1 - smooth(t0 + 1.0, t0 + 2.0, t)
    lean = lerp(-0.42, -0.30, strain) + 0.15 * dragged
    shake = 0.010 * strain * math.sin(t * 31) * (t < EV['sun_break'] + 2)
    R = rz(yaw) @ rx(lean + shake)
    z = gz + 42.0 - 6.0 * strain + 8.0 * dragged
    root = np.array([xy[0], xy[1], z])
    L = {}
    L['spine'] = rx(-0.05); L['chest'] = rx(0.05)
    L['neck'] = rx(0.18 - 0.25 * smooth(EV['visor_off'], EV['visor_off'] + 1.2, t))
    W0 = rig.fk(root, R, L)
    # pés: plantados (no arrasto os pés não tocam o fundo)
    feet = {}
    for sd, s in rig.SIDES.items():
        fwd = R @ np.array([0, 1.0, 0]); right = R @ np.array([1.0, 0, 0])
        stance = (-8.0 if sd == 'R' else 9.0)
        p = root[:2] + (right * s * 10.0)[:2] + (fwd * stance)[:2]
        tk = round(tt / 0.4)
        tq_ = t0 + tk * 0.4 if dragged < 0.5 else t
        # pisadas pesadas na grade de semínimas do 3/4: o pé só muda de lugar no meio do passo
        pz = ground_z(*p) + rig.SOLE_BELOW_ANKLE + (6.0 if dragged > 0.5 else 0.0)
        feet[sd] = (np.array([p[0], p[1], pz]), rz(yaw) @ rx(0.15))
    hands = {}
    for sd, s in rig.SIDES.items():
        fwd = R @ np.array([0, 1.0, 0]); right = R @ np.array([1.0, 0, 0]); up = R @ np.array([0, 0, 1.0])
        tgt = W0['chest'][:3, 3] + fwd * 22.0 + up * 4.0 + right * s * 3.5 + fwd * (s * 2.5)
        hands[sd] = (tgt, rz(yaw) @ rx(1.75) @ ry(-s * 0.3), right * s * 0.5 - up)
    L = rig.hand_curl(L, 'R', 1.0); L = rig.hand_curl(L, 'L', 1.0)
    L, W = rig.solve_pose(root, R, L, feet=feet, hands=hands)
    return W, eye, root, R

# ------------------------------------------------------------------ corrente: simulação Verlet determinística
def grip(W, sd='R'):
    """Ponto dentro do punho fechado onde o elo passa."""
    m = W[f'wrist{sd}']; return m[:3, :3] @ np.array([0, 1.6, -7.6]) + m[:3, 3]

def capsules_from(W):
    caps = []
    def seg(a, b, r): caps.append((W[a][:3, 3], W[b][:3, 3], r))
    seg('pelvis', 'neck', 13.0); seg('neck', 'head', 8.0)
    for sd in 'LR':
        seg(f'shoulder{sd}', f'elbow{sd}', 5.0); seg(f'elbow{sd}', f'wrist{sd}', 5.5)
        seg(f'hip{sd}', f'knee{sd}', 6.0); seg(f'knee{sd}', f'ankle{sd}', 6.5)
    return caps

def end_guide(t):
    """Trajetória-guia da ponta solta (puxada por mola; o resto da corrente é física)."""
    keys = [(EV['pin_shear'], WD.SHACKLE + np.array([0, 0, 3.0])), (EV['whip'], np.array([-4.0, 120.0, 40.0])),
            (EV['whip'] + 2.4, np.array([-10.0, 40.0, 120.0])), (EV['crane_hit'], np.array([-8.0, -40.0, 66.0])),
            (EV['crane_hit'] + 2.5, np.array([10.0, -10.0, 4.0])), (EV['crane_hit'] + 9, np.array([70.0, 120.0, 2.0])),
            (EV['takeoff'] - 2.5, np.array([140.0, 280.0, 4.0])), (EV['catch'], None)]
    for (t0, a), (t1, b) in zip(keys[:-1], keys[1:]):
        if t0 <= t < t1:
            if b is None: return None
            u = (t - t0) / (t1 - t0); u = u * u * (3 - 2 * u)
            return a + (b - a) * u
    return None

def simulate_chain(mech_W_at):
    N = WD.N_LINKS; L = WD.LINK_PITCH
    top0 = collar_pos(0.0); bot = WD.SHACKLE.copy()
    # pose inicial: desce do colar, o excesso deita no fundo rumo ao norte
    # pose inicial: reta do colar até um ponto Q no fundo, e daí deitada no fundo até a manilha
    drop = np.linalg.norm(top0 - bot); Ltot = N * L
    dQ = (Ltot ** 2 - drop ** 2) / (2 * Ltot)
    Q = bot + np.array([0, dQ, 0]); Q[2] = float(WD.seabed_z(Q[0], Q[1])) + 4
    l1 = np.linalg.norm(Q - top0)
    pts = []
    for i in range(N + 1):
        s_ = i * L
        if s_ <= l1: pts.append(top0 + (Q - top0) * s_ / l1)
        else: pts.append(Q + (bot - Q) * min(1.0, (s_ - l1) / max(1e-6, np.linalg.norm(bot - Q))))
    P = np.array(pts, float)
    prev = P.copy()
    g = np.array([0, 0, -9.8])
    sub = 16; dt = 1.0 / FPS / sub
    LH = WD.LIGHTHOUSE
    def solve(P, t, W, iters=12):
        caps = capsules_from(W) if W is not None else []
        iu = np.triu_indices(N + 1, 3)
        for it in range(iters):
            d = P[1:] - P[:-1]; ln = np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
            corr = (ln - L) / ln * d * 0.5
            P[:-1] += corr; P[1:] -= corr
            pin_top(P, t); pin_end(P, t, W)
            # chão real (fundo, cais, quebra-mar, plataforma)
            zb = ground_zv(P[:, 0], P[:, 1]) + WD.LINK_W * 0.5
            P[1:, 2] = np.maximum(P[1:, 2], zb[1:])
            # torre do farol
            dx = P[:, 0] - LH[0]; dy = P[:, 1] - LH[1]; r = np.hypot(dx, dy) + 1e-6
            R0 = WD.LH_R0 + 4.6
            m = (P[:, 2] < WD.LH_PLAT_Z + WD.LH_H + 2) & (r < R0); m[0] = False
            P[m, 0] = LH[0] + dx[m] / r[m] * R0; P[m, 1] = LH[1] + dy[m] / r[m] * R0
            # corpo do robô (cápsulas), menos os elos na mão
            for a_, b_, rr in caps:
                ab = b_ - a_; u = np.clip(((P - a_) @ ab) / (ab @ ab), 0, 1)
                c = a_ + u[:, None] * ab; v = P - c; dd = np.linalg.norm(v, axis=1) + 1e-6
                rr2 = rr + 4.2
                m = dd < rr2; m[N - 3:] = False; m[0] = False
                P[m] = c[m] + v[m] / dd[m, None] * rr2
            # autocolisão entre elos não vizinhos
            D = P[iu[0]] - P[iu[1]]; dist = np.linalg.norm(D, axis=1) + 1e-6
            bad = dist < 7.6
            if bad.any():
                push = ((7.6 - dist[bad]) / 2 / dist[bad])[:, None] * D[bad]
                np.add.at(P, iu[0][bad], push); np.add.at(P, iu[1][bad], -push)
        return P
    def pin_top(P, t): P[0] = collar_pos(t) + np.array([0, 0, -2.0])
    def pin_end(P, t, W):
        if t < EV['pin_shear']: P[N] = WD.SHACKLE + np.array([0, 0, 2.0]); return
        if t >= EV['catch'] and W is not None:
            P[N] = grip(W, 'R')
            if t >= EV['splash'] + 0.6: P[N - 2] = grip(W, 'L')
    out = []
    # pré-assentamento (30 s) com o fim preso
    for k in range(30 * FPS // 4):
        v = (P - prev) * 0.9; prev = P.copy(); P = P + v + g * (dt * 4) ** 2 * 1
        P = solve(P, 0.0, None)
    prev = P.copy()
    for f in range(NF):
        t0 = f / FPS
        W = mech_W_at(f)
        for s in range(sub):
            t = t0 + s * dt
            damp = np.where(P[:, 2] < 0, 0.94, 0.995)[:, None]
            v = (P - prev) * damp; prev = P.copy()
            P = P + v + g * dt * dt
            G = end_guide(t)
            if G is not None and t >= EV['pin_shear']:
                k = 0.06 if t < EV['crane_hit'] + 2.5 else 0.03
                P[N] += (G - P[N]) * k
            P = solve(P, t, W, 7)
            prev[0] = P[0]
            if t < EV['pin_shear'] or t >= EV['catch']: prev[N] = P[N]
        out.append(P.copy())
    return np.array(out)

def link_mats(P):
    """Elos: centro no meio do segmento, eixo longo no segmento, malhas alternando 90 graus (transporte paralelo)."""
    mats = []; ref = np.array([1.0, 0, 0])
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]; ax = b - a; ax /= np.linalg.norm(ax)
        n = ref - ax * np.dot(ref, ax)
        if np.linalg.norm(n) < 1e-4: n = np.cross(ax, [0, 0, 1.0])
        n /= np.linalg.norm(n); ref = n
        w = n if i % 2 == 0 else np.cross(ax, n)
        h = np.cross(ax, w)
        R = np.stack([w, ax, h], 1)               # malha do elo: X largura, Y comprimento, Z espessura
        mats.append(M4(R, (a + b) / 2))
    return mats

# ------------------------------------------------------------------ gaivota
def gull_state(t, W):
    nest = W['head'] @ np.array([0, -0.5, 11.4, 1.0])
    headR = W['head'][:3, :3]
    if t < EV['gull_off'] - 0.4 or t >= EV['gull_land']:
        look = 0.0
        if ts('gull_looks') <= t < EV['strike_chain'] + 1: look = 0.6
        R = headR @ rx(0) @ rz(0.4) @ rx(-look * 0.3)
        Mg = M4(R, nest[:3] + np.array([0, 0, 0.8])); wing = 0.15 + (0.9 if abs(t - EV['gull_land']) < 0.25 else 0)
        return dict(M=Mg, wing=wing)
    if t < EV['gull_land'] - 2.0:
        u = t - (EV['gull_off'] - 0.4)
        p = nest[:3] + np.array([30 * math.sin(u * 0.25) + u * 12, -u * 6, 18 * u ** 0.7 + 4])
        if u > 6: p = nest[:3] + np.array([150 * math.cos(u * 0.18), 150 * math.sin(u * 0.18), 120])
        yaw = u * 0.18 + 1.6
        Mg = M4(rz(yaw) @ rx(0.2), p)
        return dict(M=Mg, wing=0.9 * math.sin(t * 9.0))
    u = clamp((t - (EV['gull_land'] - 2.0)) / 2.0)
    far = nest[:3] + np.array([60, -50, 40]); p = far + (nest[:3] + np.array([0, 0, 0.8]) - far) * eio(u)
    Mg = M4(rz(math.atan2(-(nest[0] - far[0]), nest[1] - far[1])) @ rx(-0.3 * u), p)
    return dict(M=Mg, wing=0.9 * math.sin(t * 8) * (1 - u) + 1.0 * u)

# ------------------------------------------------------------------ câmeras
def look_at(pos, tgt, roll=0.0):
    f = np.asarray(tgt, float) - np.asarray(pos, float); f /= np.linalg.norm(f)
    x = np.cross(f, [0, 0, 1.0]); x /= np.linalg.norm(x); y = np.cross(x, f)
    R = np.stack([x, y, -f], 1)
    if roll: R = R @ rz(roll)
    return M4(R, pos)

def cam_for(f, st):
    i = shot_of(f); name = SHOTS[i][1]
    t = f / FPS; u = (f - SHOT_F0[i]) / max(1, SHOT_F0[i + 1] - SHOT_F0[i] - 1)
    U = eio(u)
    J = st['_W']
    head = J['head'][:3, 3] + J['head'][:3, :3] @ np.array([0, 2.0, 5.0])
    pel = J['pelvis'][:3, 3]; chest = J['chest'][:3, 3]
    col = collar_pos(t); city = np.array([*city_xy(t), 480.0])
    LH = np.array([*WD.LIGHTHOUSE, 20.0])
    P = st['_P']
    end = P[-1]
    def L(a, b): return np.asarray(a, float) + (np.asarray(b, float) - np.asarray(a, float)) * U
    lens = 35.0
    if name == 'sunrise_wide': pos = L((-330, -820, 210), (-300, -800, 230)); tgt = L((0, -40, 120), (0, 120, 330)); lens = 30
    elif name == 'city_close': pos = L((300, 30, 520), (270, 60, 532)); tgt = city + np.array([0, 0, 10]); lens = 38
    elif name == 'underside': pos = L((150, 40, 290), (138, 64, 300)); tgt = L((0, 160, 330), (0, 160, 370)); lens = 32
    elif name == 'chain_down': pos = (70, 110, 46); tgt = L((0, 160, 170), (0, 160, -10)); lens = 30
    elif name == 'anchor': pos = L((28, 128, 14), (24, 134, 12)); tgt = (0, 160, -36); lens = 30
    elif name == 'port_dock': pos = L((60, -30, 72), (36, -36, 66)); tgt = (-60, -172, 0); lens = 32
    elif name == 'mech_face': pos = L((-60, -142, 30), (-58, -140, 31)); tgt = head; lens = 55
    elif name == 'lighthouse': pos = L((228, 202, 14), (222, 208, 15)); tgt = LH; lens = 30
    elif name == 'storm_west': pos = (90, 120, 40); tgt = L((-2000, 300, 260), (-2000, 200, 320)); lens = 26
    elif name == 'spout_forms':
        sp = spout_state(t); pos = (-260, 140, 46); tgt = (sp['x'], sp['y'], 180); lens = 45
    elif name == 'city_wind': pos = L((90, 120, 515), (84, 128, 518)); tgt = (20, 150, 525); lens = 36
    elif name == 'gull_looks': pos = L((-48, -158, 46), (-49, -157, 46.5)); tgt = st['_gull'][:3, 3]; lens = 85
    elif name == 'strike_chain': pos = (230, -80, 70); tgt = (0, 160, 210); lens = 26
    elif name == 'discharge':
        z = lerp(300, 20, U); pos = (46, 150, z + 8); tgt = (0, 160, z - 30); lens = 32
    elif name == 'anchor_glow': pos = L((26, 140, 12), (24, 142, 11)); tgt = WD.SHACKLE; lens = 45
    elif name == 'pin_shears': pos = (16, 150, 6); tgt = WD.SHACKLE + np.array([0, 0, -1.5]); lens = 85
    elif name == 'chain_free': pos = (70, 70, 24); tgt = L((0, 150, 30), (0, 120, 110)); lens = 26
    elif name == 'city_drifts': pos = L((90, -330, 140), (80, -320, 150)); tgt = city + np.array([0, 0, -80]); lens = 24
    elif name == 'chain_sweeps': pos = (100, -170, 34); tgt = end; lens = 26
    elif name == 'crane_smash': pos = (70, -10, 24); tgt = L((-8, -60, 50), (-8, -80, 30)); lens = 26
    elif name == 'strike_antenna': pos = (-10, -120, 52); tgt = head + np.array([0, 0, 6]); lens = 32
    elif name == 'visor_lights': pos = L((-60, -150, 29.5), (-60, -151.5, 29.5)); tgt = head; lens = 70
    elif name == 'hand_closes':
        h = J['wristR'][:3, 3]; pos = L(h + np.array([22, 24, 10]), h + np.array([20, 22, 9])); tgt = h + np.array([0, 0, -4]); lens = 40
    elif name == 'rises': pos = L((-28, -98, -6.5), (-30, -100, -6)); tgt = chest + np.array([0, 0, 6]); lens = 22
    elif name == 'gull_flies': pos = (-30, -120, 70); tgt = st['_gull'][:3, 3]; lens = 40
    elif name == 'wades': pos = L((30, 50, 14), (50, 60, 14)); tgt = pel; lens = 30
    elif name == 'climbs': pos = L((240, 10, 12), (240, 30, 12)); tgt = pel; lens = 32
    elif name == 'runs': pos = np.array([108.0, pel[1] - 30, 30.0]); tgt = pel + np.array([0, 10, 0]); lens = 32
    elif name == 'foot_slam':
        fp = PLANTS[16]['pos']; pos = fp + np.array([26, -26, 5]); tgt = fp + np.array([0, 0, 2]); lens = 32
    elif name == 'past_lighthouse': pos = L((240, 300, 22), (236, 306, 22)); tgt = pel; lens = 30
    elif name == 'chain_ahead': pos = L((120, 250, 34), (124, 256, 34)); tgt = end; lens = 30
    elif name == 'leap': pos = (214, 316, 9); tgt = pel + np.array([0, 0, 10]); lens = 22
    elif name == 'catch': h = J['wristR'][:3, 3]; pos = h + np.array([30, -20, -6]); tgt = h; lens = 40
    elif name == 'dragged': pos = L((190, 400, 18), (180, 410, 18)); tgt = pel; lens = 28
    elif name == 'swing_round': pos = L((240, 340, 60), (246, 330, 60)); tgt = LH + np.array([-20, 20, 10]); lens = 26
    elif name == 'wraps': pos = L((214, 238, 26), (212, 236, 25)); tgt = LH + np.array([0, 0, -4]); lens = 32
    elif name == 'holds': pos = L((206, 182, 8), (207, 180, 8)); tgt = chest; lens = 22
    elif name == 'spout_passes': pos = L((-60, 30, 400), (-70, 40, 402)); tgt = L((-200, 360, 430), (-260, 420, 430)); lens = 22
    elif name == 'spout_recedes':
        sp = spout_state(t); pos = (-40, 110, 320); tgt = (sp['x'], sp['y'], 300); lens = 32
    elif name == 'clouds_tear': pos = (110, 160, 24); tgt = L((1000, 260, 420), (1000, 220, 520)); lens = 24
    elif name == 'gull_returns': pos = L((head[0] + 40, head[1] - 40, head[2] + 10), (head[0] + 38, head[1] - 38, head[2] + 9)); tgt = head + np.array([0, 0, 8]); lens = 45
    elif name == 'visor_dims':
        fw = J['head'][:3, :3] @ np.array([0, 1.0, 0]); pos = head + fw * 34 + np.array([0, 0, 1.0]); tgt = head; lens = 70
    else: pos = L((520, -230, 120), (640, -330, 150)); tgt = (60, 200, 170); lens = 28
    return look_at(np.asarray(pos, float), tgt), lens

# ------------------------------------------------------------------ efeitos (2D, ancorados em 3D, sempre em dois)
WATERFALLS = [0.6, 2.2, 3.9, 5.2]
def fx_for(f, st, t):
    fx = []
    ta = tq(f)
    P = st['_P']
    for b in [EV['strike_chain']]:
        if -0.5 / FPS <= t - b < 0.45: fx.append(('bolt', dict(a=(-600, 260, 1100), b=tuple(P[8]), seed=int(b * 10), age=t - b, main=True)))
    if -0.5 / FPS <= t - EV['strike_antenna'] < 0.45:
        tip = st['_W']['head'] @ np.array([3.6, -1.0, 19.6, 1.0])
        fx.append(('bolt', dict(a=(-400, -300, 1050), b=tuple(tip[:3]), seed=77, age=t - EV['strike_antenna'], main=True)))
    for b in AMBIENT_BOLTS:
        if 0 <= t - b < 0.25: fx.append(('bolt', dict(a=(-1500 + b * 30 % 900, 900 - b * 40 % 1200, 1100), b=(-1500 + b * 30 % 900 + 60, 900 - b * 40 % 1200, 0), seed=int(b * 10), age=t - b, main=False)))
    # descarga correndo pela corrente
    if EV['strike_chain'] <= ta < EV['discharge_reach'] + 0.6:
        u = clamp((ta - EV['strike_chain'] - 0.2) / (EV['discharge_reach'] - EV['strike_chain'] - 0.2))
        k = int(lerp(8, WD.N_LINKS, u))
        fx.append(('discharge', dict(pts=[tuple(p) for p in P[max(0, k - 6):k + 1]], seed=f // 2)))
    if EV['discharge_reach'] <= ta < EV['pin_shear'] + 0.6:
        fx.append(('sparks', dict(c=tuple(WD.SHACKLE), age=ta - EV['discharge_reach'], seed=3, n=26, r=12)))
    if EV['pin_shear'] <= ta < EV['pin_shear'] + 1.4:
        fx.append(('sparks', dict(c=tuple(WD.SHACKLE), age=ta - EV['pin_shear'], seed=5, n=40, r=26)))
        fx.append(('bubbles', dict(c=tuple(WD.SHACKLE), age=ta - EV['pin_shear'], seed=6)))
    if EV['crane_hit'] <= ta < EV['crane_hit'] + 2.0:
        fx.append(('debris', dict(c=(-8, -40, 64), age=ta - EV['crane_hit'], seed=8, n=30, r=40)))
    if EV['hand_close'] - 0.1 <= ta < ts('rises', 15):
        h = st['_W']['wristR'][:3, 3]
        fx.append(('rustflakes', dict(c=tuple(h), age=ta - EV['hand_close'] + 0.1, seed=9, n=30, r=14)))
    if ts('rises') <= ta < STEP0 + 1.5:
        fx.append(('rustflakes', dict(c=tuple(st['_W']['chest'][:3, 3]), age=ta - ts('rises'), seed=10, n=60, r=30)))
    # pés na água: lâminas de água com coroa de espuma, a cada pisada que cai no mar
    for p in PLANTS:
        if p['pos'][2] - rig.SOLE_BELOW_ANKLE < -1 and 0 <= ta - p['t'] < 1.3:
            fx.append(('splash', dict(c=(p['pos'][0], p['pos'][1], 0.0), age=ta - p['t'], size=26, seed=int(p['t'] * 10))))
        elif p['pos'][2] - rig.SOLE_BELOW_ANKLE > -1 and 0 <= ta - p['t'] < 0.5:
            fx.append(('dust', dict(c=tuple(p['pos'] - np.array([0, 0, 4.0])), age=ta - p['t'], seed=int(p['t'] * 10))))
    if EV['splash'] <= ta < EV['splash'] + 2.0:
        pel = st['_W']['pelvis'][:3, 3]
        fx.append(('splash', dict(c=(pel[0], pel[1], 0.0), age=ta - EV['splash'], size=70, seed=12)))
    if EV['splash'] <= ta < EV['splash'] + 2.6:
        pel = st['_W']['pelvis'][:3, 3]
        fx.append(('wake', dict(c=(pel[0], pel[1], 0.0), age=ta - EV['splash'], seed=13, w=40)))
    # pontas da corrente batendo na água
    if EV['pin_shear'] < ta < EV['catch']:
        e = P[-1]
        if e[2] < 4: fx.append(('wake', dict(c=(e[0], e[1], 0.0), age=0.5, seed=f // 2, w=10)))
    # mecha andando no mar: anel de espuma em volta das pernas
    if STEP0 < ta < EV['takeoff'] or ta > EV['splash']:
        for sd in 'LR':
            k = st['_W'][f'knee{sd}'][:3, 3]; a = st['_W'][f'ankle{sd}'][:3, 3]
            if a[2] < 0 < k[2] or (a[2] < 0 and k[2] < 0 and st['_W'][f'hip{sd}'][2, 3] > 0):
                fx.append(('legfoam', dict(c=(a[0], a[1], 0.0), r=7.5, seed=f // 2)))
    # cachoeiras da borda da cidade (sempre)
    C = st['city']
    for k, a in enumerate(WATERFALLS):
        rim = C @ np.array([math.cos(a) * WD.CITY_R * 0.98, math.sin(a) * WD.CITY_R * 0.98, WD.CITY_TOP + 2, 1.0])
        fx.append(('waterfall', dict(top=tuple(rim[:3]), out=(math.cos(a), math.sin(a)), seed=k, f=twos(f))))
    # chuva
    rain = smooth(ts('spout_forms'), ts('city_wind'), t) * (1 - smooth(EV['sun_break'], EV['sun_break'] + 2.5, t))
    if rain > 0.01: fx.append(('rain', dict(amount=rain, f=twos(f))))
    # spray na base da tromba
    sp = st['spout']
    if sp['w'] > 0.05: fx.append(('spoutspray', dict(c=(sp['x'], sp['y'], 0.0), w=sp['w'], f=twos(f))))
    # raios de sol entrando pelo rasgo
    if t > EV['sun_break'] - 0.2: fx.append(('sunrays', dict(a=smooth(EV['sun_break'] - 0.2, EV['sun_break'] + 1.0, t))))
    # corrente esticada vibra / poeira de ferrugem na trava
    if EV['wrap_lock'] <= ta < EV['wrap_lock'] + 1.0:
        fx.append(('rustflakes', dict(c=(WD.LIGHTHOUSE[0], WD.LIGHTHOUSE[1], 16.0), age=ta - EV['wrap_lock'], seed=14, n=40, r=18)))
    if EV['taut'] <= ta < EV['taut'] + 1.2:
        fx.append(('tautlines', dict(pts=[tuple(p) for p in P[::4]], age=ta - EV['taut'])))
    return fx

# ------------------------------------------------------------------ montar todos os quadros
def build():
    # 1) robô em dois quadros (precisa vir antes da corrente: o punho segura o elo)
    mechW = {}
    def W_at(f):
        q = twos(f)
        if q not in mechW:
            mechW[q] = mech_state(q / FPS, chain_end=_end_cache.get(q))
        return mechW[q][0]
    _end_cache = {}
    # primeira passada sem a corrente para ter o punho; a mão vai até onde a ponta chega
    P = simulate_chain(lambda f: W_at(f))
    # segunda passada: a mão alcança a posição real da ponta perto da pegada
    for f in range(NF):
        if EV['catch'] - 0.5 <= f / FPS < EV['catch'] + 0.1: _end_cache[twos(f)] = P[twos(f)][-1]
    mechW.clear()
    P = simulate_chain(lambda f: W_at(f))
    states = []
    for f in range(NF):
        t = f / FPS; ta = tq(f)
        W, eye, root, R = mechW[twos(f)] if twos(f) in mechW else mech_state(ta)
        Pq = P[twos(f)]                         # corrente e efeitos em dois quadros
        st = {'f': f, 't': t, 'shot': shot_of(f), 'shot_name': SHOTS[shot_of(f)][1]}
        st['joints'] = {k: v.tolist() for k, v in W.items()}
        st['_W'] = W; st['_P'] = Pq
        st['links'] = [m.tolist() for m in link_mats(Pq)]
        st['vines'] = {v: (1.0 if ta < ts('rises', 4) or v in ('V_head', 'V_foreR', 'V_shinL') else 0.0) for v in
                       ('V_padR', 'V_padR2', 'V_padL', 'V_head', 'V_chest', 'V_chest2', 'V_foreR', 'V_shinL')}
        g = gull_state(ta, W); st['gull'] = {'M': g['M'].tolist(), 'wing': g['wing']}; st['_gull'] = g['M']
        st['city'] = city_mat(ta); st['mill'] = ta * (0.6 + 2.2 * smooth(ts('storm_west'), ts('city_wind'), ta) * (1 - smooth(EV['sun_break'], EV['sun_break'] + 4, ta)))
        hit = EV['crane_hit']
        st['crane'] = {'tilt': 1.25 * smooth(hit, hit + 1.8, ta) ** 1.8, 'boom': -0.5 * smooth(hit, hit + 0.8, ta)}
        pin = M4(np.eye(3), (0, 0, 0))
        if ta >= EV['pin_shear']:
            d = ta - EV['pin_shear']; pin = M4(rx(d * 3), (d * 3, d * 1.5, -min(d * 4, 6.0)))
        st['pin'] = pin.tolist()
        st['storm_x'] = storm_x(ta); st['spout'] = spout_state(ta)
        se, sd_ = sun_euler(t); st['sun_euler'] = se; st['sun_dir'] = sd_.tolist()
        st['cover'] = cover(t); st['flash'] = flash(t); st['eye'] = eye
        st['antenna_glow'] = math.exp(-max(0, t - EV['strike_antenna']) * 2.5) if t >= EV['strike_antenna'] else 0.0
        st['discharge_glow'] = smooth(EV['strike_chain'], EV['strike_chain'] + .1, t) * (1 - smooth(EV['pin_shear'], EV['pin_shear'] + 1, t))
        cam, lens = cam_for(f, st); st['cam'] = cam.tolist(); st['lens'] = lens
        st['fx'] = fx_for(f, st, t)
        # tremida 2D (aplicada na segunda passada) nos golpes
        sh = 0.0
        for k, a in (('strike_chain', 10), ('pin_shear', 6), ('whip', 8), ('crane_hit', 14), ('strike_antenna', 10), ('first_plant', 8),
                     ('wade_hit', 6), ('climb_hit', 7), ('slam_hit', 12), ('catch', 9), ('splash', 14), ('wrap_lock', 10), ('taut', 12)):
            d = t - EV[k]
            if 0 <= d < 0.6: sh = max(sh, a * math.exp(-d * 7))
        if STEP0 < t < EV['takeoff']:
            d = ((t - STEP0) % STEP_DT); sh = max(sh, 4 * math.exp(-d * 10))
        st['shake'] = sh
        st['city'] = st['city'].tolist()
        states.append(st)
    return states, P

def export(path='states.pkl'):
    states, P = build()
    slim = []
    for st in states:
        d = {k: v for k, v in st.items() if not k.startswith('_')}
        d['chainP'] = st['_P'].tolist()
        slim.append(d)
    with open(path, 'wb') as fh: pickle.dump(slim, fh)
    cues = dict(fps=FPS, dur=DUR, eighth=E8, shots=[dict(name=n, e=e, t0=float(SHOT_T0[i]), f0=SHOT_F0[i]) for i, (e, n) in enumerate(SHOTS)],
                events={k: float(v) for k, v in EV.items()}, hits=HITS, steps=[float(p['t']) for p in PLANTS],
                ambient_bolts=AMBIENT_BOLTS)
    json.dump(cues, open('cues.json', 'w'), indent=1)
    print('frames', len(slim))

if __name__ == '__main__':
    export(sys.argv[1] if len(sys.argv) > 1 else 'states.pkl')
