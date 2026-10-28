# Upstream and dependency lock

Lock date: 2026-10-19. All hashes are hexadecimal SHA-256 unless identified as
Git object IDs. This source lock does not establish a published binary release.

## Source selection

| Field | Locked value |
| --- | --- |
| Project | LimboAI |
| Canonical repository | `https://github.com/limbonaut/limboai` |
| Selected tag | `v1.8.0` |
| Selected commit | `3fbd85118b924d50c10a495ad5c7175028649d77` |
| Selected tree | `6b7600efa803889a544b3683f2e7da59745e9ac0` |
| Compatibility checkpoint | `v1.6.0@91b22a187f7cd701e25eedd6dcff34179795e687` |
| Compatibility-checkpoint tree | `ef660c9ad2fbafb11cff12c12bad9774f52734d1` |
| Downstream branch | `port/redot-26.2` |
| Downstream version | `1.8.0+redot.26.2.1` |

The complete immutable `v1.8.0` tag is the feature baseline. It contains all
49 non-merge commits after `v1.6.0`, including the 1.7 editor/debugger/HSM
features and the 1.8 safety/build fixes. Upstream targets Godot 4.6 and carries
4.7 build compatibility; this downstream preserves that source baseline while
adapting only engine-facing incompatibilities proven against Redot 26.2's
4.5.2 API lineage. The current Redot adaptations are listed in
`COMPATIBILITY.md`; source-build instructions are in `README.md`.

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
| Redot C++ binding | `https://github.com/dominicbytes/redot-cpp`, commit `9e7161bd7a3572a36ffa93109e73169861e9f834` | Git commit |

The official engine-generated API is the accepted build input. A second clean
dump produced the same hash. The source-backed API is retained as comparison
evidence; a recursive comparison found no class, method, enum, singleton,
utility, native-structure, or builtin-class delta, only official/custom build
labels.

## Supported runtimes and downstream binding patch

The build identity is `REDOT_BUILD_VERSION=26.2.stable.official.4f5b14aba`.
The supported runtimes are that exact 26.2 release and
`26.3.stable.official.85e520394`. Both run the same libraries built against
the locked 26.2 API and interface above. No 26.3 API generation is used for builds.
The supplied 26.3 API is a strict superset with unchanged existing builtin
storage sizes and native structures; it appends Struct at type 39.

Official 26.3 archives from the
[Redot release assets](https://github.com/Redot-Engine/redot-engine/releases/tag/redot-26.3-stable)
were downloaded and their SHA-256 verified against the release asset digests:

| Runtime archive | SHA-256 |
| --- | --- |
| `Redot_v26.3-stable_windows_win64.zip` | `2C6C7B4E96A88CA44EB413D9A5D43B8468B60A346C2448854C1A0C6BC9BAAB76` |
| `Redot_v26.3-stable_linux_x64.zip` | `7D5155B80F4262F0A394C5040E539BB330CB63DD147BEDD9172D83EC2EFDBD91` |
| `Redot_v26.3-stable_macos_universal.zip` | `BF781AE53DFAA4BBC6AADD21EBF2C69DA3681ED85894D3AB2A816F0B03755A34` |

The owner binding fork fixes the Array initializer-list constructor and retains
the 26.2 API. It still needs one mandatory downstream patch:
`patches/redot-cpp-variant-forward-compat.patch`. It fixes PackedVector4Array
cleanup and routes unknown runtime types through engine destruction.
Run `python scripts/prepare_binding.py --apply` after installing the locked API.
Preparation and SCons both verify the patch, locked preimage, and effective
postimage, rejecting unrelated binding source changes. Source hashes normalize
CRLF to LF; the patch itself is pinned byte-for-byte with LF checkout rules.

| Patched input | SHA-256 |
| --- | --- |
| Patch file | `DD388F84367D1624A58E2B9AF65F6F18726B7B45B74283AF6AF87E1A52CF7A85` |
| `src/variant/variant.cpp`, preimage | `DDE55AE4B59881CA42C4A2897F198CA562A552CC8E7483D49FF6BAB89D184E74` |
| `src/variant/variant.cpp`, postimage | `A64AE038023F0E111C0041AC35C09959FA0F095C56707A71C1D10CB59A4392D2` |

The temporary 26.3 editor-import shutdown exception is documented in
`LIMITATIONS.md`. Runtime diagnostics remain strict on both releases.

## Reference engines and build tools

| Input | Locked value |
| --- | --- |
| Redot API-lineage checkpoint | Godot `4.5.2.stable.official.6ce3de25a`; SHA-256 `446E08F71624052572F96DE9031850BA96382CE6752ADDE38BB955B0A49BED01` |
| Compatibility-checkpoint Godot C++ | commit `58d1de720b8ffe9f8ffcdfe3a85148582cfd2e74` with Godot 4.4 API |
| Compatibility-checkpoint API | SHA-256 `8A8386E3597083CF4357B3DBF501EDE3D38A4E3F7FF75DA86DFEF0D1D9C3E3A8` |
| Upstream v1.8 Godot C++ reference | commit `5ffd70e34d0ab87009a9f0ffa3361bc8f4b09731`, Godot 4.6 API |
| SCons | `4.10.1` |
| Windows compiler | Visual Studio 2022 MSVC `19.44` |
| Cross-build container | `ghcr.io/rust-cross/cargo-zigbuild@sha256:b8364c2c60cdcc9b95c402d17654bff517410926a35678bd89dd924b8158d6ae` |
| CI checkout action | `actions/checkout@11d5960a326750d5838078e36cf38b85af677262` |
| CI upload action | `actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02` |
| CI download action | `actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093` |

The Godot 4.5.2 fixture remains historical API-lineage evidence for the former
1.6 checkpoint; it is not presented as an oracle for 1.8-only behavior.

## Rights lock

| Content | License | SHA-256 |
| --- | --- | --- |
| Core source, `LICENSE.md` | MIT-style | `BEED25D187C191D7FC30CC9EED7E040571C86BFEDC23BAC06CCAD05A99FF9B56` |
| Redot C++ bindings, `LICENSE_REDOT_CPP.md` | MIT | `67F3B52502D83AD1737C89B0A1CFC5FF08DFFAFFE78715D45F906E99C43E1AE4` |
| Logo, `LOGO_LICENSE.md` | CC BY 4.0 | `B3CF21D09F7E2191AED99AE8E3F57E8006BDA915F489A732B160BB3FA83E9D31` |
| Demo graphics, `demo/LICENSE_ASSETS.md` | CC BY 4.0 | `98E9F4B4A73A158C17F4410E0E49EF21F15041D20CD69C8818AFDAFF62B9246C` |
| Junction Bold | SIL OFL 1.1 | `C12EB45E8764A687B53DA149EEB9813D67762315FC3B42DE13B1A7A6E2240150` |
| Knewave Regular | SIL OFL 1.1; reserved name `Knewave` | `80E6C7DA48890789171F46F07F97E207BB04C1299B663EDC506F951100F0F124` |

The core package excludes `LimboAI.svg`, the documentation logo, and all demo
content. The deterministic package manifest records each shipped path, hash,
size, and license classification. Binary and archive content checks are
separate from the immutable input hashes recorded here.
