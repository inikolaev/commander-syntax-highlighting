# commander-tree-sitter

The pinned Tree-sitter 0.25.10 runtime, SwiftTreeSitter 0.25.0 bindings, and
generated parsers used by [Commander](https://github.com/inikolaev/commander).
This package has no SwiftPM dependencies, so a clean Commander checkout fetches
one source repository for all built-in Tree-sitter languages.

`CommanderTreeSitter` exports the upstream `TreeSitter`, `SwiftTreeSitter`, and
individual `TreeSitter*` modules. Commander owns its highlight queries, semantic
styles, and language registry. This keeps registration configurable for future
plugins, while adding a built-in parser requires a new version of this package.

All generated parsers, their Swift C headers, and the Swift bindings are copied
from the exact revisions recorded in `UPSTREAM-PINS.json`. See `Licenses/` for
upstream license text. To update a grammar or the Swift bindings, edit its
revision (and version, where applicable) in `UPSTREAM-PINS.json`, then run:

```sh
python3 scripts/vendor.py --fetch
swift build
```

For a new language, also add its module to `Package.swift` and `GRAMMARS` in
`scripts/vendor.py`. Review the source and license diff, run Commander's syntax
tests, then release a new tag. Grammar query files are not included because
Commander carries its own highlight queries.
