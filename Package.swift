// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "commander-tree-sitter",
    platforms: [.macOS(.v13)],
    products: [.library(name: "SyntaxCore", targets: ["SyntaxCore"])],
    targets: [
        .binaryTarget(
            name: "SyntaxCore",
            url: "https://github.com/inikolaev/commander-tree-sitter/releases/download/0.2.0/SyntaxCore.xcframework.zip",
            checksum: "125a8dcbc20e271b09b7ca402b84668a80e1f5e59d7fdad60136b9b1e952ef1f"
        ),
    ]
)
