# -*- coding: utf-8 -*-
import hou


PATH = r"G:\HDA_JD\hips\apex\01_minimal_apex_graph.hip"


PY_CODE = r'''import hou
import apex

geo = hou.pwd().geometry()
geo.clear()

g = apex.Graph()

# APEX graphs use special __parms__ and __output__ nodes for graph inputs/outputs.
parms = g.addNode("parms", "__parms__")
output = g.addNode("output", "__output__")

value_10 = g.addNode("value_10", "Value<Float>")
add = g.addNode("add_a_plus_10", "Add<Float>")

g.setNodeParm(value_10, "parm", 10.0)

a_in = g.addGraphInput(parms, "a")
result_out = g.addGraphOutput(output, "result")

g.addWire(a_in, g.getPort(add, "a"))
g.addWire(g.getPort(value_10, "value"), g.getPort(add, "b"))
g.addWire(g.getPort(add, "result"), result_out)

g.setNodePosition(parms, hou.Vector3(-4, 0, 0))
g.setNodePosition(value_10, hou.Vector3(-4, -1.2, 0))
g.setNodePosition(add, hou.Vector3(-1, -0.6, 0))
g.setNodePosition(output, hou.Vector3(2, -0.6, 0))

g.saveToGeometry(geo)
'''


def clear_children(node):
    for child in node.children():
        child.destroy()
    for note in node.stickyNotes():
        note.destroy()


def node(parent, type_name, name, pos):
    n = parent.createNode(type_name, node_name=name)
    n.setPosition(hou.Vector2(pos[0], pos[1]))
    return n


def sticky(parent, text, pos, size, color):
    note = parent.createStickyNote()
    note.setText(text)
    note.setPosition(hou.Vector2(pos[0], pos[1]))
    note.setSize(hou.Vector2(size[0], size[1]))
    note.setColor(hou.Color(color))
    return note


hou.hipFile.clear(suppress_save_prompt=True)
obj = hou.node("/obj")
for child in obj.children():
    child.destroy()

geo = obj.createNode("geo", "EX01_minimal_apex_graph")
clear_children(geo)

py = node(geo, "python", "MAKE_REAL_APEX_GRAPH__a_plus_10", (0, 0))
py.parm("python").set(PY_CODE)
py.setComment("This Python SOP writes real APEX graph geometry: 4 graph nodes and 3 wires.")
py.setGenericFlag(hou.nodeFlag.DisplayComment, True)

edit = node(geo, "apex::graph", "OPEN_THIS__apex_graph_editor", (2.7, 0))
edit.setInput(0, py)
edit.setComment("Select this node and press the parameter button 'Edit Graph'.")
edit.setGenericFlag(hou.nodeFlag.DisplayComment, True)

layout = node(geo, "apex::layoutgraph", "layout_graph_for_readability", (5.4, 0))
layout.setInput(0, edit)

out = node(geo, "null", "OUT_APEX_GRAPH_GEOMETRY", (8, 0))
out.setInput(0, layout)
out.setDisplayFlag(True)
out.setRenderFlag(True)
out.setComment("Display this, then open Geometry Spreadsheet.")
out.setGenericFlag(hou.nodeFlag.DisplayComment, True)

sticky(
    geo,
    "例子 1：这次不是空图了\n\n"
    "显示 OUT_APEX_GRAPH_GEOMETRY，然后打开 Geometry Spreadsheet：\n\n"
    "看 Points 页签：应该有 4 行。\n"
    "- parms：callback 是 __parms__，代表图输入\n"
    "- value_10：callback 是 Value<Float>，代表常量 10\n"
    "- add_a_plus_10：callback 是 Add<Float>，代表加法节点\n"
    "- output：callback 是 __output__，代表图输出\n\n"
    "看 Primitives 页签：应该有 3 条 primitive，它们就是三根 wire/连线。\n\n"
    "Detail 只是图的整体 metadata，不是这个例子的重点。",
    (-4.8, 2.4),
    (8.6, 4.5),
    (0.95, 0.83, 0.45),
)

sticky(
    geo,
    "打开图编辑器\n\n"
    "1. 选中 OPEN_THIS__apex_graph_editor。\n"
    "2. 参数面板点 Edit Graph。\n"
    "3. 你会看到 a -> Add<Float>，以及 Value<Float>(10) -> Add<Float>，最后输出 result。\n\n"
    "这才是“APEX Graph 在 SOP 里也是 geometry”的可见版本。",
    (3.1, 2.5),
    (7.6, 3.2),
    (0.68, 0.86, 0.95),
)

geo.layoutChildren()

# Cook once so obvious errors surface while the file is being created.
out.geometry()
hou.hipFile.save(PATH)
