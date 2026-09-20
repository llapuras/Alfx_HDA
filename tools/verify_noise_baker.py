import hou
import os

path = r"G:\VFX_JD\Assets\HDA\Alfx_Noise_Baker.hda"
print("size", os.path.getsize(path))
hou.hda.installFile(path)
parent = hou.node("/obj").createNode("geo", "t")
n = parent.createNode("Alfx_Noise_Baker", "baker")
names = [p.name() for p in n.parms()]
print("parms", names)
assert "noisetype" in names, names
assert "execute" in names
cb = n.parm("execute").parmTemplate().scriptCallback()
print("execute callback", cb)
assert "rop_image1" in cb

n.parm("res1").set(64)
n.parm("res2").set(64)

labels = ("Torus", "Perlin", "WorleyF1", "WorleyF2F1", "White", "Alligator")
for i, label in enumerate(labels):
    n.parm("noisetype").set(i)
    prim = n.geometry().prims()[0]
    res = prim.resolution()
    assert res == (64, 64, 1), res
    mid = prim.voxel((32, 32, 0))
    print(i, label, "mid", round(mid, 4))

n.parm("noisetype").set(1)
n.parm("fold").set(1)
print("ridged", round(n.geometry().prims()[0].voxel((32, 32, 0)), 4))
n.parm("fold").set(0)
n.parm("complement").set(1)
print("complement", round(n.geometry().prims()[0].voxel((32, 32, 0)), 4))
print("OK")
