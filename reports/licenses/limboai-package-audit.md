# Package rights and content audit

Date: 2026-08-11
Status: PASS for classification, package rules, and final local archives.

## Rights sources

| Content | License | Package |
| --- | --- | --- |
| LimboAI source, native binaries, non-logo class icons, docs | MIT-style `LICENSE.md` | Core |
| LimboAI logo | CC BY 4.0 `LOGO_LICENSE.md` | Demo only |
| Demo PNG/SVG graphics | CC BY 4.0 `demo/LICENSE_ASSETS.md` | Demo only |
| Junction Bold | SIL OFL 1.1 | Demo only |
| Knewave Regular, reserved name `Knewave` | SIL OFL 1.1 | Demo only |
| Redot C++/SCons/API dumps/build caches | Build input, not redistributed | Neither |

The font hashes and embedded copyright/license strings were inspected from the
shipped files. `demo/THIRD_PARTY_FONTS.md` supplies notices and
`demo/OFL-1.1.txt` supplies the license.

## Package rules

`scripts/package_release.py` includes in core only the `.gdextension`
manifest, exactly six desktop native libraries, non-logo class icons,
installation/compatibility/limitations/migration/notices, the MIT license,
version, and deterministic checksums. It removes the `LimboAI.svg` mapping and
excludes the logo file.

The separate demo archive includes the project/tutorial, branding copy, CC BY
notices, MIT notice for scripts, OFL notices/text, version, and checksums. It
contains no native addon or build cache.

Every archive entry receives a path, SHA-256, size, and license classification
in `release-manifest.json`. Packaging fails for missing platform binaries,
dirty source without an explicit evidence-only override, cache/test/build
paths, private-key markers, fixture markers, or local source paths. The
workflow never publishes a GitHub release.

## Final local archive result

Both runs used clean source commit
`a6c0d0863fb98f93d1219acbe6fc07b3608614be` and produced identical bytes:

| Archive | Entries | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `redot-limboai-1.8.0+redot.26.2.1-core.zip` | 78 | 10,762,336 | `D4C339702D7F3DCCDF5D414EDE7EA1F5C0174385DB65F7A75685CFCA88C39075` |
| `redot-limboai-1.8.0+redot.26.2.1-demo.zip` | 171 | 3,739,279 | `7F4C8A31C51BE566357E2D37966166730C1B5697CA8350F0D18FACEC426F3DE3` |

The core inventory contains the six audited native libraries, MIT material,
and approved addon documentation/icons only. The logo, demo, fonts, fixture,
test, cache, source checkout, credentials, and local build paths are absent.
The demo inventory contains no native addon or build cache. Fresh Windows and
Linux editor/release runs and an 89-file packed Linux release run pass from the
core archive. Source publication remains separate from tag/release authority.

Hosted workflow run `31476931577` independently packages commit `1470048`
twice after successful Windows, Linux, and native macOS jobs. The two outputs
match byte-for-byte: the 78-entry core SHA-256 is
`1872EF8284BD4DF670717963898769470B20F5AB057116CCCD6CA11390009B9F`, and
the 171-entry demo SHA-256 is
`7CC10D10E725C2E7D3EB7E91A61ED9EF82B8F62684B8C68263A8116F5EAB3D1D`.
They remain workflow evidence artifacts rather than a public release.
