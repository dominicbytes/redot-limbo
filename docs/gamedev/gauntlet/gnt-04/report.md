# GNT-04 — Desktop package, export, and rights

Date: 2026-08-11
Mode: SELF_REVIEW (no delegated critics were authorized)
Verdict: **BLOCKED**

## Passing evidence

- Final Windows x86-64 editor/template-release DLLs pass PE dependency,
  symbol, signature-state, and forbidden-string audits plus all 13 fixture
  cases.
- Final Linux x86-64 editor/template-release shared objects pass ELF audits
  plus all 13 fixture cases; the exact release binary extracted from the core
  archive passes a newly generated 89-file packed PCK.
- Hosted macOS universal editor and template-release frameworks pass a strict
  two-slice Mach-O audit and native Redot execution: all 13 cases pass in both
  profiles with zero suspicious lines.
- Core/demo content is rights-separated and every source, logo, demo graphic,
  and font license is classified.
- Two clean-source packaging runs from `a6c0d08` are byte-identical. The
  78-entry core SHA-256 is `D4C33970...8C39075`; the 171-entry demo SHA-256 is
  `7F4C8A31...6F3DE3`.
- A fresh core extraction passes Windows and Ubuntu 24.04 editor and
  template-release fixtures: all 13 cases and zero suspicious lines in each.
- Fork workflow run `31476931577` passes Windows, Linux, native macOS, and two
  byte-identical CI package builds at source commit `1470048`.

## Self-review lenses

| Lens | Finding |
| --- | --- |
| Native binaries | PASS for hosted Windows, Linux, and native macOS builds, audits, and runtime fixtures. |
| Clean install | PASS for headless Windows/Linux fixtures extracted from the final core archive; visible authoring remains open. |
| Export isolation | PASS for the exact packaged Linux release library and 89-file PCK; Windows/macOS native exported products remain open. |
| Rights/attribution | PASS for classification, package rules, and final file-level archive inventories. |
| Reproducibility | PASS for two byte-identical clean-source core/demo package runs. |
| Unlensed read | Source publication is authorized; a binary release remains gated. |

GNT-04 remains blocked by native Windows/macOS exported-game evidence and
interactive editor authoring. The workflow uploads evidence only and performs
no public release.
