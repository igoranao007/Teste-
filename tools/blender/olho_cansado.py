"""Olho cansado sem peça extra: as faces do olho acima de uma altura viram pelo (pálpebra na própria malha).
Uso: blender -b metalis.blend --python olho_cansado.py -- altura saida.blend"""
import bpy, sys
Z, OUT = sys.argv[sys.argv.index('--') + 1:]; Z = float(Z)
o = bpy.data.objects['corpo']; me = o.data
nomes = [m.name for m in me.materials]; pelo = nomes.index('pelo_sujo')
n = 0
for p in me.polygons:
    if nomes[p.material_index] in ('olho', 'iris', 'preto') and p.center.z > Z and p.center.z > 0.90:
        p.material_index = pelo; n += 1
print('PALPEBRA faces', n)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
