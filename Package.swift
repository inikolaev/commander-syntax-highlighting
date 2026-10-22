// swift-tools-version: 6.2
import PackageDescription

let grammars = [
    "TreeSitterJSON", "TreeSitterPython", "TreeSitterRuby", "TreeSitterC",
    "TreeSitterCPP", "TreeSitterGo", "TreeSitterBash", "TreeSitterJavaScript",
    "TreeSitterHTML", "TreeSitterTypeScript", "TreeSitterTSX", "TreeSitterYAML",
    "TreeSitterTOML", "TreeSitterJava", "TreeSitterKotlin", "TreeSitterSwift",
    "TreeSitterRust", "TreeSitterStarlark", "TreeSitterCSS",
    "TreeSitterMarkdown", "TreeSitterMarkdownInline",
]
let scannerless: Set<String> = ["TreeSitterJSON", "TreeSitterC", "TreeSitterGo", "TreeSitterJava"]

let package = Package(
    name: "commander-tree-sitter",
    platforms: [.macOS(.v13)],
    products: [
        .library(name: "CommanderTreeSitter", targets: ["SwiftTreeSitter", "TreeSitter"] + grammars),
    ],
    targets: [
        .target(
            name: "TreeSitter", path: "Sources/TreeSitter",
            exclude: [
                "src/lib.c", "src/unicode/ICU_SHA", "src/unicode/README.md",
                "src/unicode/LICENSE", "src/wasm/stdlib-symbols.txt",
            ], sources: ["src"], publicHeadersPath: "include",
            cSettings: [
                .headerSearchPath("src"),
                .define("_POSIX_C_SOURCE", to: "200112L"),
                .define("_DEFAULT_SOURCE"),
                .define("_DARWIN_C_SOURCE"),
            ]
        ),
        .target(name: "SwiftTreeSitter", dependencies: ["TreeSitter"]),
    ] + grammars.map { name in
        .target(
            name: name, path: "Sources/\(name)",
            sources: scannerless.contains(name) ? ["src/parser.c"] : ["src/parser.c", "src/scanner.c"],
            publicHeadersPath: "include", cSettings: [.headerSearchPath("src")]
        )
    },
    cLanguageStandard: .c11
)
