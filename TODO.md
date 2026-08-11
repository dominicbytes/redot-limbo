# Implementation status

## Completed locally

- [x] Fetch full upstream history and lock exact LimboAI
  `v1.8.0@3fbd85118b924d50c10a495ad5c7175028649d77`.
- [x] Account for all 48 non-merge commits between the v1.6 compatibility
  checkpoint and v1.8; adopt the complete range.
- [x] Reproduce the official Redot 26.2 API and lock Redot C++.
- [x] Replace automatic dependency cloning with a fail-closed build contract.
- [x] Preserve the 1.8 task-palette/favorites/probability/status/debugger work,
  ownership fixes, HSM cargo, and blackboard runtime inspection.
- [x] Add the narrow Redot editor/theme/demo-serialization compatibility
  changes exposed by build and runtime failures.
- [x] Expand the deterministic fixture to 13 cases, including direct checks
  for transition cargo and scoped runtime blackboard inspection.
- [x] Pass Windows and Linux editor/template-release builds and all 13 fixture
  cases with zero suspicious runtime lines.
- [x] Fresh-import, statically check 71 files, and run the complete 1.8 demo in
  Redot without parse, load, runtime, or warning output.
- [x] Cross-build and structurally audit macOS universal editor and
  template-release frameworks.
- [x] Keep pinned native desktop CI and deterministic core/demo packaging
  aligned with version `1.8.0+redot.26.2.1`.
- [x] Classify source, logo, demo graphics, and both font licenses.
- [x] Update compatibility, limitations, migration, baseline-delta, and
  upstream-sync documentation for the adopted 1.8 baseline.

## Remaining in this implementation task

- [ ] Rebuild the six final desktop libraries from the committed v1.8 port so
  embedded version metadata identifies the source commit.
- [ ] Re-run binary audits and Windows/Linux clean-install fixtures using the
  final libraries.
- [ ] Produce the core/demo archives twice from a clean commit and verify
  byte-identical bytes plus file-level rights inventories.
- [ ] Reconcile final platform/archive hashes and verdicts into the reports and
  source-of-truth workbook.
- [ ] Push the completed source branch to `dominicbytes/redot-limbo` and mark
  the repository description as the Redot port.

## Required before a release claim

- [ ] Run the native macOS CI job and retain universal binary/runtime evidence.
- [ ] Complete GNT-03's visible editor, accessibility, debugger, and lifecycle
  session at both UI profiles.
- [ ] Complete the plan's full five-run performance matrix; automated
  200-agent smoke samples do not satisfy that controlled claim.
- [ ] Run and record visible clean-install authoring plus native Windows/macOS
  game exports.
- [ ] Obtain explicit owner authorization before any tag, GitHub release,
  signing, notarization, or distribution-channel publication.
