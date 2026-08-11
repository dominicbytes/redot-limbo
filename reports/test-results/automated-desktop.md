# Automated desktop evidence

Date: 2026-08-11
Scope: headless/static automated evidence only.

## Locked source and engine

- Runtime source commit: `2e32af7802ef1d1fa8cd1b3d1e0a77b438b36398`.
- Harness hardening commit: `d35033e`.
- Clean package source commit: `f51be6ba2b2761234cfd6d804470a88379ce5538`.
- Redot: `26.2.stable.official.4f5b14aba`.
- Redot C++: `598ec78e86b2c240a023f6de13daba70f7de8610`.
- Official API SHA-256:
  `177E7796166929B2193C9CCE2FD32F59601A0147D0D1E7FE904B94E8F69F6577`.

The unchanged LimboAI 1.6.0 oracle and the selected Redot port normalize to
the same 11-case semantic result: registration, blackboard, resource round
trip, direct ticks, clone, built-in semantics, `BTPlayer`, 32 agents, custom
task categories, HSM/`BTState`, and runtime view/200 agents.

## Windows x86-64

| Profile | Bytes | SHA-256 | Result |
| --- | ---: | --- | --- |
| Editor | 2,435,584 | `D244C56657C1F5D145528BF2E893032709504F598A6574837A797466CEF6099F` | PE audit PASS; editor import and 11 cases PASS; zero suspicious lines. |
| Template release | 1,189,376 | `E01C5F14F39EE19DE695D18FA887B3A7A3D56BD40B0C6B13E15AAFC4D2E59971` | Exact forced release mapping and 11 cases PASS; zero suspicious lines. |

Both DLLs are PE x86-64, export `limboai_init`, depend only on
`KERNEL32.dll`, contain zero forbidden strings, and are not signed. The local
Redot editor SHA-256 is
`5633D02A28A73514084DF6A60FFE01FABDBBB9AC5E28FDFD590ED47277F51989`.

## Linux x86-64

| Profile | Bytes | SHA-256 | Result |
| --- | ---: | --- | --- |
| Editor | 5,784,048 | `F8E232A328E5EBFE1F9AB7606875A852AFD0D95E23C02D8C9BF3BD967A2CA3BF` | ELF audit PASS; editor import and 11 cases PASS; zero suspicious lines. |
| Template release | 4,039,856 | `2291FCABF6B92A391E07368883AAFB7F38CC52715EEDB9E9FDA2E3EEC3A63A7C` | ELF audit PASS; exact forced release mapping and 11 cases PASS; zero suspicious lines. |

Both shared objects are stripped ELF64 x86-64, export `limboai_init`, and
require only `libm.so.6`, `libc.so.6`, and `ld-linux-x86-64.so.2`. The Redot
Linux editor SHA-256 is
`11D299E0F01A63574E612C64718CA3037A65540139DEC7B93A87650EE9AAB2F3`.
Their ELF version requirements peak at `GLIBC_2.38`; the Ubuntu 24.04/glibc
2.38 floor is enforced by the binary audit and declared in the shipped
compatibility and limitations documents.
The exact release binary extracted from the final core archive also passes an
89-file packed PCK run with all 11 cases and zero suspicious lines. The packed
fixture SHA-256 is
`63F19B0741847F1D5A289DE1744C0C50DC6EA6A14B8C1C1768F5B68645AD13CB`.

## macOS universal

| Profile | Bytes | SHA-256 | Result |
| --- | ---: | --- | --- |
| Editor | 15,450,112 | `283E258CD9514743A233CAFD9B824ADC5BD8A1C6A7BA324B46BF0C3E4905520A` | Structural universal audit PASS. |
| Template release | 8,863,744 | `DC4F4FEE2E9B0144530B4D3CF5B7101DD7167FF79AB1897863B7AAA3C5BF60A6` | Structural universal audit PASS. |

Each framework has exactly x86-64 and arm64 slices, macOS 11.0 deployment
target, only `/usr/lib/libSystem.B.dylib`, `_limboai_init`, a stable
`@rpath/<binary-name>` install identity, and zero forbidden strings. Zig emits
an ad-hoc code-signature command for arm64 but not x86-64; neither constitutes
Developer ID signing or notarization. Native macOS execution remains a hosted
CI release gate.

## Deterministic archives and clean install

Two clean-source package runs from `f51be6ba` produced byte-identical archives:

| Archive | Entries | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Core | 78 | 10,420,481 | `FF4E028C09784A1C0F83BBC1F0AB6EAF6D6BB0FBD046F22745F463E94D1FEE70` |
| Demo | 171 | 3,733,279 | `30456BCF232E029368CBB9913F850581356C15A384F5E1CE3E4C0EB417ECC8A3` |

The core archive was extracted into a new addon root. Windows and Ubuntu 24.04
editor/template-release runs each passed all 11 cases with zero suspicious
lines. The forced release runs selected the exact packaged Windows and Linux
release hashes listed above. This proves headless initialization and runtime
behavior from the archive; it does not substitute for the visible editor
authoring protocol or native Windows/macOS game exports.

## Performance samples

The 200-agent sample completed in 3,172 microseconds (Windows editor), 2,984
microseconds (Windows release), 3,119 microseconds (Linux editor), and 2,566
microseconds (Linux release). Archive clean-install samples also passed at
3,796, 3,319, 3,299, and 2,906 microseconds respectively, and the packed Linux
run completed in 2,583 microseconds. These are smoke samples, not the plan's
required controlled warmup-plus-five performance claim.

## Gates not proven by this report

This report does not pass visible-editor UX/accessibility/debugger/lifecycle
work, the full five-run performance/oracle matrix, native macOS runtime,
native Windows/macOS exported products, Developer ID signing/notarization, or
publication.
