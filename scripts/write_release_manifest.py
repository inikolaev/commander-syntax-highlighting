#!/usr/bin/env python3
"""Write the dependency-free manifest for a binary release tag."""

import pathlib
import re
import sys

version, checksum = sys.argv[1:]
if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
    raise SystemExit("version must be X.Y.Z")
if not re.fullmatch(r"[0-9a-f]{64}", checksum):
    raise SystemExit("checksum must be a SHA-256 hex digest")

pathlib.Path("Package.swift").write_text(f'''// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "commander-tree-sitter",
    platforms: [.macOS(.v13)],
    products: [.library(name: "SyntaxCore", targets: ["SyntaxCore"])],
    targets: [
        .binaryTarget(
            name: "SyntaxCore",
            url: "https://github.com/inikolaev/commander-tree-sitter/releases/download/{version}/SyntaxCore.xcframework.zip",
            checksum: "{checksum}"
        ),
    ]
)
''')
