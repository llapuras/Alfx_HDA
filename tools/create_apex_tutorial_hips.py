# -*- coding: utf-8 -*-
import os
import hou


ROOT = r"G:\HDA_JD"
OUT_DIR = os.path.join(ROOT, "hips", "apex")


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def clear_scene():
    hou.hipFile.clear(suppress_save_prompt=True)
    obj = hou.node("/obj")
    for child in obj.children():
        child.destroy()
    return obj


def make_geo(obj, name):
    geo = obj.createNode("geo", name)
    for child in geo.children():
        child.destroy()
    return geo


def make_node(parent, type_names, name, pos=(0, 0), comment=None):
    if isinstance(type_names, str):
        type_names = [type_names]
    last_error = None
    for type_name in type_names:
        try:
            node = parent.createNode(type_name, node_name=name)
            node.setPosition(hou.Vector2(pos[0], pos[1]))
            if comment:
                node.setComment(comment)
                node.setGenericFlag(hou.nodeFlag.DisplayComment, True)
            return node
        except Exception as exc:
            last_error = exc
    raise RuntimeError("Could not create node %s: %s" % (name, last_error))


def maybe_node(parent, type_names, name, pos=(0, 0), comment=None):
    try:
        return make_node(parent, type_names, name, pos, comment)
    except Exception:
        null = make_node(parent, "null", name, pos, comment or "This Houdini build could not create the requested node.")
        null.setColor(hou.Color((0.6, 0.25, 0.2)))
        return null


def sticky(parent, text, pos=(-4, 2), size=(5, 3), color=(0.95, 0.83, 0.45)):
    note = parent.createStickyNote()
    note.setText(text)
    note.setPosition(hou.Vector2(pos[0], pos[1]))
    note.setSize(hou.Vector2(size[0], size[1]))
    note.setColor(hou.Color(color))
    return note


def set_parm(node, parm_name, value):
    parm = node.parm(parm_name)
    if parm is not None:
        try:
            parm.set(value)
        except Exception:
            pass


def layout(parent):
    try:
        parent.layoutChildren()
    except Exception:
        pass


def save(name):
    ensure_dir(OUT_DIR)
    path = os.path.join(OUT_DIR, name)
    hou.hipFile.save(path)
    return path


def create_ex01():
    obj = clear_scene()
    geo = make_geo(obj, "EX01_minimal_apex_graph")

    graph = maybe_node(
        geo,
        "apex::graph",
        "apex_graph__edit_me",
        (0, 0),
        "Open Edit Graph. The output of this SOP is APEX graph geometry.",
    )
    layout_graph = maybe_node(
        geo,
        "apex::layoutgraph",
        "layout_graph_for_readability",
        (2, 0),
        "Optional: lays out graph nodes for easier reading.",
    )
    out = make_node(geo, "null", "OUT_APEX_GRAPH_GEOMETRY", (4, 0), "This Null receives graph geometry, not a mesh.")
    layout_graph.setInput(0, graph)
    out.setInput(0, layout_graph)
    out.setDisplayFlag(True)
    out.setRenderFlag(True)

    sticky(
        geo,
        "例子 1：最小 APEX Graph\n\n目标：理解 APEX Graph 在 SOP 里也是 geometry。\n\n操作：\n1. 选中 apex_graph__edit_me。\n2. 点击参数面板里的 Edit Graph。\n3. 回到 Geometry Spreadsheet，观察它输出的不是模型，而是图数据。\n\n记住：APEX Graph SOP 负责创建/保存逻辑图；执行图是另一步。",
        (-4, 2),
        (6.8, 3.2),
    )
    geo.layoutChildren()
    return save("01_minimal_apex_graph.hip")


def create_ex02():
    obj = clear_scene()
    geo = make_geo(obj, "EX02_numbers_add")

    graph = maybe_node(geo, "apex::graph", "apex_graph__a_plus_b", (0, 0), "Build a graph with float inputs a/b and float output result.")
    invoke = maybe_node(geo, "apex::invokegraph", "invoke_graph__test_values", (2, 0), "Use this to execute the graph after you add ports inside APEX Network View.")
    out = make_node(geo, "null", "OUT_RESULT", (4, 0), "Inspect details/dictionaries after invoking.")
    invoke.setInput(0, graph)
    out.setInput(0, invoke)
    out.setDisplayFlag(True)
    out.setRenderFlag(True)

    sticky(
        geo,
        "例子 2：两个数相加\n\n在 APEX Network View 里搭这个结构：\n\nfloat input a\nfloat input b\n        ↓\n      add\n        ↓\nfloat output result\n\n然后用 invoke_graph__test_values 测试：\na = 2, b = 3, result = 5\n\n核心概念：APEX Graph 定义怎么算；APEX Invoke Graph 真的执行一次。",
        (-4.5, 2.2),
        (7.4, 3.4),
    )
    geo.layoutChildren()
    return save("02_apex_add_two_numbers.hip")


