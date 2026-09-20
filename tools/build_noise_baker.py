"""Rebuild Alfx_Noise_Baker as one SOP HDA: Copernicus fractalnoise + bake."""
from __future__ import print_function

import os
import shutil
import time

import hou

HDA_PATH = r"G:\VFX_JD\Assets\HDA\Alfx_Noise_Baker.hda"
HDA_COPY = r"G:\HDA_JD\hda\Alfx_Noise_Baker.hda"
BACKUP_DIR = r"G:\VFX_JD\Assets\HDA\backup"
TYPE_NAME = "Alfx_Noise_Baker"


def backup_existing():
    if not os.path.isfile(HDA_PATH):
        return None
    os.makedirs(BACKUP_DIR, exist_ok=True)
    existing = [
        n for n in os.listdir(BACKUP_DIR)
        if n.startswith("Alfx_Noise_Baker_bak") and n.endswith(".hda")
    ]
    idx = 1
    nums = []
    for n in existing:
        body = n[len("Alfx_Noise_Baker_bak"):-len(".hda")]
        if body.isdigit():
            nums.append(int(body))
    if nums:
        idx = max(nums) + 1
    dest = os.path.join(BACKUP_DIR, "Alfx_Noise_Baker_bak{}.hda".format(idx))
    shutil.copy2(HDA_PATH, dest)
    print("backup", dest)
    return dest


def destroy_old_definition():
    if not os.path.isfile(HDA_PATH):
        return
    try:
        hou.hda.installFile(HDA_PATH)
    except Exception as e:
        print("install skip", e)
        return
    try:
        defs = list(hou.hda.definitionsInFile(HDA_PATH))
    except Exception as e:
        print("no definitions", e)
        return
    for d in defs:
        print("destroy definition", d.nodeTypeName())
        d.destroy()


def make_parm_group():
    noise_menu = hou.MenuParmTemplate(
        "noisetype",
        "Noise Type",
        menu_items=("torus", "perlin", "worleyA", "worleyB", "white", "alligator"),
        menu_labels=(
            "Torus",
            "Perlin",
            "Worley F1",
            "Worley F2-F1",
            "White",
            "Alligator",
        ),
        default_value=1,
    )

    amp = hou.FloatParmTemplate(
        "amp", "Amplitude", 1,
        default_value=(0.5,), min=0.0, max=2.0, min_is_strict=True,
    )
    amp.setMaxIsStrict(False)

    elementsize = hou.FloatParmTemplate(
        "elementsize", "Element Size", 1,
        default_value=(0.1,), min=0.001, max=1.0, min_is_strict=True,
    )
    elementsize.setMaxIsStrict(False)

    off = hou.FloatParmTemplate(
        "offset", "Offset", 2,
        default_value=(0.15, 0.37),
        min=-10.0, max=10.0,
        naming_scheme=hou.parmNamingScheme.XYZW,
    )

    jitter = hou.FloatParmTemplate(
        "jitter", "Jitter", 1,
        default_value=(1.0,), min=0.0, max=1.0,
    )
    jitter.setConditional(
        hou.parmCondType.HideWhen,
        "{ noisetype != 2 noisetype != 3 }",
    )

    metric = hou.MenuParmTemplate(
        "metric",
        "Distance Metric",
        menu_items=("euclidean", "manhattan", "chebyshev"),
        menu_labels=("Euclidean", "Manhattan", "Chebyshev"),
        default_value=0,
    )
    metric.setConditional(
        hou.parmCondType.HideWhen,
        "{ noisetype != 2 noisetype != 3 }",
    )

    type_folder = hou.FolderParmTemplate(
        "folder_type", "Type",
        (noise_menu, amp, elementsize, off, jitter, metric),
        folder_type=hou.folderType.Simple,
    )

    octaves = hou.FloatParmTemplate(
        "oct", "Octaves", 1,
        default_value=(4.0,), min=1.0, max=16.0, min_is_strict=True,
    )
    lac = hou.FloatParmTemplate(
        "lac", "Lacunarity", 1,
        default_value=(2.0,), min=1.0, max=4.0,
    )
    rough = hou.FloatParmTemplate(
        "rough", "Roughness", 1,
        default_value=(0.5,), min=0.0, max=1.0,
    )
    center = hou.FloatParmTemplate(
        "center", "Center", 1,
        default_value=(0.5,), min=0.0, max=1.0,
    )
    fold = hou.ToggleParmTemplate("fold", "Ridged (Fold)", default_value=False)
    complement = hou.ToggleParmTemplate("complement", "Complement", default_value=False)

    fractal_folder = hou.FolderParmTemplate(
        "folder_fractal", "Fractal",
        (octaves, lac, rough, center, fold, complement),
        folder_type=hou.folderType.Simple,
    )

    tiled = hou.ToggleParmTemplate("tiled", "Tiling", default_value=True)
    tilesize = hou.FloatParmTemplate(
        "tilesize", "Tile Size", 1,
        default_value=(2.0,), min=0.01, max=16.0,
    )
    tilesize.setConditional(hou.parmCondType.HideWhen, "{ tiled == 0 }")

    clamp01 = hou.ToggleParmTemplate("clamp01", "Clamp 0-1", default_value=True)

    tiling_folder = hou.FolderParmTemplate(
        "folder_tiling", "Tiling",
        (tiled, tilesize, clamp01),
        folder_type=hou.folderType.Simple,
    )

    res = hou.IntParmTemplate(
        "res", "Resolution", 2,
        default_value=(1024, 1024),
        min=16, max=8192, min_is_strict=True,
        naming_scheme=hou.parmNamingScheme.Base1,
    )

    copoutput = hou.StringParmTemplate(
        "copoutput",
        "Output File",
        1,
        default_value=("G:/HDA_JD/Assets/comp/test_noise.png",),
        string_type=hou.stringParmType.FileReference,
        file_type=hou.fileType.Image,
    )

    execute = hou.ButtonParmTemplate("execute", "Render to Disk")
    execute.setScriptCallback(
        "kwargs['node'].node('copnet/rop_image1').parm('execute').pressButton()"
    )
    execute.setScriptCallbackLanguage(hou.scriptLanguage.Python)

    output_folder = hou.FolderParmTemplate(
        "folder_output", "Output",
        (res, copoutput, execute),
        folder_type=hou.folderType.Simple,
    )

    ptg = hou.ParmTemplateGroup()
    ptg.append(type_folder)
    ptg.append(fractal_folder)
    ptg.append(tiling_folder)
    ptg.append(output_folder)
    return ptg


