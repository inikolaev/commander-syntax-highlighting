#!/usr/bin/env python3
"""Build a universal static SyntaxCore XCFramework from pinned SwiftPM sources."""

import os
import pathlib
import plistlib
import shutil
import subprocess
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ARCHES = ("arm64", "x86_64")


def run(*args):
    print("+", *args, flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    for arch in ARCHES:
        # llbuild's shared database can retain commands from the previous triple.
        (ROOT / ".build" / "build.db").unlink(missing_ok=True)
        run(
            "swift", "build", "--configuration", "release", "--triple",
            f"{arch}-apple-macosx13.0", "--disable-sandbox",
        )

    xc = DIST / "SyntaxCore.xcframework"
    framework = xc / "macos-arm64_x86_64" / "SyntaxCore.framework"
    modules = framework / "Modules" / "SyntaxCore.swiftmodule"
    modules.mkdir(parents=True)
    libs = [ROOT / ".build" / f"{arch}-apple-macosx" / "release" / "libSyntaxCore.a" for arch in ARCHES]
    run("lipo", "-create", *(str(lib) for lib in libs), "-output", str(framework / "SyntaxCore"))

    for arch in ARCHES:
        build = ROOT / ".build" / f"{arch}-apple-macosx" / "release"
        shutil.copy2(build / "Modules" / "SyntaxCore.swiftinterface", modules / f"{arch}-apple-macos.swiftinterface")
        shutil.copy2(build / "Modules" / "SyntaxCore.swiftdoc", modules / f"{arch}-apple-macos.swiftdoc")

    (framework / "Info.plist").write_bytes(plistlib.dumps({
        "CFBundleDevelopmentRegion": "en",
        "CFBundleExecutable": "SyntaxCore",
        "CFBundleIdentifier": "com.inikolaev.commander.SyntaxCore",
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": "SyntaxCore",
        "CFBundlePackageType": "FMWK",
        "CFBundleShortVersionString": "1.0",
        "CFBundleVersion": "1",
    }))
    (xc / "Info.plist").write_bytes(plistlib.dumps({
        "AvailableLibraries": [{
            "BinaryPath": "SyntaxCore.framework/SyntaxCore",
            "LibraryIdentifier": "macos-arm64_x86_64",
            "LibraryPath": "SyntaxCore.framework",
            "SupportedArchitectures": list(ARCHES),
            "SupportedPlatform": "macos",
        }],
        "CFBundlePackageType": "XFWK",
        "XCFrameworkFormatVersion": "1.0",
    }))
    for name in ("LICENSE",):
        shutil.copy2(ROOT / name, xc / name)

    shutil.copytree(ROOT / "Licenses", xc / "Licenses")

    archive = DIST / "SyntaxCore.xcframework.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(xc.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(DIST))
    run("swift", "package", "compute-checksum", str(archive))


if __name__ == "__main__":
    main()
