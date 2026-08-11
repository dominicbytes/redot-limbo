# Upstream and dependency lock

Lock date: 2026-08-10. All hashes are hexadecimal SHA-256 unless identified as
Git object IDs. The public release gate is not implied by this source lock.

## Source selection

| Field | Locked value |
| --- | --- |
| Project | LimboAI |
| Canonical repository | `https://github.com/limbonaut/limboai` |
| Selected tag | `v1.6.0` |
| Selected commit | `91b22a187f7cd701e25eedd6dcff34179795e687` |
| Selected tree | `ef660c9ad2fbafb11cff12c12bad9774f52734d1` |
| Newest evaluated tag | `v1.8.0` |
| Newest commit | `3fbd85118b924d50c10a495ad5c7175028649d77` |
| Newest tree | `6b7600efa803889a544b3683f2e7da59745e9ac0` |
| Downstream branch | `port/redot-26.2` |
| Downstream version | `1.6.0+redot.26.2.1` |

`v1.8.0` was rejected as the baseline because it requires Godot API 4.6 and
contains later 4.6/4.7 editor and content work. The newest viable 1.6 release
built and ran unchanged under Godot 4.5.2 and Redot 26.2. Every later non-merge
commit is dispositioned in
`reports/api-diffs/limboai-newest-vs-selected.md`.

## Engine and ABI

| Input | Version / commit | SHA-256 |
| --- | --- | --- |
| Redot Windows console editor | `26.2.stable.official.4f5b14aba`; engine commit `4f5b14abade2239104847d03d8f9056e4467cfcd` | `5633D02A28A73514084DF6A60FFE01FABDBBB9AC5E28FDFD590ED47277F51989` |
| Redot Windows release archive | `Redot_v26.2-stable_windows_win64.zip` | `4644C7591BBE8019B861DEB0CCDB64FD4F59A88514ABF7C788CF176C259855AF` |
| Redot Linux release archive | `Redot_v26.2-stable_linux_x64.zip` | `F474D890806C41AF15513CF5A8600243E241882E11B68DBB95660E3465B5B1E4` |
| Redot macOS release archive | `Redot_v26.2-stable_macos_universal.zip` | `128CB7BCA69B95A3998A84E72B0990A302CE5B1919DFB56CFDC709C2C87925AE` |
| Official Redot extension API | Engine-generated, single precision | `177E7796166929B2193C9CCE2FD32F59601A0147D0D1E7FE904B94E8F69F6577` |
| Redot C++ source-backed API | Same 4.5.2 callable/type surface; custom-build labels only | `453A0CC128BB58333A001F7F43573A5961D973FB7B151AF43139869F22D5915C` |
| Redot C++ interface header | Binding checkout file | `4CD695E86B92E2BF4E60BBE19CE137FAF41205DA1CF94F29E069AFEC0F7BF320` |
| Redot C++ binding | `https://github.com/Redot-Engine/redot-cpp`, commit `598ec78e86b2c240a023f6de13daba70f7de8610` | Git commit |

The official engine-generated API is the accepted build input. A second clean
dump produced the same hash. The source-backed API is retained as comparison
evidence; a recursive comparison found no class, method, enum, singleton,
utility, native-structure, or builtin-class delta, only official/custom build
labels.

## Oracle and build tools

| Input | Locked value |
| --- | --- |
| Godot oracle | `4.5.2.stable.official.6ce3de25a`; SHA-256 `446E08F71624052572F96DE9031850BA96382CE6752ADDE38BB955B0A49BED01` |
| Upstream Godot C++ oracle | tag `10.0.0-rc1`, commit `58d1de720b8ffe9f8ffcdfe3a85148582cfd2e74` |
| Oracle API | Godot 4.4 JSON, SHA-256 `8A8386E3597083CF4357B3DBF501EDE3D38A4E3F7FF75DA86DFEF0D1D9C3E3A8` |
| SCons | `4.10.1` |
| Windows compiler | Visual Studio 2022 MSVC `19.44` |
| Cross-build container | `ghcr.io/rust-cross/cargo-zigbuild@sha256:b8364c2c60cdcc9b95c402d17654bff517410926a35678bd89dd924b8158d6ae` |
| CI checkout action | `actions/checkout@11d5960a326750d5838078e36cf38b85af677262` |
| CI upload action | `actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02` |
| CI download action | `actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093` |

## Rights lock

| Content | License | SHA-256 |
| --- | --- | --- |
| Core source, `LICENSE.md` | MIT-style | `BEED25D187C191D7FC30CC9EED7E040571C86BFEDC23BAC06CCAD05A99FF9B56` |
| Logo, `LOGO_LICENSE.md` | CC BY 4.0 | `B3CF21D09F7E2191AED99AE8E3F57E8006BDA915F489A732B160BB3FA83E9D31` |
| Demo graphics, `demo/LICENSE_ASSETS.md` | CC BY 4.0 | `98E9F4B4A73A158C17F4410E0E49EF21F15041D20CD69C8818AFDAFF62B9246C` |
| Junction Bold | SIL OFL 1.1 | `C12EB45E8764A687B53DA149EEB9813D67762315FC3B42DE13B1A7A6E2240150` |
| Knewave Regular | SIL OFL 1.1; reserved name `Knewave` | `80E6C7DA48890789171F46F07F97E207BB04C1299B663EDC506F951100F0F124` |

The core package excludes `LimboAI.svg`, the documentation logo, and all demo
content. The deterministic package manifest assigns every shipped path to a
license and rejects caches, tests, build inputs, private-key markers, and local
workspace paths.
