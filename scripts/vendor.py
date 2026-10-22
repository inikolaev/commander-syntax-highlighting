#!/usr/bin/env python3
"""Refresh vendored sources from UPSTREAM-PINS.json.

Use --fetch to download the pinned revisions, or pass an existing directory of
checkouts with those exact revisions. Neither mode changes the pin file.
"""

import argparse
import json
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAMMARS = {
    "TreeSitterJSON": ("tree-sitter-json", "", "json"),
    "TreeSitterPython": ("tree-sitter-python", "", "python"),
    "TreeSitterRuby": ("tree-sitter-ruby", "", "ruby"),
    "TreeSitterC": ("tree-sitter-c", "", "c"),
    "TreeSitterCPP": ("tree-sitter-cpp", "", "cpp"),
    "TreeSitterGo": ("tree-sitter-go", "", "go"),
    "TreeSitterBash": ("tree-sitter-bash", "", "bash"),
    "TreeSitterJavaScript": ("tree-sitter-javascript", "", "javascript"),
    "TreeSitterHTML": ("tree-sitter-html", "", "html"),
    "TreeSitterTypeScript": ("tree-sitter-typescript", "typescript", "typescript"),
    "TreeSitterTSX": ("tree-sitter-typescript", "tsx", "tsx"),
    "TreeSitterYAML": ("tree-sitter-yaml", "", "yaml"),
    "TreeSitterTOML": ("tree-sitter-toml", "", "toml"),
    "TreeSitterJava": ("tree-sitter-java", "", "java"),
    "TreeSitterKotlin": ("tree-sitter-kotlin", "", "kotlin"),
    "TreeSitterSwift": ("tree-sitter-swift", "", "swift"),
    "TreeSitterRust": ("tree-sitter-rust", "", "rust"),
    "TreeSitterStarlark": ("tree-sitter-starlark", "", "starlark"),
    "TreeSitterCSS": ("tree-sitter-css", "", "css"),
    "TreeSitterMarkdown": ("tree-sitter-markdown", "tree-sitter-markdown", "markdown"),
    "TreeSitterMarkdownInline": ("tree-sitter-markdown", "tree-sitter-markdown-inline", "markdown_inline"),
}


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    destination.chmod(destination.stat().st_mode | stat.S_IWUSR)


def pinned_sources() -> dict[str, dict]:
    pins = json.loads((ROOT / "UPSTREAM-PINS.json").read_text())["pins"]
    by_name = {pin["identity"].lower(): pin for pin in pins}
    names = {"tree-sitter", "SwiftTreeSitter"} | {value[0] for value in GRAMMARS.values()}
    missing = {name for name in names if name.lower() not in by_name}
    if missing:
        raise RuntimeError(f"Missing upstream pins: {sorted(missing)}")
    return {name: by_name[name.lower()] for name in names}


def verify_checkout(source: Path, revision: str) -> None:
    if not source.is_dir():
        raise RuntimeError(f"Missing checkout: {source}")
    result = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    )
    if result.stdout.strip() != revision:
        raise RuntimeError(f"Wrong revision in {source}: expected {revision}, got {result.stdout.strip()}")


def fetch_sources(destination: Path, pins: dict[str, dict]) -> None:
    for name, pin in sorted(pins.items()):
        source = destination / name
        revision = pin["state"]["revision"]
        url = pin["location"]
        subprocess.run(["git", "init", "-q", str(source)], check=True)
        subprocess.run(["git", "-C", str(source), "remote", "add", "origin", url], check=True)
        subprocess.run(["git", "-C", str(source), "fetch", "-q", "--depth=1", "origin", revision], check=True)
        subprocess.run(["git", "-C", str(source), "checkout", "-q", "--detach", "FETCH_HEAD"], check=True)
        verify_checkout(source, revision)


def main(checkouts: Path) -> None:
    for name, pin in pinned_sources().items():
        verify_checkout(checkouts / name, pin["state"]["revision"])

    runtime = checkouts / "tree-sitter"
    target = ROOT / "Sources/TreeSitter"
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(runtime / "lib/src", target / "src")
    shutil.copytree(runtime / "lib/include", target / "include")

    swift = checkouts / "SwiftTreeSitter"
    target = ROOT / "Sources/SwiftTreeSitter"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    for file in (swift / "Sources/SwiftTreeSitter").glob("*.swift"):
        copy_file(file, target / file.name)

    for module, (repo, subdir, language) in GRAMMARS.items():
        source = checkouts / repo
        grammar = source / subdir
        target = ROOT / "Sources" / module
        shutil.rmtree(target, ignore_errors=True)
        src = grammar / "src"
        for name in ("parser.c", "scanner.c", "scanner.cc", "tag.h", "schema.core.c"):
            if (src / name).exists():
                copy_file(src / name, target / "src" / name)
        for file in (src / "tree_sitter").glob("*.h"):
            copy_file(file, target / "src/tree_sitter" / file.name)

        # The TypeScript scanners share a generated helper two levels above src.
        if module in ("TreeSitterTypeScript", "TreeSitterTSX"):
            copy_file(source / "common/scanner.h", target / "common/scanner.h")
            # Preserve the relative include in the upstream scanner source.
            scanner = target / "src/scanner.c"
            scanner.write_text(scanner.read_text().replace(
                '"../../common/scanner.h"', '"../common/scanner.h"'))

        headers = list(grammar.glob("bindings/swift/**/*.h"))
        if module in ("TreeSitterTypeScript", "TreeSitterTSX"):
            headers = list(source.glob(f"bindings/swift/{subdir}/**/*.h"))
        if len(headers) != 1:
            raise RuntimeError(f"Expected one Swift header for {module}: {headers}")
        copy_file(headers[0], target / "include" / module / headers[0].name)

    licenses = ROOT / "Licenses"
    shutil.rmtree(licenses, ignore_errors=True)
    for repo in sorted({"tree-sitter", "SwiftTreeSitter"} | {v[0] for v in GRAMMARS.values()}):
        source = checkouts / repo
        candidates = [p for p in source.iterdir() if p.is_file() and p.name.upper().startswith("LICENSE")]
        if not candidates:
            raise RuntimeError(f"Missing license for {repo}")
        for file in candidates:
            copy_file(file, licenses / repo / file.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--fetch", action="store_true", help="fetch every pin into a temporary directory")
    source.add_argument("--checkouts", type=Path, help="use existing checkouts at the pinned revisions")
    args = parser.parse_args()
    if args.fetch:
        with tempfile.TemporaryDirectory(prefix="commander-tree-sitter-") as temp:
            checkouts = Path(temp)
            fetch_sources(checkouts, pinned_sources())
            main(checkouts)
    else:
        main(args.checkouts.resolve())
