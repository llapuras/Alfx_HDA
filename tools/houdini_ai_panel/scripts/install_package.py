"""Install the Houdini package file for the local AI Assistant panel."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


PACKAGE_NAME = "hda_jd_ai_panel.json"


def _documents_dir():
    return Path.home() / "Documents"


def _houdini_pref_dirs():
    docs = _documents_dir()
    if not docs.exists():
        return []
    return sorted(
        [path for path in docs.iterdir() if path.is_dir() and path.name.lower().startswith("houdini")],
        key=lambda path: path.name,
    )


def _default_pref_dir():
    dirs = _houdini_pref_dirs()
    if not dirs:
        raise RuntimeError("No Houdini preference directory found under %s" % _documents_dir())
    return dirs[-1]


def _plugin_root():
    return Path(__file__).resolve().parents[1]


def _package_payload(plugin_root):
    root = plugin_root.as_posix()
    return {
        "env": [
            {"HDA_JD_AI_PANEL": root},
            {"PYTHONPATH": "$HDA_JD_AI_PANEL/python;$PYTHONPATH"},
            {"HOUDINI_PYTHON_PANEL_PATH": "$HDA_JD_AI_PANEL/python_panels;$HOUDINI_PYTHON_PANEL_PATH"},
        ]
    }


def install(pref_dir=None):
    pref_path = Path(pref_dir) if pref_dir else _default_pref_dir()
    packages_dir = pref_path / "packages"
    packages_dir.mkdir(parents=True, exist_ok=True)

    package_path = packages_dir / PACKAGE_NAME
    payload = _package_payload(_plugin_root())
    package_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return package_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pref-dir",
        help="Houdini preference directory, for example C:\\Users\\you\\Documents\\houdini21.0",
    )
    args = parser.parse_args()
    package_path = install(args.pref_dir)
    print("Installed Houdini package:")
    print(package_path)
    print("Restart Houdini, then open a Python Panel and choose AI Assistant.")


if __name__ == "__main__":
    main()
