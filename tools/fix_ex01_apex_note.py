# -*- coding: utf-8 -*-
import hou


path = r"G:\HDA_JD\hips\apex\01_minimal_apex_graph.hip"
hou.hipFile.load(path, suppress_save_prompt=True)

geo = hou.node("/obj/EX01_minimal_apex_graph")
if geo is not None:
    node = geo.node("apex_graph__edit_me")
    if node is not None:
        node.setComment("Select this SOP node, then press the parameter button labeled 'Edit Graph'.")
        node.setGenericFlag(hou.nodeFlag.DisplayComment, True)

    for note in geo.stickyNotes():
        note.setText(
            "例子 1：最小 APEX Graph\n\n"
            "注意：apex_graph__edit_me 是节点名字，不是参数按钮名字。\n\n"
            "正确操作：\n"
            "1. 双击进入 /obj/EX01_minimal_apex_graph。\n"
            "2. 选中 SOP 节点 apex_graph__edit_me。\n"
            "3. 看右侧参数面板，找到按钮 Edit Graph。\n"
            "4. 点击 Edit Graph 打开 APEX Network View。\n\n"
            "如果你选中的是外层 Geometry 对象，或后面的 OUT_APEX_GRAPH_GEOMETRY Null，参数面板里不会有 Edit Graph。"
        )

hou.hipFile.save(path)
