#!/usr/bin/env python3
"""Generate Lua palette files for suannhai-nvim from the canonical JSON color definitions."""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COLORS_DIR = REPO_ROOT / "colors"
PALETTES_DIR = REPO_ROOT / "suannhai-nvim" / "lua" / "suannhai" / "palettes"

# JSON filename prefix -> Lua filename (without extension)
PREFIX_MAP = {
    "formosa-": "",
    "nippon-": "",
}

# JSON nested keys -> flat Lua keys
KEY_MAP = {
    "background": "bg",
    "foreground": "fg",
    "function": "func",
}


def json_to_lua_name(json_name: str) -> str:
    """formosa-jiufen.json -> jiufen, nippon-rouiro.json -> rouiro"""
    stem = Path(json_name).stem
    for prefix in PREFIX_MAP:
        if stem.startswith(prefix):
            return stem[len(prefix):]
    return stem


def extract_palette(data: dict) -> list[tuple[str, str]]:
    """Extract (lua_key, value) pairs from JSON color data, preserving group order."""
    entries: list[tuple[str, str]] = []

    for group in ("neutrals", "accents", "diagnostic"):
        for role, info in data.get(group, {}).items():
            lua_key = KEY_MAP.get(role, role)
            entries.append((lua_key, info["hex"]))

    entries.append(("appearance", data["appearance"]))
    return entries


def render_lua(lua_name: str, entries: list[tuple[str, str]]) -> str:
    """Render a Lua palette file from extracted entries."""
    lines = [
        f"-- suannhai-nvim/lua/suannhai/palettes/{lua_name}.lua",
        "---@class suannhai.Palette",
        "return {",
    ]

    # Group: neutrals (first 5), accents (next 6), diagnostic (next 1), meta (last)
    groups = [
        entries[:5],   # neutrals
        entries[5:11],  # accents
        entries[11:12], # diagnostic
        entries[12:],   # appearance
    ]

    for i, group in enumerate(groups):
        for key, val in group:
            if key == "appearance":
                lines.append(f'  {key} = "{val}",')
            else:
                lines.append(f'  {key} = "{val}",')
        if i < len(groups) - 1:
            lines.append("")

    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    if not COLORS_DIR.is_dir():
        print(f"error: colors directory not found: {COLORS_DIR}", file=sys.stderr)
        return 1

    if not PALETTES_DIR.is_dir():
        print(f"error: palettes directory not found: {PALETTES_DIR}", file=sys.stderr)
        return 1

    changed = []

    for json_file in sorted(COLORS_DIR.glob("*.json")):
        lua_name = json_to_lua_name(json_file.name)
        lua_path = PALETTES_DIR / f"{lua_name}.lua"

        with open(json_file) as f:
            data = json.load(f)

        entries = extract_palette(data)
        content = render_lua(lua_name, entries)

        # Only write if content changed
        existing = lua_path.read_text() if lua_path.exists() else ""
        if content != existing:
            lua_path.write_text(content)
            changed.append(lua_name)
            print(f"updated: {lua_path.relative_to(REPO_ROOT)}")
        else:
            print(f"unchanged: {lua_path.relative_to(REPO_ROOT)}")

    if changed:
        print(f"\n{len(changed)} palette(s) updated: {', '.join(changed)}")
    else:
        print("\nall palettes up to date")

    return 0


if __name__ == "__main__":
    sys.exit(main())
