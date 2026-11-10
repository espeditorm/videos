"""Constrói o mundo inteiro de High Harbor em Blender, só com Python.
Uso: blender -b -P build_scene.py -- out.blend
Cada material escreve AOVs para a segunda passada (tinta e pintura):
  base  = cor da tinta da célula (sem luz)      lit = luz de cel (Shader to RGB do difuso, com sombras)
  lid   = id de linha (fronteiras viram traço) cat = categoria (0 céu,1 robô,2 corrente,3 construção,4 rocha,
          5 nuvem, 6 terreno, 7 cristal, 8 olho, 9 viseira, 10 vegetação, 11 gaivota, 12 cachoeira-âncora, 13 tromba)
"""
import bpy, bmesh, sys, math, os, random
import numpy as np
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(__file__))
import rig, world as WD

random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ------------------------------------------------------------------ coleções
def coll(name, parent=None):
    c = bpy.data.collections.new(name); (parent or sc.collection).children.link(c); return c
C_MAIN = coll('MAIN'); C_SEA = coll('SEA'); C_FX = coll('PROXY')
C_MECH = coll('MECH', C_MAIN); C_CHAIN = coll('CHAIN', C_MAIN); C_PORT = coll('PORT', C_MAIN)
C_CITY = coll('CITY', C_MAIN); C_SKY = coll('SKYC', C_MAIN); C_SEABED = coll('SEABED', C_MAIN)

# ------------------------------------------------------------------ materiais de cel
def _aov(nt, name, sock, is_value):
    n = nt.nodes.new('ShaderNodeOutputAOV'); n.aov_name = name
    nt.links.new(sock, n.inputs['Value' if is_value else 'Color'])

def _hex(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1,)

