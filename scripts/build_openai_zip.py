"""Build the ChatGPT plugin ZIP from openai/ plus the shared skill and icons.

    python scripts/build_openai_zip.py   ->  dist/gemstoneai-chatgpt-<version>.zip
"""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "openai"
SHARED = ROOT / "plugins" / "gemstoneai"
ICON = SHARED / "assets" / "icon-512.png"


def main() -> None:
    manifest = json.loads((SRC / "plugin.json").read_text())
    out = ROOT / "dist" / f"gemstoneai-chatgpt-{manifest['version']}.zip"
    out.parent.mkdir(exist_ok=True)
    files = {
        "plugin.json": SRC / "plugin.json",
        "mcp.json": SRC / "mcp.json",
        "skills/get-started/SKILL.md": SRC / "skills" / "get-started" / "SKILL.md",
        "skills/jewelry-research/SKILL.md": SHARED / "skills" / "jewelry-research" / "SKILL.md",
    }
    for name in ("composer-icon", "composer-icon-dark", "logo", "logo-dark"):
        files[f"assets/{name}.png"] = ICON
    iface = manifest["extensions"]["com.openai"]["interface"]
    for key in ("composerIcon", "composerIconDark", "logo", "logoDark"):
        assert iface[key].removeprefix("./") in files, key
    assert len(iface["displayName"]) <= 30 and len(iface["shortDescription"]) <= 30
    assert len(iface["longDescription"]) <= 4000 and all(len(c) <= 120 for c in iface["capabilities"])
    assert len(iface["defaultPrompt"]) <= 3 and all(len(p) <= 128 for p in iface["defaultPrompt"])
    cases = manifest["extensions"]["com.openai"]["review"]["test_cases"]
    assert len(cases["positive"]) == 5 and len(cases["negative"]) == 3
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, path in files.items():
            z.write(path, arc)
    print(out, f"{out.stat().st_size // 1024} KB", sorted(files))


if __name__ == "__main__":
    main()
