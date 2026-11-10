"""Unit 07: esqueleto, cinemática direta e IK de dois ossos (numpy puro, sem bpy).

Unidades: metros. Eixos locais do robô: +Y frente, +Z cima, +X lado direito do robô.
O mesmo módulo é usado pelo relógio da história, pelo construtor de cena e pelos testes,
então as peças em Blender e a matemática dos poses nunca divergem.
"""
import numpy as np

# ---------------------------------------------------------------- matrizes
def rx(a):
    c, s = np.cos(a), np.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def ry(a):
    c, s = np.cos(a), np.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def rz(a):
    c, s = np.cos(a), np.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def euler(x=0., y=0., z=0.):
    return rz(z) @ ry(y) @ rx(x)
def M4(R=None, t=None):
    m = np.eye(4)
    if R is not None: m[:3, :3] = R
    if t is not None: m[:3, 3] = t
    return m

# ---------------------------------------------------------------- esqueleto
# nome: (pai, deslocamento no quadro do pai em repouso)
SIDES = {'R': 1.0, 'L': -1.0}
JOINTS = {
    'pelvis': (None, (0, 0, 0)),
    'spine': ('pelvis', (0, 0, 4.0)),
    'chest': ('spine', (0, 0, 10.0)),
    'neck': ('chest', (0, 1.0, 14.0)),
    'head': ('neck', (0, 0, 2.5)),
}
for sd, s in SIDES.items():
    JOINTS.update({
        f'shoulder{sd}': ('chest', (s * 16.0, 0, 10.0)),
        f'elbow{sd}': (f'shoulder{sd}', (0, 0, -19.0)),
        f'wrist{sd}': (f'elbow{sd}', (0, 0, -18.0)),
        f'hip{sd}': ('pelvis', (s * 7.5, 0, -3.0)),
        f'knee{sd}': (f'hip{sd}', (0, 0, -19.0)),
        f'ankle{sd}': (f'knee{sd}', (0, 0, -18.0)),
    })
    for i, fx in enumerate((-3.3, 0.0, 3.3)):
        JOINTS[f'f{i}a{sd}'] = (f'wrist{sd}', (fx, 0.6, -8.5))
        JOINTS[f'f{i}b{sd}'] = (f'f{i}a{sd}', (0, 0, -5.0))
    JOINTS[f'tha{sd}'] = (f'wrist{sd}', (-s * 4.6, 2.2, -3.0))
    JOINTS[f'thb{sd}'] = (f'tha{sd}', (0, 0, -4.2))
ORDER = []
def _order(n):
    if n in ORDER: return
    p = JOINTS[n][0]
    if p: _order(p)
    ORDER.append(n)
for _n in JOINTS: _order(_n)

PELVIS_STAND = 44.0       # altura da pelvis com a sola no chão
SOLE_BELOW_ANKLE = 4.0
L_THIGH, L_SHIN = 19.0, 18.0
L_UPPER, L_FORE = 19.0, 18.0

