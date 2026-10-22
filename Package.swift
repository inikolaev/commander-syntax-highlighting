// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "commander-syntax-highlighting",
    platforms: [.macOS(.v13)],
    products: [.library(name: "SyntaxCore", targets: ["SyntaxCore"])],
    targets: [
        .binaryTarget(
            name: "SyntaxCore",
            url: "https://github.com/inikolaev/commander-syntax-highlighting/releases/download/0.2.3/SyntaxCore.xcframework.zip",
            checksum: "4dec2439715863d873773fc6a9c94e332f232e015077bd0c91d1719fd4e7ad67"
        ),
    ]
)
