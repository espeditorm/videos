"""Layout de High Harbor em escala real (metros, z para cima, +x leste, +y norte, nível do mar z=0).
Constantes usadas por história, cena e testes; build_world() só roda dentro do Blender."""
import math, random
import numpy as np

SEA_HALF = 7000.0
# corrente: elo com malhete, d = 2 m
LINK_D, LINK_L, LINK_W = 2.0, 12.8, 7.2
LINK_PITCH = 8.0
N_LINKS = 56
CHAIN_LEN = N_LINKS * LINK_PITCH
# cidade flutuante
CITY0 = np.array([0.0, 160.0])          # centro em planta no início
CITY_TOP = 470.0                        # superfície da ilha
CITY_R = 165.0
COLLAR_Z = 318.0                        # base do colar de ferro (ponta de baixo)
ANCHOR = np.array([0.0, 160.0, -40.0])  # âncora no fundo
SHACKLE = ANCHOR + np.array([0, 0, 9.0])
# porto
QUAY_Y = -70.0
DOCK = dict(x0=-92.0, x1=-28.0, y0=-205.0, y1=-70.0, floor=-12.0, top=4.0)
CRANE_SMASH = np.array([-8.0, -92.0])
CRANES = [CRANE_SMASH, np.array([62.0, -92.0]), np.array([126.0, -92.0])]
BW = dict(x=170.0, y0=-90.0, y1=250.0, top=6.0, half=11.0)
LIGHTHOUSE = np.array([170.0, 266.0])
LH_PLAT_R, LH_PLAT_Z = 22.0, 6.0
LH_R0, LH_R1, LH_H = 5.6, 4.3, 28.0

def seabed_z(x, y):
    """Fundo: raso (-12) junto ao porto, desce a -40 sob a cidade, sobe para a praia ao sul."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    z = -12.0 - 30.0 * np.exp(-((x - ANCHOR[0]) ** 2 + (y - ANCHOR[1]) ** 2) / (2 * 260.0 ** 2))
    z = np.where(y < QUAY_Y, np.maximum(z, 4.0), z)
    return z

def land_z(x, y):
    """Colina da cidade baixa ao sul do cais (terraços)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    t = np.clip((-y - 210.0) / 600.0, 0, 1)
    return np.where(y < -200.0, 4.0 + 170.0 * t ** 1.3 + 12 * np.sin(x / 140.0) * t, 4.0)