# ---------------------------------------------------------------- peças (caixas arredondadas)
# nome da peça: (junta, centro no quadro da junta, tamanho, raio do chanfro, material)
PARTS = {
    'pelvis': ('pelvis', (0, 0, -0.5), (18, 12, 8), 1.6, 'yellow'),
    'belly': ('spine', (0, 0.4, 4.6), (14, 10, 8.0), 1.6, 'dark'),
    'chest': ('chest', (0, 0.4, 7.6), (27, 16, 15), 2.6, 'yellow'),
    'chestplate': ('chest', (0, 8.4, 6.6), (17, 1.6, 9.5), 0.6, 'yellow2'),
    'collar': ('chest', (0, 0.6, 14.6), (12, 10, 2.6), 0.8, 'dark'),
    'neckp': ('neck', (0, 0, 1.0), (6, 6, 3.6), 0.8, 'dark'),
    'head': ('head', (0, 0.6, 5.0), (12.5, 11, 9.6), 2.8, 'yellow'),
    'visor': ('head', (0, 5.9, 5.6), (11.4, 1.2, 3.6), 1.1, 'visor'),
    'antenna': ('head', (3.6, -1.0, 13.8), (0.7, 0.7, 9.0), 0.3, 'metal'),
    'antennatip': ('head', (3.6, -1.0, 18.6), (1.5, 1.5, 1.5), 0.7, 'metal'),
}
for sd, s in SIDES.items():
    PARTS.update({
        f'pad{sd}': (f'shoulder{sd}', (s * 1.5, 0, 1.5), (12.5, 13.5, 9.0), 2.6, 'yellow'),
        f'upper{sd}': (f'shoulder{sd}', (0, 0, -9.5), (7.2, 7.2, 15.0), 1.6, 'dark'),
        f'elbowp{sd}': (f'elbow{sd}', (0, 0, 0), (8.0, 8.0, 5.0), 2.0, 'metal'),
        f'fore{sd}': (f'elbow{sd}', (0, 0, -9.6), (9.6, 9.6, 15.0), 2.2, 'yellow'),
        f'palm{sd}': (f'wrist{sd}', (0, 0.6, -4.4), (10.4, 5.0, 8.6), 1.6, 'dark'),
        f'thigh{sd}': (f'hip{sd}', (0, 0, -9.6), (9.0, 9.4, 15.6), 2.0, 'dark'),
        f'kneep{sd}': (f'knee{sd}', (0, 1.2, 0.4), (9.6, 9.0, 7.0), 2.4, 'yellow'),
        f'shin{sd}': (f'knee{sd}', (0, 0.4, -10.0), (10.6, 10.6, 15.0), 2.4, 'yellow'),
        f'foot{sd}': (f'ankle{sd}', (0, 3.0, -2.2), (10.6, 16.0, 3.6), 1.4, 'dark'),
        f'heel{sd}': (f'ankle{sd}', (0, -0.5, 0.6), (7.0, 7.0, 4.0), 1.6, 'metal'),
    })
    for i in range(3):
        PARTS[f'f{i}a{sd}'] = (f'f{i}a{sd}', (0, 0, -2.4), (2.7, 3.2, 5.2), 1.0, 'metal')
        PARTS[f'f{i}b{sd}'] = (f'f{i}b{sd}', (0, 0, -2.2), (2.5, 3.0, 4.6), 1.0, 'metal')
    PARTS[f'tha{sd}'] = (f'tha{sd}', (0, 0, -2.0), (2.9, 3.2, 4.6), 1.0, 'metal')
    PARTS[f'thb{sd}'] = (f'thb{sd}', (0, 0, -1.9), (2.6, 3.0, 4.0), 1.0, 'metal')

def adjacent(j1, j2):
    """Peças em juntas pai/filho (ou na mesma junta) se tocam no encaixe: não é atravessar."""
    if j1 == j2: return True
    p1, p2 = JOINTS[j1][0], JOINTS[j2][0]
    return p1 == j2 or p2 == j1 or (p1 == p2 and p1 is not None and (j1.startswith(('f', 'th')) or j2.startswith(('f', 'th'))) is False and False)

# ---------------------------------------------------------------- cinemática direta
def fk(root_pos, root_R, local):
    """local: junta -> matriz 3x3 de rotação local (ausente = identidade). Devolve junta -> 4x4 mundo."""
    W = {}
    for n in ORDER:
        par, off = JOINTS[n]
        R = local.get(n, np.eye(3))
        if par is None:
            W[n] = M4(root_R @ R, np.asarray(root_pos, float))
        else:
            P = W[par]
            W[n] = M4(P[:3, :3] @ R, P[:3, 3] + P[:3, :3] @ np.asarray(off, float))
    return W

def part_mats(W):
    out = {}
    for name, (j, c, size, bev, mat) in PARTS.items():
        m = W[j].copy(); m[:3, 3] = m[:3, 3] + m[:3, :3] @ np.asarray(c, float)
        out[name] = m
    return out

