"""Confirmed Houdini Python execution helpers."""

from __future__ import annotations

import datetime
import os
import traceback

try:
    import hou
except ImportError:
    hou = None


def make_hip_backup():
    """Save a timestamped backup next to the current hip file before mutation."""
    if hou is None:
        raise RuntimeError("hou module is not available")

    hip_path = hou.hipFile.path()
    if not hip_path or hip_path == "untitled.hip":
        raise RuntimeError("Save the hip file once before executing scene-changing code.")

    root, ext = os.path.splitext(hip_path)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = "%s.ai_panel_backup_%s%s" % (root, stamp, ext or ".hip")
    hou.hipFile.save(file_name=backup_path)
    hou.hipFile.save(file_name=hip_path)
    return backup_path


def run_hou_python(code):
    """Execute HOM/Python after the UI has obtained explicit confirmation."""
    if hou is None:
        return {"ok": False, "error": "hou module is not available", "backup_path": None}

    backup_path = None
    try:
        backup_path = make_hip_backup()
        namespace = {
            "__name__": "__houdini_ai_panel_exec__",
            "hou": hou,
        }
        exec(compile(code, "<houdini_ai_panel>", "exec"), namespace, namespace)
        return {"ok": True, "error": None, "backup_path": backup_path}
    except Exception:
        return {"ok": False, "error": traceback.format_exc(), "backup_path": backup_path}


def create_node(parent, node_type, name=None):
    """Create a node using HOM. Intended for future structured tool calls."""
    if hou is None:
        raise RuntimeError("hou module is not available")
    parent_node = hou.node(parent)
    if parent_node is None:
        raise RuntimeError("Parent node does not exist: %s" % parent)
    return parent_node.createNode(node_type, node_name=name).path()


def set_parm(path, parm, value):
    """Set a parameter using HOM. Intended for future structured tool calls."""
    if hou is None:
        raise RuntimeError("hou module is not available")
    node = hou.node(path)
    if node is None:
        raise RuntimeError("Node does not exist: %s" % path)
    parameter = node.parm(parm)
    if parameter is None:
        raise RuntimeError("Parameter does not exist: %s/%s" % (path, parm))
    parameter.set(value)
    return True