def create_ex03():
    obj = clear_scene()
    geo = make_geo(obj, "EX03_geometry_offset")

    box = make_node(geo, "box", "source_box", (-2, 0), "Input geometry for the APEX graph.")
    xform = make_node(geo, "xform", "sop_reference_offset_y2", (0, -1.2), "Plain SOP reference: this shows the expected result.")
    set_parm(xform, "ty", 2)
    graph = maybe_node(geo, "apex::graph", "apex_graph__geo_offset", (0, 0.8), "Build graph inputs: geo geometry, offset vector. Output: out_geo.")
    invoke = maybe_node(geo, "apex::invokegraph", "invoke_graph__offset_box", (2.2, 0.8), "Bind source_box geometry to input geo; set offset to (0, 2, 0).")
    out = make_node(geo, "null", "OUT_OFFSET_GEO", (4.4, 0.8), "Display the invoked geometry output.")
    xform.setInput(0, box)
    invoke.setInput(0, graph)
    invoke.setInput(1, box)
    out.setInput(0, invoke)
    out.setDisplayFlag(True)
    out.setRenderFlag(True)

    sticky(
        geo,
        "例子 3：APEX 处理 geometry\n\n目标：知道 APEX 不只服务角色绑定，也能把 geometry 当输入/输出。\n\nAPEX 图的函数感：\nout_geo = MyGraph(geo, offset)\n\n练习：在 apex_graph__geo_offset 里创建 geometry 输入 geo、vector 输入 offset，用 transform 类节点把 box 平移到 Y=2。",
        (-5, 2.7),
        (7.8, 3.3),
    )
    geo.layoutChildren()
    return save("03_apex_geometry_offset.hip")


def create_ex04():
    obj = clear_scene()
    geo = make_geo(obj, "EX04_three_joint_tube_rig")

    tube = make_node(geo, "tube", "source_tube_finger", (-4, 0), "Simple tube standing in for a finger/tail/mechanical arm.")
    set_parm(tube, "type", 1)
    set_parm(tube, "rad1", 0.15)
    set_parm(tube, "rad2", 0.15)
    set_parm(tube, "height", 3.0)
    set_parm(tube, "orient", 1)

    line = make_node(geo, "line", "joint_guide_line", (-4, -1.5), "Visual guide for three joints: root, mid, tip.")
    set_parm(line, "points", 3)
    set_parm(line, "dist", 1.5)

    pack = maybe_node(geo, "apex::packcharacter", "apex_pack_character", (-1, 0), "Pack shape/skeleton/capture data into an APEX character folder.")
    fk = maybe_node(geo, ["apex::autorigcomponent::3.0", "apex::autorigcomponent"], "add_fk_component", (1.4, 0), "Add an FK rig component.")
    deform = maybe_node(geo, ["apex::autorigcomponent::3.0", "apex::autorigcomponent"], "add_bone_deform_component", (3.8, 0), "Add a bone deform component.")
    out = make_node(geo, "null", "OUT_THREE_JOINT_RIG", (6, 0), "Enter Animate State on the APEX node chain after the rig is configured.")

    try:
        pack.setInput(0, tube)
        pack.setInput(1, line)
    except Exception:
        pass
    fk.setInput(0, pack)
    deform.setInput(0, fk)
    out.setInput(0, deform)
    out.setDisplayFlag(True)
    out.setRenderFlag(True)

    sticky(
        geo,
        "例子 4：三关节管子绑定\n\n这里放好了管子、三关节 guide，以及 APEX Pack Character / AutoRig Component 节点骨架。\n\n你要在 Houdini 里补完：\n1. 用 KineFX 创建 root/mid/tip 三个 joint。\n2. 给 tube 做 capture 权重。\n3. Pack 成 character folder。\n4. 添加 FK 和 Bone Deform 组件。\n5. 进入 Animate State 测试控制器。\n\n重点：角色数据 + rig components -> APEX rig graph -> 可动画角色。",
        (-5.3, 2.8),
        (8.5, 3.8),
    )
    geo.layoutChildren()
    return save("04_three_joint_tube_apex_rig.hip")


def create_ex05():
    obj = clear_scene()
    geo = make_geo(obj, "EX05_inspect_apex_rig")

    pack = maybe_node(geo, "apex::packcharacter", "example_character_folder", (-2, 0), "Start from an existing APEX character or the result from example 4.")
    builder = maybe_node(geo, "apex::autorigbuilder", "apex_autorig_builder", (0.4, 0), "Generate or edit rig components interactively.")
    graph = maybe_node(geo, "apex::graph", "open_rig_graph_here", (2.8, 0), "Open Edit Graph and inspect inputs, outputs, controls, skeleton, deform.")
    layout_graph = maybe_node(geo, "apex::layoutgraph", "layout_graph", (5.2, 0), "Clean up graph layout for reading.")
    out = make_node(geo, "null", "OUT_INSPECTED_RIG", (7.2, 0), "Use this as the final inspection point.")

    builder.setInput(0, pack)
    graph.setInput(0, builder)
    layout_graph.setInput(0, graph)
    out.setInput(0, layout_graph)
    out.setDisplayFlag(True)
    out.setRenderFlag(True)

    sticky(
        geo,
        "例子 5：拆看 APEX rig\n\n不要试图一次看懂整张大图。按数据流追：\n\n1. inputs / outputs\n2. control 参数\n3. joint transform\n4. skeleton update\n5. bone deform\n\n练习：找一个 FK 控制器，追踪它如何改变 joint transform，最后如何影响模型变形。",
        (-4.8, 2.5),
        (7.6, 3.5),
    )

    sticky(
        geo,
        "调试提示\n\nHoudini 22 有更明显的 APEX graph debugger；Houdini 21 也可以通过 Network View、Geometry Spreadsheet、节点属性和端口类型来观察。\n\n关键词：ports、tags、properties、path pattern、character folder。",
        (2.2, 2.5),
        (6.2, 2.8),
        (0.68, 0.86, 0.95),
    )
    geo.layoutChildren()
    return save("05_inspect_apex_rig_graph.hip")


def main():
    ensure_dir(OUT_DIR)
    paths = [
        create_ex01(),
        create_ex02(),
        create_ex03(),
        create_ex04(),
        create_ex05(),
    ]
    print("\n".join(paths))


if __name__ == "__main__":
    main()