# ---------------------------------------------------------------- IK de dois ossos
def _look(dirv, up_hint):
    """Base cujo -Z aponta para dirv (ossos pendem em -Z) e cujo +Y fica perto de up_hint."""
    z = -dirv / np.linalg.norm(dirv)
    y = up_hint - z * np.dot(up_hint, z)
    if np.linalg.norm(y) < 1e-6: y = np.array([0, 1.0, 0]) - z * z[1]
    y /= np.linalg.norm(y); x = np.cross(y, z)
    return np.stack([x, y, z], 1)

def two_bone(root_world, parent_R, target, l1, l2, pole):
    """Devolve (R1 local, R2 local) para os dois ossos alcançarem target com o joelho/cotovelo para pole."""
    d = target - root_world; L = np.linalg.norm(d)
    L = np.clip(L, abs(l1 - l2) + 1e-3, l1 + l2 - 1e-3)
    dn = d / np.linalg.norm(d)
    # ângulo no primeiro osso pela lei dos cossenos
    a1 = np.arccos(np.clip((l1 * l1 + L * L - l2 * l2) / (2 * l1 * L), -1, 1))
    pn = pole - dn * np.dot(pole, dn); pn /= np.linalg.norm(pn)
    b1 = dn * np.cos(a1) + pn * np.sin(a1)          # direção do primeiro osso
    mid = root_world + b1 * l1
    b2 = (root_world + dn * L) - mid; b2 /= np.linalg.norm(b2)
    W1 = _look(b1, pn)                               # o joelho/cotovelo dobra para o lado do pole
    W2 = _look(b2, pn)
    return parent_R.T @ W1, W1.T @ W2, mid

def solve_pose(root_pos, root_R, local, feet=None, hands=None):
    """Aplica IK nas pernas (feet: lado -> (posição do tornozelo, R do pé no mundo))
    e nos braços (hands: lado -> (posição do punho, R da mão no mundo, pole))."""
    local = dict(local)
    W = fk(root_pos, root_R, local)
    for sd, (tgt, Rfoot) in (feet or {}).items():
        hip = W[f'hip{sd}']
        pole = root_R @ np.array([0, 1.0, 0.25])        # joelho para frente
        R1, R2, _ = two_bone(hip[:3, 3], W['pelvis'][:3, :3], np.asarray(tgt, float), L_THIGH, L_SHIN, pole)
        local[f'hip{sd}'] = R1; local[f'knee{sd}'] = R2
        W = fk(root_pos, root_R, local)
        local[f'ankle{sd}'] = W[f'knee{sd}'][:3, :3].T @ Rfoot
        W = fk(root_pos, root_R, local)
    for sd, (tgt, Rhand, pole) in (hands or {}).items():
        sh = W[f'shoulder{sd}']
        R1, R2, _ = two_bone(sh[:3, 3], W['chest'][:3, :3], np.asarray(tgt, float), L_UPPER, L_FORE, np.asarray(pole, float))
        local[f'shoulder{sd}'] = R1; local[f'elbow{sd}'] = R2
        W = fk(root_pos, root_R, local)
        local[f'wrist{sd}'] = W[f'elbow{sd}'][:3, :3].T @ Rhand
        W = fk(root_pos, root_R, local)
    return local, W

def hand_curl(local, sd, amount, thumb=None):
    """Fecha os dedos (0 aberto, 1 punho). Dedos dobram para a palma (+Y)."""
    local = dict(local)
    for i in range(3):
        local[f'f{i}a{sd}'] = rx(-1.25 * amount)
        local[f'f{i}b{sd}'] = rx(-1.45 * amount)
    t = amount if thumb is None else thumb
    s = SIDES[sd]
    local[f'tha{sd}'] = ry(s * 0.35) @ rx(-0.6 * t)
    local[f'thb{sd}'] = rx(-1.0 * t)
    return local