MATS = {}
def cel(name, color, lid, cat, wear=None, emit=False):
    """Material de cel: a cor vai para AOV 'base'; a luz difusa (com sombra) vira 'lit'."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    dif = nt.nodes.new('ShaderNodeBsdfDiffuse'); dif.inputs['Color'].default_value = (1, 1, 1, 1)
    s2r = nt.nodes.new('ShaderNodeShaderToRGB'); nt.links.new(dif.outputs[0], s2r.inputs[0])
    bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(s2r.outputs['Color'], bw.inputs[0])
    base_sock = None
    if wear is None:
        rgb = nt.nodes.new('ShaderNodeRGB'); rgb.outputs[0].default_value = _hex(color); base_sock = rgb.outputs[0]
    else:
        base_sock = wear(nt, color)
    _aov(nt, 'base', base_sock, False)
    _aov(nt, 'lit', bw.outputs[0], True)
    v = nt.nodes.new('ShaderNodeValue'); v.outputs[0].default_value = lid / 64.0; _aov(nt, 'lid', v.outputs[0], True)
    v2 = nt.nodes.new('ShaderNodeValue'); v2.outputs[0].default_value = cat / 16.0; _aov(nt, 'cat', v2.outputs[0], True)
    oi = nt.nodes.new('ShaderNodeObjectInfo'); mm = nt.nodes.new('ShaderNodeMath'); mm.operation = 'MULTIPLY'; mm.inputs[1].default_value = 1000.0
    nt.links.new(oi.outputs['Random'], mm.inputs[0]); _aov(nt, 'oid', mm.outputs[0], True)
    # superfície visível neutra (a cor final é pintada na segunda passada)
    em = nt.nodes.new('ShaderNodeEmission'); nt.links.new(base_sock, em.inputs['Color'])
    nt.links.new(em.outputs[0], out.inputs['Surface'])
    MATS[name] = m
    return m

def _tex_coord(nt):
    tc = nt.nodes.new('ShaderNodeTexCoord'); return tc

def wear_paint(nt, color):
    """Amarelo de segurança lascado: lascas cinza com primer, escorridos de ferrugem e musgo no que olha para cima.
    Tudo com limiar duro (rampas constantes) para virar manchas chapadas de cel."""
    tc = _tex_coord(nt)
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    # lascas
    n1 = nt.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.22; n1.inputs['Detail'].default_value = 6
    n1.inputs['Roughness'].default_value = 0.65
    nt.links.new(tc.outputs['Object'], n1.inputs['Vector'])
    r1 = nt.nodes.new('ShaderNodeValToRGB'); r1.color_ramp.interpolation = 'CONSTANT'
    r1.color_ramp.elements[0].position = 0; r1.color_ramp.elements[0].color = (0, 0, 0, 1)
    r1.color_ramp.elements[1].position = 0.64; r1.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(n1.outputs['Fac'], r1.inputs[0])
    # escorridos de ferrugem: ruído esticado na vertical
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.4, 1.4, 0.05)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 0.5; n2.inputs['Detail'].default_value = 3
    nt.links.new(mp.outputs[0], n2.inputs['Vector'])
    r2 = nt.nodes.new('ShaderNodeValToRGB'); r2.color_ramp.interpolation = 'CONSTANT'
    r2.color_ramp.elements[0].color = (0, 0, 0, 1); r2.color_ramp.elements[1].position = 0.66; r2.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(n2.outputs['Fac'], r2.inputs[0])
    # musgo nas faces de cima
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Normal'], sep.inputs[0])
    n3 = nt.nodes.new('ShaderNodeTexNoise'); n3.inputs['Scale'].default_value = 0.35; n3.inputs['Detail'].default_value = 4
    nt.links.new(tc.outputs['Object'], n3.inputs['Vector'])
    add = nt.nodes.new('ShaderNodeMath'); add.operation = 'ADD'
    nt.links.new(sep.outputs['Z'], add.inputs[0]); nt.links.new(n3.outputs['Fac'], add.inputs[1])
    r3 = nt.nodes.new('ShaderNodeValToRGB'); r3.color_ramp.interpolation = 'CONSTANT'
    r3.color_ramp.elements[0].color = (0, 0, 0, 1); r3.color_ramp.elements[1].position = 1.18; r3.color_ramp.elements[1].color = (1, 1, 1, 1)
    r3.color_ramp.elements[1].position = 0.999
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY_ADD'; mul.inputs[1].default_value = 1.0; mul.inputs[2].default_value = -0.33
    nt.links.new(add.outputs[0], mul.inputs[0]); nt.links.new(mul.outputs[0], r3.inputs[0])
    c0 = nt.nodes.new('ShaderNodeRGB'); c0.outputs[0].default_value = _hex(color)
    cchip = nt.nodes.new('ShaderNodeRGB'); cchip.outputs[0].default_value = _hex('#7f8790')
    crust = nt.nodes.new('ShaderNodeRGB'); crust.outputs[0].default_value = _hex('#a0532e')
    cmoss = nt.nodes.new('ShaderNodeRGB'); cmoss.outputs[0].default_value = _hex('#6f9e3c')
    def mix(a, b, f):
        m = nt.nodes.new('ShaderNodeMix'); m.data_type = 'RGBA'
        nt.links.new(f, m.inputs['Factor']); nt.links.new(a, m.inputs['A']); nt.links.new(b, m.inputs['B']); return m.outputs['Result']
    x = mix(c0.outputs[0], cchip.outputs[0], r1.outputs['Color'])
    x = mix(x, crust.outputs[0], r2.outputs['Color'])
    x = mix(x, cmoss.outputs[0], r3.outputs['Color'])
    return x

def wear_simple(chip='#6f747a', scale=0.4, th=0.7):
    def f(nt, color):
        tc = _tex_coord(nt)
        n1 = nt.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = scale; n1.inputs['Detail'].default_value = 5
        nt.links.new(tc.outputs['Object'], n1.inputs['Vector'])
        r1 = nt.nodes.new('ShaderNodeValToRGB'); r1.color_ramp.interpolation = 'CONSTANT'
        r1.color_ramp.elements[0].color = _hex(color); r1.color_ramp.elements[1].position = th; r1.color_ramp.elements[1].color = _hex(chip)
        nt.links.new(n1.outputs['Fac'], r1.inputs[0]); return r1.outputs['Color']
    return f

# paleta
cel('yellow', '#f4c22e', 1, 1, wear_paint)
cel('yellow2', '#e9b425', 2, 1, wear_paint)
cel('dark', '#4f5a66', 3, 1, wear_simple('#6b4836', 0.3, 0.72))
cel('metal', '#8e98a3', 4, 1, wear_simple('#9c5a35', 0.5, 0.74))
cel('visor', '#173b4f', 5, 9)
cel('eye', '#ffb347', 6, 8)
cel('chain', '#59616b', 7, 2, wear_simple('#8f4f2c', 0.6, 0.62))
cel('concrete', '#c9c4b8', 8, 3, wear_simple('#b2ad9f', 0.08, 0.6))
cel('concrete_dark', '#9d998f', 9, 3)
cel('crane_red', '#d9534a', 10, 3, wear_simple('#a8473f', 0.3, 0.72))
cel('crane_white', '#eef0ec', 11, 3)
cel('wall_white', '#f3eee4', 12, 3)
cel('roof', '#d8734a', 13, 3, wear_simple('#c25f3c', 0.9, 0.62))
cel('wood', '#8a5a3c', 14, 3)
cel('rock', '#9b8d7e', 15, 4, wear_simple('#86786a', 0.05, 0.55))
cel('rock_dark', '#6f6458', 16, 4)
cel('grass', '#7dbb4f', 17, 6, wear_simple('#6aa846', 0.03, 0.6))
cel('crystal', '#5fd2ff', 18, 7)
cel('iron', '#4a4f57', 19, 2, wear_simple('#7a4329', 0.4, 0.68))
cel('cloud', '#ffffff', 0, 5)
cel('storm', '#3b3f74', 0, 5)
cel('vine', '#4f8f3a', 20, 10)
cel('leaf', '#69ad48', 21, 10)
cel('gull', '#fbfbf8', 22, 11)
cel('gull_wing', '#9aa3ad', 23, 11)
cel('beak', '#f2b632', 24, 11)
cel('nest', '#a77a4c', 25, 10)
cel('light_red', '#e04a3c', 26, 3)
cel('light_white', '#f6f4ee', 27, 3)
cel('glass', '#bfe7ff', 28, 3)
cel('coral_a', '#ff8a7a', 29, 10)
cel('coral_b', '#ffd36a', 30, 10)
cel('coral_c', '#b98cff', 31, 10)
cel('sand', '#d9c89a', 32, 6)
cel('container_a', '#3b7fc4', 33, 3)
cel('container_b', '#e0823c', 34, 3)
cel('container_c', '#4aa36b', 35, 3)
cel('boat_blue', '#2f6fb5', 36, 3)
cel('spout', '#9fb2d6', 37, 13)
cel('windmill', '#efe6d4', 38, 3)
cel('tetra', '#bdb7aa', 39, 3, wear_simple('#a59f92', 0.15, 0.62))
cel('seabed', '#7fae9e', 0, 6)

# ------------------------------------------------------------------ geometria
def mesh_obj(name, bm, mat, col, index=0):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    me.materials.append(MATS[mat] if isinstance(mat, str) else mat)
    ob = bpy.data.objects.new(name, me); col.objects.link(ob); ob.pass_index = index
    return ob

def rbox(name, size, bevel, mat, col, index=0, seg=2):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(bevel, min(size) * 0.45), segments=seg, affect='EDGES', profile=0.5)
    return mesh_obj(name, bm, mat, col, index)

def cyl(name, r1, r2, h, mat, col, seg=24, index=0, cap=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, segments=seg, radius1=r1, radius2=r2, depth=h)
    return mesh_obj(name, bm, mat, col, index)

def add_mod_bevel(ob, w, seg=2):
    m = ob.modifiers.new('bev', 'BEVEL'); m.width = w; m.segments = seg; m.limit_method = 'ANGLE'

# ------------------------------------------------------------------ Unit 07
mech_parts = {}
for i, (pname, (j, c, size, bev, mat)) in enumerate(rig.PARTS.items()):
    ob = rbox('M_' + pname, size, bev, mat, C_MECH, index=1)
    mech_parts[pname] = ob
# luzes dos olhos: dois discos na viseira (presos à cabeça)
for k, x in enumerate((-2.6, 2.6)):
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=20)
    for v in bm.verts: v.co = Vector((x + v.co.x * 1.15, 6.6, 5.6 + v.co.y * 0.7))
    mesh_obj(f'M_eye{k}', bm, 'eye', C_MECH, index=1)
# ninho de gravetos no alto da cabeça
bm = bmesh.new()
for k in range(26):
    a = k / 26 * math.tau; r = 3.0 + random.random() * 0.6
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((math.cos(a) * r, math.sin(a) * r - 0.5, 10.6 + random.random() * 0.6)) @ Matrix.Rotation(a + 1.2, 4, 'Z') @ Matrix.Diagonal((3.4, 0.45, 0.45, 1)))
bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=3.0, radius2=3.6, depth=0.8, matrix=Matrix.Translation((0, -0.5, 10.3)))
mesh_obj('M_nest', bm, 'nest', C_MECH, index=1)
# cipós pendurados (presos às peças, balançam com elas)
def vine(name, pts, parent_col, r=0.35):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 1
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts): p.co = (q[0], q[1], q[2], 1)
    cu.materials.append(MATS['vine'])
    ob = bpy.data.objects.new(name, cu); parent_col.objects.link(ob); ob.pass_index = 1; return ob
VINES = {   # nome: (peça, pontos no quadro da peça)
    'V_padR': ('padR', [(4, 6, 4), (5, 7.2, -2), (5.5, 7.6, -9), (5.2, 7.4, -15)]),
    'V_padR2': ('padR', [(-3, 6.8, 4), (-3.5, 7.4, -3), (-3.2, 7.6, -7)]),
    'V_padL': ('padL', [(-4, 6, 4), (-5, 7.2, -3), (-5.2, 7.5, -11)]),
    'V_head': ('head', [(-5.5, 5.8, 9.5), (-6.4, 6.0, 4), (-6.6, 6.2, -1)]),
    'V_chest': ('chest', [(9, 8.4, 14), (10, 8.8, 8), (10.4, 9.2, 1), (10, 9.4, -4)]),
    'V_chest2': ('chest', [(-11, 8.4, 13), (-11.6, 8.8, 6), (-11.4, 9.0, 2)]),
    'V_foreR': ('foreR', [(4.8, 0, 6), (5.6, 1, -1), (5.6, 1.4, -6)]),
    'V_shinL': ('shinL', [(-5.3, 5.6, 6), (-5.8, 6.2, -1), (-5.6, 6.4, -6)]),
}
for vn, (pn, pts) in VINES.items():
    vine(vn, pts, C_MECH)
    # folhas em losango ao longo do cipó
    bm = bmesh.new()
    for a, b in zip(pts[:-1], pts[1:]):
        for u in (0.3, 0.75):
            p = Vector(a).lerp(Vector(b), u)
            for sgn in (-1, 1):
                q = p + Vector((sgn * 0.9, 0.3, -0.3))
                v = [bm.verts.new(q + Vector(d)) for d in ((0, 0, 0.7), (sgn * 0.9, 0.1, 0), (0, 0, -0.7), (-sgn * 0.3, 0, 0))]
                bm.faces.new(v)
    mesh_obj(vn + '_lv', bm, 'leaf', C_MECH, index=1)

# ------------------------------------------------------------------ gaivota
def gull():
    parts = {}
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * 0.55, v.co.y * 1.4, v.co.z * 0.55))
    parts['body'] = mesh_obj('G_body', bm, 'gull', C_MECH, index=2)
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.42)
    for v in bm.verts: v.co += Vector((0, 1.35, 0.45))
    parts['head'] = mesh_obj('G_head', bm, 'gull', C_MECH, index=2)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.16, radius2=0.0, depth=0.6,
                                            matrix=Matrix.Translation((0, 1.95, 0.4)) @ Matrix.Rotation(-math.pi / 2, 4, 'X'))
    parts['beak'] = mesh_obj('G_beak', bm, 'beak', C_MECH, index=2)
    for s, n in ((1, 'R'), (-1, 'L')):
        bm = bmesh.new()
        v = [bm.verts.new(Vector(p)) for p in ((0, 0.5, 0), (s * 2.6, 0.2, 0), (s * 2.9, -0.6, 0), (0, -0.5, 0))]
        bm.faces.new(v)
        parts['wing' + n] = mesh_obj('G_wing' + n, bm, 'gull_wing', C_MECH, index=2)
    return parts
gull()

# ------------------------------------------------------------------ corrente (elos com malhete)
def chain_link_mesh():
    d = WD.LINK_D; L = WD.LINK_L; Wd = WD.LINK_W
    bm = bmesh.new()
    # elo como pista (duas retas + dois semicírculos) varrida por um círculo
    rr = (Wd - d) / 2; straight = L - Wd
    path = []
    for k in range(12):
        a = math.pi + k / 11 * math.pi
        path.append((rr * math.cos(a), -straight / 2 + rr * math.sin(a)))
    for k in range(12):
        a = k / 11 * math.pi
        path.append((rr * math.cos(a), straight / 2 + rr * math.sin(a)))
    n = len(path); ring = 8; verts = []
    for i, (x, y) in enumerate(path):
        x2, y2 = path[(i + 1) % n]; x0, y0 = path[i - 1]
        tx, ty = x2 - x0, y2 - y0; l = math.hypot(tx, ty); nx, ny = ty / l, -tx / l
        row = []
        for k in range(ring):
            a = k / ring * math.tau
            row.append(bm.verts.new((x + nx * math.cos(a) * d / 2, y + ny * math.cos(a) * d / 2, math.sin(a) * d / 2)))
        verts.append(row)
    for i in range(n):
        for k in range(ring):
            bm.faces.new((verts[i][k], verts[(i + 1) % n][k], verts[(i + 1) % n][(k + 1) % ring], verts[i][(k + 1) % ring]))
    # malhete (stud) atravessando o meio
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((Wd - d * 1.2, d * 0.7, d * 0.7, 1)))
    return bm
for i in range(WD.N_LINKS):
    mesh_obj(f'C_link{i:02d}', chain_link_mesh(), 'chain', C_CHAIN, index=3)

# ------------------------------------------------------------------ mundo: porto, cidade, céu, fundo do mar
WD.build_world(globals())

# ------------------------------------------------------------------ mar (camada separada)
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=160, y_segments=160, size=WD.SEA_HALF)
ob = mesh_obj('SEA', bm, 'cloud', C_SEA, index=20)
ob.data.materials[0] = None
seam = bpy.data.materials.new('sea'); seam.use_nodes = True; ob.data.materials[0] = seam
nt = seam.node_tree; nt.nodes.clear()
o = nt.nodes.new('ShaderNodeOutputMaterial'); e = nt.nodes.new('ShaderNodeEmission'); nt.links.new(e.outputs[0], o.inputs[0])

# ------------------------------------------------------------------ luz, câmera, render
sun = bpy.data.lights.new('SUN', 'SUN'); sun.energy = 4.0; sun.angle = math.radians(0.6)
sunob = bpy.data.objects.new('SUN', sun); sc.collection.objects.link(sunob)
cam = bpy.data.cameras.new('CAM'); cam.clip_start = 1.0; cam.clip_end = 30000; cam.sensor_width = 36
camob = bpy.data.objects.new('CAM', cam); sc.collection.objects.link(camob); sc.camera = camob
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.06, 0.1, 1)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

sc.render.engine = 'BLENDER_EEVEE_NEXT'
sc.eevee.taa_render_samples = 1
sc.eevee.use_shadows = True
sc.eevee.shadow_ray_count = 1; sc.eevee.shadow_step_count = 4
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.film_transparent = True
sc.render.fps = 24
sc.view_settings.view_transform = 'Standard'
sc.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
sc.render.image_settings.color_depth = '32'
sc.render.image_settings.exr_codec = 'ZIP'
vl = sc.view_layers[0]; vl.name = 'main'
for n in ('base', 'lid', 'cat', 'oid'):
    a = vl.aovs.add(); a.name = n; a.type = 'COLOR' if n == 'base' else 'VALUE'
a = vl.aovs.add(); a.name = 'lit'; a.type = 'VALUE'
vl.use_pass_z = True; vl.use_pass_normal = True; vl.use_pass_object_index = True
vl.layer_collection.children['SEA'].exclude = True
vl.layer_collection.children['PROXY'].exclude = True
vl2 = sc.view_layers.new('sea')
vl2.use_pass_z = True; vl2.use_pass_normal = True
vl2.layer_collection.children['MAIN'].exclude = True
vl2.layer_collection.children['PROXY'].exclude = True

out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.save_as_mainfile(filepath=out)
print('SAVED', out, len(bpy.data.objects), 'objects')
