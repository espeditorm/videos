"""Aplica um estado do relógio da história (um quadro) na cena do Blender."""
import bpy, math
import numpy as np
from mathutils import Matrix
import rig, world as WD

def _M(a):
    return Matrix([list(r) for r in np.asarray(a, float)])

VINE_PART = {'V_padR': 'padR', 'V_padR2': 'padR', 'V_padL': 'padL', 'V_head': 'head', 'V_chest': 'chest',
             'V_chest2': 'chest', 'V_foreR': 'foreR', 'V_shinL': 'shinL'}
_cache = {}

def objs():
    if not _cache:
        _cache.update({o.name: o for o in bpy.data.objects})
        _cache['_city_rest'] = {o.name: o.matrix_world.copy() for o in bpy.data.objects if o.name.startswith('CITY_')}
        _cache['_crane_rest'] = {o.name: o.matrix_world.copy() for o in bpy.data.objects if o.name.startswith('CRANE0_')}
    return _cache

def apply_state(st):
    O = objs()
    # robô
    W = {k: np.asarray(v) for k, v in st['joints'].items()}
    P = rig.part_mats(W)
    for name, m in P.items(): O['M_' + name].matrix_world = _M(m)
    for k in (0, 1): O[f'M_eye{k}'].matrix_world = _M(W['head'])
    O['M_nest'].matrix_world = _M(W['head'])
    for vn, pn in VINE_PART.items():
        vis = st['vines'].get(vn, 1.0) > 0.5
        for nm in (vn, vn + '_lv'):
            O[nm].matrix_world = _M(P[pn]); O[nm].hide_render = not vis
    # gaivota
    g = st['gull']; G = _M(g['M'])
    for nm in ('G_body', 'G_head', 'G_beak'): O[nm].matrix_world = G
    for sd, s in (('R', 1), ('L', -1)):
        O['G_wing' + sd].matrix_world = G @ Matrix.Rotation(s * g['wing'], 4, 'Y')
    # corrente
    for i, m in enumerate(st['links']): O[f'C_link{i:02d}'].matrix_world = _M(m)
    # cidade (translação + leve inclinação)
    C = _M(st['city'])
    for n, m0 in O['_city_rest'].items():
        O[n].matrix_world = C @ m0
    for k in range(5):
        ob = O[f'CITY_blades{k}']; x, y, a = ob['mill']
        R = Matrix.Rotation(a - math.pi / 2, 4, 'Z') @ Matrix.Rotation(st['mill'] + k * 0.7, 4, 'Y')
        ob.matrix_world = C @ Matrix.Translation((x * 1.0 + math.cos(a) * 6.5, y + math.sin(a) * 6.5, WD.CITY_TOP + 8 + 20)) @ R
    # guindaste derrubado: gira em torno da base (e a lança solta)
    cr = st['crane']
    for n, m0 in O['_crane_rest'].items():
        x, y = WD.CRANE_SMASH
        piv = Matrix.Translation((x + 12, y, 4.0))
        R = Matrix.Rotation(cr['tilt'], 4, 'Y')
        M = piv @ R @ piv.inverted()
        if n.endswith('_boom') or n.endswith('_cab'):
            pv2 = Matrix.Translation((x, y, 64.0))
            M = M @ pv2 @ Matrix.Rotation(cr['boom'], 4, 'X') @ pv2.inverted()
        O[n].matrix_world = M @ m0
    # pino da manilha
    O['SHACKLE_PIN'].matrix_world = _M(st['pin'])
    # nuvens de tempestade e tromba
    O['STORM'].location = (st['storm_x'], 0, 0)
    sp = st['spout']
    O['SPOUT'].location = (sp['x'], sp['y'], -2.0)
    O['SPOUT'].scale = (sp['w'], sp['w'], 1.0)
    O['SPOUT'].rotation_euler = (0, 0, sp['spin'])
    O['SPOUT'].hide_render = sp['w'] < 0.02
    # sol
    O['SUN'].rotation_euler = st['sun_euler']
    # câmera
    cam = O['CAM']; cam.matrix_world = _M(st['cam']); cam.data.lens = st['lens']
