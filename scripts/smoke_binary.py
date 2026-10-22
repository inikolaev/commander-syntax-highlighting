#!/usr/bin/env python3
"""Verify a separate SwiftPM client can import and link the packaged binary."""

import os
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="syntaxcore-consumer-") as temp:
    client = pathlib.Path(temp)
    (client / "Sources" / "Consumer").mkdir(parents=True)
    (client / "SyntaxCore.xcframework").symlink_to(root / "dist" / "SyntaxCore.xcframework")
    (client / "Package.swift").write_text('''// swift-tools-version: 6.2
import PackageDescription
let package = Package(name: "Consumer", platforms: [.macOS(.v13)], targets: [
    .binaryTarget(name: "SyntaxCore", path: "SyntaxCore.xcframework"),
    .executableTarget(name: "Consumer", dependencies: ["SyntaxCore"]),
])
''')
    (client / "Sources" / "Consumer" / "main.swift").write_text('''import Foundation
import SyntaxCore
precondition(SyntaxRegistry.viewer.supports(URL(fileURLWithPath: "hello.swift")))
let source = Data(#"{"count":42}"#.utf8)
let highlighter = SyntaxRegistry.viewer.highlighter(for: URL(fileURLWithPath: "sample.json"), data: source)
precondition(highlighter.highlights(in: 0..<source.count).contains { $0.kind == .number })
print("SyntaxCore binary import and link OK")
''')
    subprocess.run(["swift", "run", "--disable-sandbox", "-c", "release", "Consumer"], cwd=client, check=True)
