# commander-tree-sitter

Prebuilt, statically linked Tree-sitter syntax highlighting for Commander. The source branch pins upstream [Tree-sitter](https://github.com/tree-sitter/tree-sitter), [SwiftTreeSitter](https://github.com/ChimeHQ/SwiftTreeSitter), and language grammars as Swift Package Manager dependencies. Parser sources are not copied into this repository.

GitHub Actions builds one universal macOS `SyntaxCore.xcframework.zip` with Swift bindings, runtime, and grammars linked into its static framework binary. Release tags contain a binary-only Swift package manifest with the release URL and checksum. Consumers fetch that artifact instead of cloning and rebuilding grammar repositories. The `SyntaxCore` API and built-in language registry are part of the binary; the public `SyntaxRegistry(languages:)` initializer permits custom highlighters. Adding a new Tree-sitter grammar to the binary requires a new release.

## Development

`Package.swift` on `main` is the source build. Update an upstream version or revision there, then run `swift test`. CI tests the source package, builds the XCFramework, and runs a separate binary consumer.

To publish, run the **Build static SyntaxCore** workflow on `main` with a new `X.Y.Z` version. It creates a `binary/X.Y.Z` branch and a release tag of the same version. The tag has only a checksum-pinned `.binaryTarget` manifest. Consumers should use a release tag.

Commander has intentionally not been switched to this package yet.
