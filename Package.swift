// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "commander-tree-sitter",
    platforms: [.macOS(.v13)],
    products: [.library(name: "SyntaxCore", targets: ["SyntaxCore"])],
    targets: [
        .binaryTarget(
            name: "SyntaxCore",
            url: "https://github.com/inikolaev/commander-tree-sitter/releases/download/0.2.2/SyntaxCore.xcframework.zip",
            checksum: "7805e1d70dc6bd829569adff714f6159ed77694581d472f4063f5432d6d79a4e"
        ),
    ]
)
