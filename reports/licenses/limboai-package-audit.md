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
`demo/OFL-1.1.txt` supplies the license. The official OFL text and each font's
canonical project were used as the external rights check.

## Core rules

`scripts/package_release.py` includes only:

- the `.gdextension` manifest;
- exactly six desktop native libraries;
- all non-logo class icons;
- installation, compatibility, limitations, migration, and notices;
- the MIT license, version, and deterministic checksums.

It removes the `LimboAI.svg` mapping from the packaged manifest and excludes
the logo file. The package fails for missing platform binaries, dirty source
without an explicit evidence-only override, cache/test/build paths, private-key
markers, fixture markers, or local source paths.

## Demo rules

The separate demo archive includes the project/tutorial, branding copy,
CC BY notices, MIT notice for scripts, OFL notices/text, version, and
checksums. It contains no native addon or build cache.

Every archive entry receives a path, SHA-256, size, and license classification
in `release-manifest.json`. Two packaging runs are byte-compared locally and in
CI before artifacts are accepted. The workflow never publishes a GitHub
release.

## Final local archive result

Both runs used clean source commit
`f51be6ba2b2761234cfd6d804470a88379ce5538` and produced identical bytes:

| Archive | Entries | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `redot-limboai-1.6.0+redot.26.2.1-core.zip` | 78 | 10,420,481 | `FF4E028C09784A1C0F83BBC1F0AB6EAF6D6BB0FBD046F22745F463E94D1FEE70` |
| `redot-limboai-1.6.0+redot.26.2.1-demo.zip` | 171 | 3,733,279 | `30456BCF232E029368CBB9913F850581356C15A384F5E1CE3E4C0EB417ECC8A3` |

The core inventory contains the six audited native libraries, MIT material,
and approved addon documentation/icons only. The logo, demo, fonts, fixture,
test, cache, source checkout, credentials, and local build paths are absent.
The demo inventory contains no native addon or build cache. The package scan
and clean-install runtime checks pass; publication remains a separate owner
gate.