def build_network(subnet):
    cop = subnet.createNode("copnet", "copnet")
    cop.parm("setres").set(1)
    cop.parm("res1").setExpression('ch("../res1")')
    cop.parm("res2").setExpression('ch("../res2")')

    noise = cop.createNode("fractalnoise", "fractalnoise1")
    noise.parm("noisetype").setExpression('ch("../../noisetype")')
    noise.parm("amp").setExpression('ch("../../amp")')
    noise.parm("elementsize").setExpression('ch("../../elementsize")')
    noise.parm("offx").setExpression('ch("../../offsetx")')
    noise.parm("offy").setExpression('ch("../../offsety")')
    noise.parm("jitter").setExpression('ch("../../jitter")')
    noise.parm("metric").setExpression('ch("../../metric")')
    noise.parm("oct").setExpression('ch("../../oct")')
    noise.parm("lac").setExpression('ch("../../lac")')
    noise.parm("rough").setExpression('ch("../../rough")')
    noise.parm("center").setExpression('ch("../../center")')
    if noise.parm("folder4") is not None:
        noise.parm("folder4").set(1)
    noise.parm("post_dofold").setExpression('ch("../../fold")')
    noise.parm("post_docomplement").setExpression('ch("../../complement")')
    noise.parm("dotiled").setExpression('ch("../../tiled")')
    noise.parm("tilesizex").setExpression('ch("../../tilesize")')
    noise.parm("tilesizey").setExpression('ch("../../tilesize")')
    noise.parm("post_doclampmin").setExpression('ch("../../clamp01")')
    noise.parm("post_doclampmax").setExpression('ch("../../clamp01")')
    noise.parm("post_minimum").set(0)
    noise.parm("post_maximum").set(1)

    out_img = cop.createNode("null", "OUT_NOISE")
    out_img.setInput(0, noise)
    out_img.setDisplayFlag(True)

    rop = cop.createNode("rop_image", "rop_image1")
    rop.parm("coppath").set("../OUT_NOISE")
    rop.parm("copoutput").setExpression('chs("../../copoutput")')

    cop.layoutChildren()

    output = subnet.createNode("output", "output0")
    output.setInput(0, cop)
    cop.setDisplayFlag(True)
    cop.setRenderFlag(True)
    subnet.layoutChildren()
    return cop, noise, rop


def verify(node):
    geo = node.geometry()
    if geo is None:
        raise RuntimeError("HDA cooked no geometry")
    prims = geo.prims()
    if not prims:
        raise RuntimeError("HDA has no prims")
    prim = prims[0]
    if prim.type() != hou.primType.Volume:
        raise RuntimeError("expected Volume prim, got {}".format(prim.type()))
    res = prim.resolution()
    print("verify volume res", res)
    if res[2] != 1:
        raise RuntimeError("expected 2D volume, z={}".format(res[2]))
    voxel = prim.voxel((res[0] // 2, res[1] // 2, 0))
    print("center voxel", voxel)

    node.parm("noisetype").set(2)
    node.parm("jitter").set(0.4)
    geo2 = node.geometry()
    v2 = geo2.prims()[0].voxel((res[0] // 2, res[1] // 2, 0))
    print("worley F1 center voxel", v2)


def main():
    hou.hipFile.clear(suppress_save_prompt=True)
    backup_existing()
    destroy_old_definition()

    obj = hou.node("/obj")
    geo = obj.createNode("geo", "build")
    for c in geo.children():
        c.destroy()
    subnet = geo.createNode("subnet", TYPE_NAME)
    subnet.setParmTemplateGroup(make_parm_group())
    build_network(subnet)

    if os.path.isfile(HDA_PATH):
        try:
            os.remove(HDA_PATH)
        except OSError as e:
            print("could not remove old hda, will overwrite:", e)

    hda_node = subnet.createDigitalAsset(
        name=TYPE_NAME,
        hda_file_name=HDA_PATH,
        description="Tileable 2D noise texture baker",
        min_num_inputs=0,
        max_num_inputs=0,
        ignore_external_references=True,
        change_node_type=True,
        create_backup=False,
    )
    ptg = make_parm_group()
    hda_node.setParmTemplateGroup(ptg)
    definition = hda_node.type().definition()
    definition.setParmTemplateGroup(ptg)
    definition.setVersion("2.0")
    definition.setComment("Copernicus fractalnoise baker for Small Tool")
    definition.updateFromNode(hda_node)

    verify(hda_node)

    definition.setParmTemplateGroup(hda_node.parmTemplateGroup())
    definition.save(HDA_PATH, hda_node)
    os.makedirs(os.path.dirname(HDA_COPY), exist_ok=True)
    shutil.copy2(HDA_PATH, HDA_COPY)
    print("saved", HDA_PATH)
    print("copied", HDA_COPY)
    print("parms", [p.name() for p in hda_node.parms()])


if __name__ == "__main__":
    main()
