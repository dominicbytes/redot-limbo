# Automated desktop evidence

Date: 2026-08-11
Scope: headless/static automated evidence for the LimboAI 1.8 Redot port.

## Locked source and engine

- Runtime and clean-package source commit:
  `a6c0d0863fb98f93d1219acbe6fc07b3608614be`.
- Upstream second parent:
  `3fbd85118b924d50c10a495ad5c7175028649d77` (`v1.8.0`).
- Redot: `26.2.stable.official.4f5b14aba`.
- Redot C++: `598ec78e86b2c240a023f6de13daba70f7de8610`.
- Official API SHA-256:
  `177E7796166929B2193C9CCE2FD32F59601A0147D0D1E7FE904B94E8F69F6577`.

The final Redot fixture passes 13 cases: registration, blackboard contract,
v1.8 scoped runtime inspection, resource round trip, direct ticks, clone,
built-in semantics, `BTPlayer`, 32 agents, custom task categories, v1.8 HSM
transition cargo, HSM/`BTState`, and runtime view/200 agents. Editor and forced
release-library runs pass on Windows and Ubuntu 24.04 with zero suspicious
lines. The historical v1.6 Godot/Redot comparison remains API-lineage evidence,
not an oracle for 1.8-only behavior.

## Windows x86-64

| Profile | Bytes | SHA-256 | Result |
| --- | ---: | --- | --- |
| Editor | 2,454,016 | `ECFA90017DE6BEF0945C5FEA05CC8368F5F4BA6CBBC4B09347AD2ED3C90F914E` | PE audit PASS; editor import and 13 cases PASS; zero suspicious lines. |
| Template release | 1,203,200 | `312A6EB51B83A7EE79CF705F650EB40E2955C1820FD7F2A21F34413A0DC85E6B` | Exact forced release mapping and 13 cases PASS; zero suspicious lines. |

Both DLLs are PE x86-64, export `limboai_init`, depend only on
`KERNEL32.dll`, contain zero forbidden strings, and are not signed. The editor
binary contains downstream version `1.8.0+redot.26.2.1` and source short hash
`a6c0d08`. The local Redot editor SHA-256 is
`5633D02A28A73514084DF6A60FFE01FABDBBB9AC5E28FDFD590ED47277F51989`.

## Linux x86-64

| Profile | Bytes | SHA-256 | Build ID | Result |
| --- | ---: | --- | --- | --- |
| Editor | 6,104,080 | `FCDB32CF5A250F72077A980DAE9B0BAE8C5FEF60C04D8797439EDC4FA0BAA405` | `052ccef1bff88940c141637afa94f1c204c92c16` | ELF audit PASS; editor import and 13 cases PASS; zero suspicious lines. |
| Template release | 4,052,144 | `873BD867F3A844C65020F6F278A85A8F2B273A3FCAAB9EA5D2D3E629ABFE9656` | `52bf974f4a3a067fe4377973d1db00493e3625cf` | ELF audit PASS; exact forced release mapping and 13 cases PASS; zero suspicious lines. |

Both shared objects are stripped ELF64 x86-64, export `limboai_init`, and
require only `libm.so.6`, `libc.so.6`, and `ld-linux-x86-64.so.2`. Their ELF
version requirements peak at `GLIBC_2.38`. The Redot Linux editor SHA-256 is
`11D299E0F01A63574E612C64718CA3037A65540139DEC7B93A87650EE9AAB2F3`.

The exact release library extracted from the core archive also passes an
89-file packed PCK run with all 13 cases. The PCK is 39,247,688 bytes with
SHA-256
`1B453F33771D23FD2F6AE8B9F6B014C73AFD10C616A315D407B513873B1D293E`.
Native libraries remain alongside the PCK at deployment time because Redot
cannot load a GDExtension shared object from inside a PCK.

## macOS universal

