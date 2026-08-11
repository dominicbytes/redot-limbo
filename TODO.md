# Implementation status

## Completed locally

- [x] Fetch full upstream history and select/pin LimboAI 1.6.0.
- [x] Build and run the unchanged 1.6.0 Godot oracle and unchanged Redot probe.
- [x] Reproduce the official Redot 26.2 API and lock Redot C++.
- [x] Replace automatic dependency cloning with a fail-closed build contract.
- [x] Backport the isolated accepted fixes and exclude the 4.6-only lifecycle
  backport whose triggering engine change is absent from Redot's 4.5 lineage.
- [x] Implement typed-GDScript BT, blackboard, resource, multi-agent, HSM,
  custom-task, runtime-view, and performance fixtures.
- [x] Match Godot and Redot normalized fixture semantics.
- [x] Build, audit, and run Windows editor/template-release libraries.
- [x] Build and audit Linux editor/template-release libraries and run the exact
  release library in a packed exported-runtime fixture.
- [x] Cross-build and structurally audit macOS universal editor and
  template-release frameworks with stable install identities.
- [x] Implement pinned native desktop CI and deterministic core/demo packaging.
- [x] Classify source, logo, demo graphics, and both font licenses.
- [x] Write compatibility, limitations, migration, notices, and package docs.

## Required before a release claim

- [ ] Run the native macOS CI job and retain universal binary/runtime evidence.
- [ ] Complete GNT-03's visible editor, accessibility, debugger, and lifecycle
  session at both UI profiles.
- [ ] Complete the plan's full five-run performance/oracle matrix; four final
  200-agent smoke samples pass but do not satisfy that claim.
- [ ] Run deterministic packaging twice from a clean, committed source after
  all three platform jobs pass.
- [ ] Run and record clean-install authoring plus native Windows/macOS game
  exports; Linux packed runtime evidence already passes.
- [ ] Reconcile final archive hashes into the source-of-truth workbook after
  the clean double-package run; platform hashes and verdicts are current.
- [ ] Obtain explicit owner authorization before any push, tag, public release,
  signing, or notarization action.
