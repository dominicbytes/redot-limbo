# GNT-04 — Desktop package, export, and rights

Date: 2026-08-11
Mode: SELF_REVIEW (no delegated critics were authorized)
Verdict: **BLOCKED**

## Passing evidence

- Final Windows x86-64 editor/template-release DLLs pass PE dependency,
  symbol, signature-state, and forbidden-string audits plus all 11 fixture
  cases.
- Final Linux x86-64 editor/template-release shared objects pass ELF audits
  plus all 11 fixture cases; the exact release binary extracted from the core
  archive passes a newly generated 89-file packed PCK.
- Both macOS universal frameworks pass a strict two-slice Mach-O audit,
  including macOS 11.0, system-only dependency, stable install identity,
  required symbol, and zero forbidden strings.
- Core/demo content is rights-separated and every source, logo, demo graphic,
  and font license is classified.
- Two clean-source packaging runs from `f51be6ba` are byte-identical. The
  78-entry core SHA-256 is `FF4E028C...D1FEE70`; the 171-entry demo SHA-256 is
  `30456BCF...ECC8A3`.
- A fresh core extraction passes Windows and Ubuntu 24.04 editor and
  template-release fixtures: all 11 cases and zero suspicious lines in each.

## Self-review lenses

| Lens | Finding |
| --- | --- |
| Native binaries | PASS structurally on all six binaries; BLOCKED on native macOS runtime. |
| Clean install | PASS for headless Windows/Linux fixtures extracted from the final core archive; visible authoring remains open. |
| Export isolation | PASS for the exact packaged Linux release library and new packed PCK; Windows/macOS native exported products remain open. |
| Rights/attribution | PASS for classification, package rules, and final file-level archive inventories. |
| Reproducibility | PASS for two byte-identical clean-source core/demo package runs. |
| Unlensed read | No partial artifact may be labeled a public release candidate under the frozen rules. |

GNT-04 remains blocked by native macOS execution, Windows/macOS export and
interactive editor evidence, and owner publication authorization. The
workflow uploads evidence only and performs no public release.
