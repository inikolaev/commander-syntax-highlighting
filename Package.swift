// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "commander-tree-sitter",
    platforms: [.macOS(.v13)],
    products: [.library(name: "SyntaxCore", targets: ["SyntaxCore"])],
    targets: [
        .binaryTarget(
            name: "SyntaxCore",
            url: "https://github.com/inikolaev/commander-tree-sitter/releases/download/0.2.1/SyntaxCore.xcframework.zip",
            checksum: "ceab2a5bb085e1143ce0892b9d40d5ae7d3893c828ac0501b703dd2181792db4"
        ),
    ]
)