def build_world(g):
    rbox, cyl, mesh_obj, MATS = g['rbox'], g['cyl'], g['mesh_obj'], g['MATS']
    bmesh, Vector, Matrix, bpy = g['bmesh'], g['Vector'], g['Matrix'], g['bpy']
    C_PORT, C_CITY, C_SKY, C_SEABED, C_FX = g['C_PORT'], g['C_CITY'], g['C_SKY'], g['C_SEABED'], g['C_FX']
    rnd = random.Random(11)

    def place(ob, x, y, z, rz=0.0):
        ob.location = (x, y, z); ob.rotation_euler = (0, 0, rz); return ob

    def joined(name, mat, col, builder, index=0):
        bm = bmesh.new(); builder(bm); return mesh_obj(name, bm, mat, col, index)

    def box_into(bm, center, size, rz=0.0):
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(center) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Diagonal((size[0], size[1], size[2], 1)))

    def prism_roof_into(bm, center, sx, sy, h, rz=0.0):
        cx, cy, cz = center
        M = Matrix.Translation(center) @ Matrix.Rotation(rz, 4, 'Z')
        p = [(-sx / 2, -sy / 2, 0), (sx / 2, -sy / 2, 0), (sx / 2, sy / 2, 0), (-sx / 2, sy / 2, 0), (-sx / 2, 0, h), (sx / 2, 0, h)]
        v = [bm.verts.new(M @ Vector(q)) for q in p]
        for f in ((0, 1, 2, 3), (0, 4, 5, 1), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2)): bm.faces.new([v[i] for i in f])

    # -------------------------------------------------------------- terreno e cais
    def terrain(bm):
        n = 120
        xs = np.linspace(-1600, 1600, n); ys = np.linspace(-1400, QUAY_Y, n // 2)
        vv = [[bm.verts.new((x, y, float(land_z(x, y)))) for x in xs] for y in ys]
        for j in range(len(ys) - 1):
            for i in range(n - 1): bm.faces.new((vv[j][i], vv[j][i + 1], vv[j + 1][i + 1], vv[j + 1][i]))
    ter = joined('LAND', 'grass', C_PORT, terrain, index=6)
    # bloco do cais (concreto) com a doca seca escavada
    D = DOCK
    def quay(bm):
        # faixa do cais ao longo da costa, recortada em volta da doca
        def slab(x0, x1, y0, y1, z0=-20.0, z1=4.0):
            box_into(bm, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0))
        slab(-700, D['x0'], -260, QUAY_Y)
        slab(D['x1'], BW['x'] - BW['half'], -260, QUAY_Y)
        slab(D['x0'], D['x1'], -260, D['y0'])
        slab(D['x0'], D['x1'], D['y0'], D['y1'], -20.0, D['floor'])
        # degraus (altares) nas laterais
        for k in range(3):
            box_into(bm, (D['x0'] + 1.5 + k * 1.5, (D['y0'] + D['y1']) / 2, D['floor'] + 1.5 + k * 3), (3 + k * 3 * 0 + 3, D['y1'] - D['y0'] - 4, 3))
            box_into(bm, (D['x1'] - 1.5 - k * 1.5, (D['y0'] + D['y1']) / 2, D['floor'] + 1.5 + k * 3), (3 + 3, D['y1'] - D['y0'] - 4, 3))
    q = joined('QUAY', 'concrete', C_PORT, quay, index=4)
    # portão da doca (caixão) aberto ao norte: baixo, o robô passa por cima
    gate = rbox('DOCKGATE', (D['x1'] - D['x0'], 6.0, 10.0), 0.6, 'iron', C_PORT, index=4)
    place(gate, (D['x0'] + D['x1']) / 2, D['y1'] + 3.0, -7.0)
    # poças no fundo da doca
    for k in range(4):
        p = cyl(f'PUDDLE{k}', 6 + rnd.random() * 6, 6, 0.2, 'glass', C_PORT, seg=16, index=4)
        place(p, rnd.uniform(D['x0'] + 10, D['x1'] - 10), rnd.uniform(D['y0'] + 60, D['y1'] - 20), D['floor'] + 0.1)

    # -------------------------------------------------------------- guindastes de contêiner
    def crane(name, x, y):
        parts = []
        def frame(bm):
            for dx in (-12, 12):
                for dy in (-9, 9):
                    box_into(bm, (dx, dy, 22), (2.4, 2.4, 44))
            for dy in (-9, 9): box_into(bm, (0, dy, 44), (27, 2.6, 3.2))
            for dx in (-12, 12): box_into(bm, (dx, 0, 44), (2.6, 20, 3.2))
            for dx in (-12, 12): box_into(bm, (dx, 0, 18), (2.0, 20, 2.0))
            box_into(bm, (0, 0, 52), (14, 14, 12))          # sala de máquinas
        fr = joined(name + '_frame', 'crane_red', C_PORT, frame, index=5)
        def boom(bm):
            box_into(bm, (0, 22, 62), (5, 92, 4))            # lança sobre a água
            box_into(bm, (0, -24, 62), (5, 30, 4))
            for k in range(9): box_into(bm, (0, -30 + k * 11, 66), (4.4, 1.2, 4.0))
            box_into(bm, (0, 0, 78), (3, 3, 30))             # mastro
        bo = joined(name + '_boom', 'crane_white', C_PORT, boom, index=5)
        def cab(bm): box_into(bm, (0, 30, 56), (6, 6, 5))
        ca = joined(name + '_cab', 'glass', C_PORT, cab, index=5)
        for ob in (fr, bo, ca): place(ob, x, y, 4.0)
        return fr, bo, ca
    for i, c in enumerate(CRANES): crane(f'CRANE{i}', c[0], c[1])
    # contêineres empilhados
    cols = ['container_a', 'container_b', 'container_c', 'crane_red']
    for k in range(4):
        def stack(bm, k=k):
            for i in range(10):
                for j in range(3):
                    for h in range(rnd.randint(1, 4)):
                        if rnd.random() < 0.25 * (k + 1) / 2:
                            box_into(bm, (10 + i * 15.5, -130 - j * 6.0 - k * 22, 4 + 1.3 + h * 2.6), (12.2, 2.44, 2.59))
        joined(f'CONTAINERS{k}', cols[k], C_PORT, stack, index=5)

    # -------------------------------------------------------------- barcos de pesca
    for k in range(9):
        x = -250 + (k % 5) * 22 + rnd.uniform(-3, 3); y = -58 + (k // 5) * 26 + rnd.uniform(-3, 3)
        def hull(bm):
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((4.4, 13.0, 2.6, 1)))
            for v in bm.verts:
                if v.co.z < 0: v.co.x *= 0.55
                if v.co.y > 0: v.co.x *= 0.35 if v.co.z < 0 else 0.5
        h = joined(f'BOAT{k}', 'boat_blue' if k % 2 else 'crane_white', C_PORT, hull, index=7)
        def cabin(bm): box_into(bm, (0, -2.0, 2.4), (3.0, 4.0, 2.4)); box_into(bm, (0, 2, 4.0), (0.3, 0.3, 6))
        c = joined(f'BOATC{k}', 'wall_white' if k % 2 else 'boat_blue', C_PORT, cabin, index=7)
        rz = rnd.uniform(-0.2, 0.2)
        place(h, x, y, 0.3, rz); place(c, x, y, 0.3, rz)

    # -------------------------------------------------------------- quebra-mar, tetrápodes e farol
    B = BW
    def breakwater(bm):
        L = B['y1'] - B['y0']
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((B['x'], (B['y0'] + B['y1']) / 2, (B['top'] - 14) / 2)) @ Matrix.Diagonal((2 * B['half'] + 10, L, B['top'] + 14, 1)))
        for v in bm.verts:
            if v.co.z > 0: v.co.x = B['x'] + math.copysign(B['half'], v.co.x - B['x'])
        bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=LH_PLAT_R + 4, radius2=LH_PLAT_R, depth=LH_PLAT_Z + 14,
                              matrix=Matrix.Translation((LIGHTHOUSE[0], LIGHTHOUSE[1], (LH_PLAT_Z - 14) / 2)))
    joined('BREAKWATER', 'concrete', C_PORT, breakwater, index=8)
    def tetrapod(bm, M):
        for d in ((0, 0, 1), (0.943, 0, -0.333), (-0.471, 0.816, -0.333), (-0.471, -0.816, -0.333)):
            dv = Vector(d); rot = dv.to_track_quat('Z', 'Y').to_matrix().to_4x4()
            bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=1.6, radius2=0.9, depth=3.2,
                                  matrix=M @ Matrix.Translation(dv * 1.6) @ rot)
    def tetras(bm):
        y = B['y0'] + 10
        while y < B['y1'] - 4:
            for side in (1, -1):
                if side < 0 and rnd.random() < 0.55: continue
                x = B['x'] + side * (B['half'] + 4 + rnd.uniform(0, 3))
                M = Matrix.Translation((x, y + rnd.uniform(-1, 1), 1.0 + rnd.uniform(0, 1.5))) @ Matrix.Rotation(rnd.uniform(0, 6.28), 4, 'Z') @ Matrix.Rotation(rnd.uniform(-0.5, 0.5), 4, 'X')
                tetrapod(bm, M)
            y += 7.5
        for k in range(26):
            a = k / 26 * math.tau
            r = LH_PLAT_R + 4.5 + rnd.uniform(0, 3)
            if math.sin(a) < -0.6: continue
            M = Matrix.Translation((LIGHTHOUSE[0] + math.cos(a) * r, LIGHTHOUSE[1] + math.sin(a) * r, 1.0)) @ Matrix.Rotation(rnd.uniform(0, 6.28), 4, 'Z')
            tetrapod(bm, M)
    joined('TETRAPODS', 'tetra', C_PORT, tetras, index=8)
    # farol listrado vermelho e branco
    nb = 6
    for k in range(nb):
        h = LH_H / nb; r0 = LH_R0 + (LH_R1 - LH_R0) * k / nb; r1 = LH_R0 + (LH_R1 - LH_R0) * (k + 1) / nb
        b = cyl(f'LH_band{k}', r0, r1, h, 'light_red' if k % 2 == 0 else 'light_white', C_PORT, seg=28, index=9)
        place(b, LIGHTHOUSE[0], LIGHTHOUSE[1], LH_PLAT_Z + h * (k + 0.5))
    g1 = cyl('LH_gallery', 6.2, 6.2, 1.0, 'iron', C_PORT, seg=28, index=9); place(g1, *LIGHTHOUSE, LH_PLAT_Z + LH_H + 0.5)
    g2 = cyl('LH_lantern', 3.3, 3.3, 4.2, 'glass', C_PORT, seg=16, index=9); place(g2, *LIGHTHOUSE, LH_PLAT_Z + LH_H + 3.1)
    g3 = cyl('LH_cap', 4.0, 0.6, 3.4, 'light_red', C_PORT, seg=16, index=9); place(g3, *LIGHTHOUSE, LH_PLAT_Z + LH_H + 6.9)

    # -------------------------------------------------------------- cidade baixa na colina
    def houses(bm, roofs=False):
        r = random.Random(5)
        for k in range(900):
            x = r.uniform(-1100, 1100); y = r.uniform(-1150, -215)
            if -120 < x < 230 and y > -260: continue
            z = float(land_z(x, y)); rz = r.choice((0, math.pi / 2)) + r.uniform(-0.1, 0.1)
            sx, sy, sh = r.uniform(8, 16), r.uniform(8, 14), r.uniform(6, 12)
            if roofs: prism_roof_into(bm, (x, y, z + sh), sx + 1.0, sy + 1.0, r.uniform(2.5, 4.0), rz)
            else: box_into(bm, (x, y, z + sh / 2 - 1), (sx, sy, sh + 2), rz)
    joined('TOWN_walls', 'wall_white', C_PORT, houses, index=10)
    joined('TOWN_roofs', 'roof', C_PORT, lambda bm: houses(bm, True), index=10)

    # -------------------------------------------------------------- fundo do mar e âncora gigante
    def seabed(bm):
        n = 90; xs = np.linspace(-900, 900, n); ys = np.linspace(QUAY_Y - 10, 1300, n)
        vv = [[bm.verts.new((x, y, float(seabed_z(x, y)))) for x in xs] for y in ys]
        for j in range(n - 1):
            for i in range(n - 1): bm.faces.new((vv[j][i], vv[j][i + 1], vv[j + 1][i + 1], vv[j + 1][i]))
    joined('SEABED', 'seabed', C_SEABED, seabed, index=11)
    def anchor(bm):
        A = Vector(ANCHOR)
        box_into(bm, A + Vector((0, 0, 3)), (3.2, 3.2, 26))                       # haste deitada inclinada
        for s in (-1, 1):
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(A + Vector((s * 8, 0, -7))) @ Matrix.Rotation(s * 0.9, 4, 'Y') @ Matrix.Diagonal((3, 3, 16, 1)))
            bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=4.0, radius2=0.2, depth=7, matrix=Matrix.Translation(A + Vector((s * 14, 0, -5))) @ Matrix.Rotation(s * 0.5, 4, 'Y'))
        box_into(bm, A + Vector((0, 0, -9.5)), (12, 3.6, 3.6))
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(A + Vector((0, 0, 14))) @ Matrix.Diagonal((18, 3.0, 3.0, 1)))  # cepo
    an = joined('ANCHOR', 'iron', C_SEABED, anchor, index=12)
    # manilha e pino (o pino é o que se rompe)
    sh = joined('SHACKLE', 'iron', C_SEABED, lambda bm: bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector(SHACKLE)) @ Matrix.Diagonal((7.0, 2.4, 6.0, 1))), index=12)
    pin = joined('SHACKLE_PIN', 'metal', C_SEABED, lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=1.0, radius2=1.0, depth=10,
                 matrix=Matrix.Translation(Vector(SHACKLE) + Vector((0, 0, -1.5))) @ Matrix.Rotation(math.pi / 2, 4, 'Y')), index=12)
    for k, m in enumerate(('coral_a', 'coral_b', 'coral_c')):
        def corals(bm, k=k):
            r = random.Random(30 + k)
            for i in range(22):
                a = r.uniform(0, 6.28); d = r.uniform(4, 22)
                c = Vector(ANCHOR) + Vector((math.cos(a) * d, math.sin(a) * d * 0.5, r.uniform(-9, 6)))
                bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r.uniform(1.2, 3.0), matrix=Matrix.Translation(c))
        joined(f'CORAL{k}', m, C_SEABED, corals, index=12)

    # -------------------------------------------------------------- cidade flutuante (malhas em coordenadas locais da ilha)
    # origem local = centro da ilha no plano, z absoluto
    def island(bm):
        r = random.Random(9)
        # rocha: cone invertido irregular do topo (470) até a ponta (~335)
        rings = [(CITY_TOP, CITY_R), (CITY_TOP - 18, CITY_R * 0.97), (CITY_TOP - 50, CITY_R * 0.82), (CITY_TOP - 85, CITY_R * 0.58),
                 (CITY_TOP - 115, CITY_R * 0.32), (CITY_TOP - 132, CITY_R * 0.12), (COLLAR_Z + 16, 4.0)]
        seg = 40; vs = []
        for z, rr in rings:
            row = []
            for i in range(seg):
                a = i / seg * math.tau; j = 1 + 0.08 * math.sin(a * 5 + z) + 0.05 * math.sin(a * 11)
                row.append(bm.verts.new((math.cos(a) * rr * j, math.sin(a) * rr * j, z + r.uniform(-3, 3) * (rr > 10))))
            vs.append(row)
        for a, b in zip(vs[:-1], vs[1:]):
            for i in range(seg): bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]))
        bm.faces.new(vs[0][::-1]); bm.faces.new(vs[-1])
    rock = joined('CITY_rock', 'rock', C_CITY, island, index=13)
    def topsoil(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=40, radius1=CITY_R * 0.99, radius2=CITY_R * 0.93, depth=8, matrix=Matrix.Translation((0, 0, CITY_TOP + 4)))
    soil = joined('CITY_grass', 'grass', C_CITY, topsoil, index=13)
    def citywalls(bm, roofs=False):
        r = random.Random(3)
        for k in range(260):
            a = r.uniform(0, 6.28); d = math.sqrt(r.uniform(0.02, 1)) * CITY_R * 0.8
            x, y = math.cos(a) * d, math.sin(a) * d
            if math.hypot(x - 20, y + 10) < 26: continue
            sx, sy, sh = r.uniform(7, 13), r.uniform(7, 12), r.uniform(6, 14) + 10 * (d < 60)
            rz = a + r.uniform(-0.2, 0.2)
            if roofs: prism_roof_into(bm, (x, y, CITY_TOP + 8 + sh), sx + 1, sy + 1, r.uniform(2.5, 4), rz)
            else: box_into(bm, (x, y, CITY_TOP + 8 + sh / 2), (sx, sy, sh), rz)
    joined('CITY_walls', 'wall_white', C_CITY, citywalls, index=14)
    joined('CITY_roofs', 'roof', C_CITY, lambda bm: citywalls(bm, True), index=14)
    # torre do sino
    def bell(bm):
        box_into(bm, (20, -10, CITY_TOP + 8 + 22), (12, 12, 44))
        box_into(bm, (20, -10, CITY_TOP + 8 + 46), (14, 14, 4))
        for dx, dy in ((-4.5, -4.5), (4.5, -4.5), (-4.5, 4.5), (4.5, 4.5)): box_into(bm, (20 + dx, -10 + dy, CITY_TOP + 8 + 52), (2.4, 2.4, 9))
        box_into(bm, (20, -10, CITY_TOP + 8 + 57.5), (14, 14, 2))
    joined('CITY_bell', 'wall_white', C_CITY, bell, index=15)
    def bellroof(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=10.5, radius2=0.3, depth=14, matrix=Matrix.Translation((20, -10, CITY_TOP + 8 + 65.5)) @ Matrix.Rotation(math.pi / 4, 4, 'Z'))
    joined('CITY_bellroof', 'roof', C_CITY, bellroof, index=15)
    # moinhos de vento (pás giram)
    for k, a in enumerate((0.4, 1.9, 3.3, 4.6, 5.6)):
        d = CITY_R * 0.78; x, y = math.cos(a) * d, math.sin(a) * d
        t = cyl(f'CITY_mill{k}', 6, 4.2, 22, 'windmill', C_CITY, seg=16, index=16); place(t, x, y, CITY_TOP + 8 + 11)
        rf = cyl(f'CITY_millroof{k}', 4.8, 0.4, 6, 'roof', C_CITY, seg=16, index=16); place(rf, x, y, CITY_TOP + 8 + 25)
        def blades(bm):
            for i in range(4):
                bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Rotation(i * math.pi / 2, 4, 'Y') @ Matrix.Translation((0, 0, 9)) @ Matrix.Diagonal((3.2, 0.4, 16, 1)))
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((2, 2, 2, 1)))
        bl = joined(f'CITY_blades{k}', 'wood', C_CITY, blades, index=16)
        bl['mill'] = (x, y, a)
    # cristais de levitação sob a rocha
    def crystals(bm):
        r = random.Random(4)
        for i in range(34):
            a = r.uniform(0, 6.28); z = r.uniform(COLLAR_Z + 40, CITY_TOP - 40)
            rr = CITY_R * max(0.08, (z - COLLAR_Z) / (CITY_TOP - COLLAR_Z)) * 0.9
            c = Vector((math.cos(a) * rr, math.sin(a) * rr, z))
            d = Vector((math.cos(a) * 0.6, math.sin(a) * 0.6, -1)).normalized()
            rot = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
            bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=r.uniform(3, 7), radius2=0.0, depth=r.uniform(14, 34), matrix=Matrix.Translation(c) @ rot @ Matrix.Translation((0, 0, 8)))
    joined('CITY_crystals', 'crystal', C_CITY, crystals, index=17)
    # colar de ferro na ponta de baixo
    co = cyl('CITY_collar', 9.5, 7.0, 16, 'iron', C_CITY, seg=24, index=18); place(co, 0, 0, COLLAR_Z + 8)
    for k in range(8):
        a = k / 8 * math.tau
        rv = rbox(f'CITY_rivet{k}', (2, 2, 2), 0.6, 'metal', C_CITY, index=18); place(rv, math.cos(a) * 9.2, math.sin(a) * 9.2, COLLAR_Z + 12)
    # bordas de onde caem as cachoeiras (pequenos canais)
    # nuvens: cúmulos brancos em anel e a massa de tempestade (índigo) que vem do oeste
    def cumulus(bm, cx, cy, cz, s, rr):
        for i in range(int(14 + s / 60)):
            a = rr.uniform(0, 6.28); d = rr.uniform(0, s * 0.55)
            c = (cx + math.cos(a) * d, cy + math.sin(a) * d * 0.6, cz + rr.uniform(0, s * 0.35) * (1 - d / (s * 0.6)))
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=rr.uniform(0.25, 0.42) * s, matrix=Matrix.Translation(c) @ Matrix.Diagonal((1, 1, 0.72, 1)))
    def clouds(bm):
        r = random.Random(21)
        for k in range(16):
            a = -1.0 + k / 16 * math.tau * 0.8; d = r.uniform(2800, 5200)
            if 1.2 < a % math.tau < 2.5: d *= 1.3
            cumulus(bm, math.cos(a) * d, math.sin(a) * d + 400, r.uniform(500, 900), r.uniform(380, 700), r)
    joined('CLOUDS', 'cloud', C_SKY, clouds, index=19)
    def stormdeck(bm):
        r = random.Random(23)
        for k in range(46):
            x = r.uniform(-2400, 600); y = r.uniform(-1600, 2400)
            cumulus(bm, x, y, r.uniform(950, 1300), r.uniform(500, 900), r)
    st = joined('STORM', 'storm', C_SKY, stormdeck, index=21)
    # tromba d'água: funil torcido
    def spout(bm):
        rings = 40; seg = 18; vs = []
        for i in range(rings):
            u = i / (rings - 1); z = u * 1050
            rr = 14 + 60 * u ** 2.2 + 30 * (u < 0.05)
            row = [bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, z)) for a in [j / seg * math.tau + u * 3 for j in range(seg)]]
            vs.append(row)
        for a, b in zip(vs[:-1], vs[1:]):
            for j in range(seg): bm.faces.new((a[j], a[(j + 1) % seg], b[(j + 1) % seg], b[j]))
    joined('SPOUT', 'spout', C_SKY, spout, index=22)
