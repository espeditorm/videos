import bpy, sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apply
a = sys.argv[sys.argv.index('--') + 1:]
states = pickle.load(open(a[0], 'rb')); out = a[1]; os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; sc.render.resolution_x, sc.render.resolution_y = int(a[3]), int(a[4])
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.0
bpy.data.lights['SUN'].energy = 3.14159
for f in map(int, a[2].split(',')):
    apply.apply_state(states[f]); sc.render.filepath = os.path.join(out, f'f{f:04d}.exr')
    bpy.ops.render.render(write_still=True)
