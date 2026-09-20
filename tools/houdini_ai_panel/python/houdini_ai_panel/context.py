"""Read-only Houdini scene inspection helpers."""

from __future__ import annotations

import traceback

try:
    import hou
except ImportError:  # Allows import outside Houdini for lightweight syntax checks.
    hou = None


ROOT_PATHS = ("/obj", "/stage", "/mat", "/out", "/shop", "/img")
MAX_CHILDREN_PER_ROOT = 40
MAX_PARMS_PER_NODE = 24


def _safe_call(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def _parm_value(parm):
    try:
        value = parm.eval()
    except Exception:
        value = "<unreadable>"
    if isinstance(value, str) and len(value) > 160:
        return value[:157] + "..."
    return value


def _node_errors(node):
    errors = []
    for method_name in ("errors", "warnings"):
        method = getattr(node, method_name, None)
        if not method:
            continue
        try:
            messages = method()
        except Exception:
            messages = ()
        for message in messages or ():
            errors.append("%s: %s" % (method_name[:-1], message))
    return errors


def _node_brief(node, include_parms=False):
    data = {
        "path": _safe_call(node.path, ""),
        "name": _safe_call(node.name, ""),
        "type": _safe_call(lambda: node.type().nameWithCategory(), ""),
        "is_bypassed": _safe_call(node.isBypassed, False),
        "is_display_flag_set": _safe_call(node.isDisplayFlagSet, False),
        "errors": _node_errors(node),
    }
    if include_parms:
        parms = {}
        for parm in _safe_call(node.parms, ())[:MAX_PARMS_PER_NODE]:
            parms[_safe_call(parm.name, "")] = _parm_value(parm)
        data["parms"] = parms
    return data


def get_scene_summary():
    """Return a compact, read-only summary of the current Houdini scene."""
    if hou is None:
        return {"available": False, "error": "hou module is not available"}

    roots = {}
    for root_path in ROOT_PATHS:
        root = hou.node(root_path)
        if root is None:
            continue
        children = list(_safe_call(root.children, ()))
        roots[root_path] = {
            "child_count": len(children),
            "children": [_node_brief(child) for child in children[:MAX_CHILDREN_PER_ROOT]],
        }

    return {
        "available": True,
        "hip_file": _safe_call(hou.hipFile.path, ""),
        "hip_name": _safe_call(hou.hipFile.basename, ""),
        "frame": _safe_call(hou.frame, None),
        "fps": _safe_call(hou.fps, None),
        "roots": roots,
    }


def get_selected_nodes():
    """Return compact information about currently selected nodes."""
    if hou is None:
        return []
    return [_node_brief(node, include_parms=True) for node in hou.selectedNodes()]


def get_node_info(path):
    """Return detailed read-only information for a single node path."""
    if hou is None:
        return {"found": False, "error": "hou module is not available"}

    node = hou.node(path)
    if node is None:
        return {"found": False, "path": path}

    inputs = []
    for input_node in _safe_call(node.inputs, ()) or ():
        inputs.append(input_node.path() if input_node else None)

    outputs = []
    for output_node in _safe_call(node.outputs, ()) or ():
        outputs.append(output_node.path())

    data = _node_brief(node, include_parms=True)
    data.update(
        {
            "found": True,
            "inputs": inputs,
            "outputs": outputs,
            "children": [_node_brief(child) for child in _safe_call(node.children, ())[:MAX_CHILDREN_PER_ROOT]],
        }
    )
    return data


def collect_prompt_context():
    """Return the context blob sent with each chat request."""
    try:
        return {
            "scene": get_scene_summary(),
            "selected_nodes": get_selected_nodes(),
        }
    except Exception:
        return {
            "scene": {"available": False, "error": traceback.format_exc()},
            "selected_nodes": [],
        }