| Profile | Bytes | SHA-256 | Result |
| --- | ---: | --- | --- |
| Editor | 16,449,536 | `3C45D891428A469CA6DF2C54433E073C3BB17A0913630F40F175BD385F42520C` | Structural universal audit PASS. |
| Template release | 8,896,512 | `19640178510822407C268CAFF28F91DEFCAC0DFB3A88179BD85859D9925A5FA3` | Structural universal audit PASS. |

Each framework has exactly x86-64 and arm64 slices, macOS 11.0 deployment
target, only `/usr/lib/libSystem.B.dylib`, `_limboai_init`, a stable
`@rpath/<binary-name>` install identity, and zero forbidden strings. Zig emits
an ad-hoc code-signature command for arm64 but not x86-64; neither constitutes
Developer ID signing or notarization. Verbose nullability diagnostics originate
in Zig's bundled libc++ build, not LimboAI source. The local cross-build is
supplemented by the hosted native validation below.

### Hosted native macOS validation

GitHub Actions run `31476931577` at source commit
`147004846d91a0e6292dd9d2dc7536c02db14a00` completed successfully on
`macos-14`. The native editor profile and forced template-release profile each
pass all 13 cases with zero suspicious lines. Their fixture results are read
from the single machine-readable stdout record because macOS does not honor
the Linux/Windows isolated `user://` location; the strict fallback is covered
by 10 Python unit tests.

| Hosted profile | Bytes | SHA-256 | Native result |
| --- | ---: | --- | --- |
| Editor | 4,193,704 | `2E2FECEAE4137B8DB50B11533C57750A740A0AFF8FE16425DC3406F16D6E05BA` | Mach-O audit and 13 cases PASS; zero suspicious lines. |
| Template release | 2,428,264 | `DEF8952D444111519F3C5C3768BF4AC769204900ECBF76D5D0F2887134C70BB0` | Mach-O audit and forced 13 cases PASS; zero suspicious lines. |

## Demo and deterministic archives

The final Windows editor library was copied into a clean imported 1.8 demo.
The project had already passed a 71-file static check; its final bounded full
run exits zero without parse, load, runtime, or warning output.

Two clean-source package runs from `a6c0d0863fb98f93d1219acbe6fc07b3608614be`
produced byte-identical archives and manifests:

| Archive | Entries | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Core | 78 | 10,762,336 | `D4C339702D7F3DCCDF5D414EDE7EA1F5C0174385DB65F7A75685CFCA88C39075` |
| Demo | 171 | 3,739,279 | `7F4C8A31C51BE566357E2D37966166730C1B5697CA8350F0D18FACEC426F3DE3` |

The core archive was extracted into a new addon root. Windows and Ubuntu 24.04
editor/template-release runs each passed all 13 cases with zero suspicious
lines, and the forced release runs selected the exact packaged hashes above.

The successful fork workflow also packaged source commit `1470048` twice from
its three hosted platform artifacts and byte-compared both outputs. Its
78-entry core is 6,940,615 bytes with SHA-256
`1872EF8284BD4DF670717963898769470B20F5AB057116CCCD6CA11390009B9F`;
its 171-entry demo is 3,741,988 bytes with SHA-256
`7CC10D10E725C2E7D3EB7E91A61ED9EF82B8F62684B8C68263A8116F5EAB3D1D`.
These CI artifacts are validation outputs, not a GitHub release.

## Performance smoke samples

Direct-build samples completed in 3,229 microseconds (Windows editor), 3,040
(Windows release), 3,174 (Linux editor), and 2,769 (Linux release). Fresh
archive samples completed in 3,229, 2,999, 3,301, and 2,691 microseconds in the
same order. The packed Linux run completed in 2,646 microseconds. These are
single smoke samples, not the plan's controlled warmup-plus-five performance
claim.

## Gates not proven by this report

This report does not pass visible-editor UX/accessibility/debugger/lifecycle
work, the full performance matrix, native Windows/macOS exported products,
Developer ID signing/notarization, or a public binary release. Source
publication to the designated Redot fork is complete; tags and releases are
not authorized.
