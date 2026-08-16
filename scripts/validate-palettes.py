#!/usr/bin/env python3
"""Validate that Zed and JetBrains themes use the same core colors as colors/.

Usage:
    python3 scripts/validate-palettes.py
    python3 scripts/validate-palettes.py --target zed
    python3 scripts/validate-palettes.py --target jetbrains
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLORS_DIR = ROOT / "colors"
ZED_THEMES_DIR = ROOT / "suannhai-zed" / "themes"
JB_SCHEMES_DIR = (
    ROOT / "suannhai-jetbrains" / "src" / "main" / "resources" / "colorSchemes"
)

# Maps colors/ filenames to (zed filename, jetbrains XML filename)
PALETTE_MAP = {
    "formosa-hue-poo.json": ("suannhai-hue-poo.json", "Suannhai Hue-poo.xml"),
    "formosa-jiufen.json": ("suannhai-jiufen.json", "Suannhai Jiufen.xml"),
    "formosa-lam-ni.json": ("suannhai-lam-ni.json", "Suannhai Lam-ni.xml"),
    "nippon-koiai.json": ("suannhai-koiai.json", "Suannhai Koiai.xml"),
    "nippon-rouiro.json": ("suannhai-rouiro.json", "Suannhai Rouiro.xml"),
    "nippon-shironeri.json": ("suannhai-shironeri.json", "Suannhai Shironeri.xml"),
    "nippon-sumi.json": ("suannhai-sumi.json", "Suannhai Sumi.xml"),
    "nippon-torinoko.json": ("suannhai-torinoko.json", "Suannhai Torinoko.xml"),
}

# colors/ role -> Zed syntax key
ZED_SYNTAX_MAP = {
    "keyword": "keyword",
    "function": "function",
    "string": "string",
    "type": "type",
    "number": "number",
    "constant": "constant",
    "comment": "comment",
    "foreground": "variable",
    "error": "comment.error",
}

# colors/ role -> Zed style key (UI colors)
ZED_STYLE_MAP = {
    "background": "editor.background",
    "foreground": "editor.foreground",
    "error": "error",
}

# colors/ role -> JetBrains XML attribute name (FOREGROUND value)
JB_ATTR_MAP = {
    "keyword": "DEFAULT_KEYWORD",
    "function": "DEFAULT_FUNCTION_DECLARATION",
    "string": "DEFAULT_STRING",
    "type": "DEFAULT_CLASS_NAME",
    "number": "DEFAULT_NUMBER",
    "constant": "DEFAULT_CONSTANT",
    "comment": "DEFAULT_LINE_COMMENT",
    "error": "DEFAULT_INVALID_STRING_ESCAPE",
}

# colors/ role -> JetBrains XML <colors> option name
JB_COLOR_MAP = {
    "background": ("TEXT", "BACKGROUND"),  # attribute name, sub-option
    "foreground": ("TEXT", "FOREGROUND"),
}


def load_source_palette(path: Path) -> dict[str, str]:
    """Load colors/ JSON and return {role: hex} dict."""
    data = json.loads(path.read_text())
    palette = {}
    for group in ("neutrals", "accents", "diagnostic"):
        for role, info in data.get(group, {}).items():
            palette[role] = info["hex"].upper()
    return palette


def normalize_hex(value: str) -> str:
    """Normalize hex color to uppercase with #, 6-char form."""
    value = value.strip().upper()
    if not value.startswith("#"):
        value = "#" + value
    return value[:7]  # strip alpha if present


def validate_zed(source_palette: dict[str, str], zed_path: Path) -> list[str]:
    """Validate Zed theme against source palette. Returns list of drift messages."""
    if not zed_path.exists():
        return [f"  MISSING: {zed_path.name}"]

    data = json.loads(zed_path.read_text())
    style = data["themes"][0]["style"]
    syntax = style.get("syntax", {})
    drifts = []

    # Check syntax colors
    for role, zed_key in ZED_SYNTAX_MAP.items():
        if role not in source_palette:
            continue
        entry = syntax.get(zed_key)
        if not entry:
            continue
        zed_color = normalize_hex(entry["color"])
        expected = source_palette[role]
        if zed_color != expected:
            drifts.append(f"  DRIFT syntax.{zed_key}: expected {expected}, got {zed_color}")

    # Check UI colors
    for role, style_key in ZED_STYLE_MAP.items():
        if role not in source_palette:
            continue
        value = style.get(style_key)
        if not value:
            continue
        zed_color = normalize_hex(value)
        expected = source_palette[role]
        if zed_color != expected:
            drifts.append(f"  DRIFT {style_key}: expected {expected}, got {zed_color}")

    return drifts


def validate_jetbrains(source_palette: dict[str, str], xml_path: Path) -> list[str]:
    """Validate JetBrains color scheme XML against source palette."""
    if not xml_path.exists():
        return [f"  MISSING: {xml_path.name}"]

    tree = ET.parse(xml_path)
    root = tree.getroot()
    drifts = []

    # Build lookup: attribute name -> {sub_option: value}
    attr_map = {}
    for option in root.findall(".//attributes/option"):
        name = option.get("name")
        values = {}
        for val in option.findall(".//value/option"):
            values[val.get("name")] = val.get("value", "")
        attr_map[name] = values

    # Check syntax colors via attributes
    for role, attr_name in JB_ATTR_MAP.items():
        if role not in source_palette:
            continue
        entry = attr_map.get(attr_name, {})
        fg = entry.get("FOREGROUND")
        if fg is None:
            continue
        jb_color = normalize_hex(fg)
        expected = source_palette[role]
        if jb_color != expected:
            drifts.append(
                f"  DRIFT {attr_name}/FOREGROUND: expected {expected}, got {jb_color}"
            )

    # Check TEXT background/foreground
    text_entry = attr_map.get("TEXT", {})
    for role, (attr_name, sub_opt) in JB_COLOR_MAP.items():
        if role not in source_palette:
            continue
        value = text_entry.get(sub_opt)
        if value is None:
            continue
        jb_color = normalize_hex(value)
        expected = source_palette[role]
        if jb_color != expected:
            drifts.append(
                f"  DRIFT {attr_name}/{sub_opt}: expected {expected}, got {jb_color}"
            )

    return drifts


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate theme palettes against colors/")
    parser.add_argument(
        "--target",
        choices=["zed", "jetbrains", "all"],
        default="all",
        help="Which theme targets to validate (default: all)",
    )
    args = parser.parse_args()

    targets = (
        [args.target] if args.target != "all" else ["zed", "jetbrains"]
    )

    has_drift = False

    for color_file, (zed_file, jb_file) in PALETTE_MAP.items():
        color_path = COLORS_DIR / color_file
        if not color_path.exists():
            print(f"SKIP {color_file}: source not found")
            continue

        palette = load_source_palette(color_path)
        name = Path(color_file).stem
        drifts = []

        if "zed" in targets:
            zed_drifts = validate_zed(palette, ZED_THEMES_DIR / zed_file)
            if zed_drifts:
                drifts.append("  [zed]")
                drifts.extend(zed_drifts)

        if "jetbrains" in targets:
            jb_drifts = validate_jetbrains(palette, JB_SCHEMES_DIR / jb_file)
            if jb_drifts:
                drifts.append("  [jetbrains]")
                drifts.extend(jb_drifts)

        if drifts:
            print(f"{name}: DRIFT")
            for d in drifts:
                print(d)
            has_drift = True
        else:
            print(f"{name}: OK")

    return 1 if has_drift else 0


if __name__ == "__main__":
    sys.exit(main())
