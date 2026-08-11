# GNT-04 — Desktop package, export, and rights

Date: 2026-08-11
Mode: SELF_REVIEW (no delegated critics were authorized)
Verdict: **BLOCKED**

## Passing evidence

- Final Windows x86-64 editor/template-release DLLs pass PE dependency,
  symbol, signature-state, and forbidden-string audits plus all 11 fixture
  cases.
- Final Linux x86-64 editor/template-release shared objects pass ELF audits
  plus all 11 fixture cases; the release binary is identical to the earlier
  passing packed-PCK artifact.
- Both macOS universal frameworks pass a strict two-slice Mach-O audit,
  including macOS 11.0, system-only dependency, stable install identity,
  required symbol, and zero forbidden strings.
- Core/demo content is rights-separated and every source, logo, demo graphic,
  and font license is classified.
- The packager has deterministic ZIP unit coverage, rejects dirty/unapproved
  inputs, and CI byte-compares two complete package runs.

## Self-review lenses

| Lens | Finding |
| --- | --- |
| Native binaries | PASS structurally on all six binaries; BLOCKED on native macOS runtime. |
| Clean install | PASS for isolated Windows/Linux fixtures; final archive clean-install is pending package assembly. |
| Export isolation | PASS for the exact Linux release library and prior packed PCK; Windows/macOS native exported products remain open. |
| Rights/attribution | PASS for classification and package rules; final archive inventory awaits double packaging. |
| Reproducibility | PASS at ZIP-writer/unit and binary-lock level; complete archive byte comparison is the next local step. |
| Unlensed read | No partial artifact may be labeled a public release candidate under the frozen rules. |

GNT-04 remains blocked by native macOS execution, Windows/macOS export and
interactive editor evidence, and owner publication authorization. The
workflow uploads evidence only and performs no public release.
