"""Renderiza quadros em Eevee: blender -b harbor.blend -P render.py -- states.pkl outdir f0 f1 [step] [w h]
Escreve EXR multicamada com as passadas que a segunda etapa (tinta e pintura) usa."""
import bpy, sys, os, pickle, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apply

argv = sys.argv[sys.argv.index('--') + 1:]
states_path, outdir, f0, f1 = argv[0], argv[1], int(argv[2]), int(argv[3])
step = int(argv[4]) if len(argv) > 4 else 1
os.makedirs(outdir, exist_ok=True)
states = pickle.load(open(states_path, 'rb'))
sc = bpy.context.scene
if len(argv) > 6: sc.render.resolution_x, sc.render.resolution_y = int(argv[5]), int(argv[6])
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.0
bpy.data.lights['SUN'].energy = 3.14159
for f in range(f0, f1, step):
    out = os.path.join(outdir, f'f{f:04d}.exr')
    if os.path.exists(out): continue
    t = time.time()
    apply.apply_state(states[f])
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print(f'FRAME {f} {time.time() - t:.1f}s', flush=True)
