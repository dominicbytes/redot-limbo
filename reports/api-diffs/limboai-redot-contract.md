# LimboAI / Redot 26.2 contract

Date: 2026-08-10
Verdict: PASS for API/build/load contract; interactive editor parity is a
separate gate.

## Accepted inputs

- Redot: `26.2.stable.official.4f5b14aba`, single precision, engine commit
  `4f5b14abade2239104847d03d8f9056e4467cfcd`.
- Official engine-generated API SHA-256:
  `177E7796166929B2193C9CCE2FD32F59601A0147D0D1E7FE904B94E8F69F6577`.
- Redot C++ commit:
  `598ec78e86b2c240a023f6de13daba70f7de8610`.
- Binding interface SHA-256:
  `4CD695E86B92E2BF4E60BBE19CE137FAF41205DA1CF94F29E069AFEC0F7BF320`.

Two independent clean official dumps matched. The binding's source-backed API
has SHA-256
`453A0CC128BB58333A001F7F43573A5961D973FB7B151AF43139869F22D5915C`.
A recursive comparison found identical counts and names for 38 builtin
classes, 993 classes, 22 global-enum groups, 14 native structures, 39
singletons, and 125 utility functions. `changedClassCount` is zero. The four
deep differences are only official/custom values in `version_build` and
`version_full_name` fields.

## Build contract

`SConstruct`:

- requires a pre-populated binding checkout;
- verifies its exact Git commit;
- verifies the selected API and interface hashes;
- separates the Redot and Godot-oracle profiles;
- places binaries into an explicit external project;
- uses `/d1trimfile` on Windows so `__FILE__` does not disclose a checkout
  path; and
- fails when the wrong profile or API is supplied.

The deliberate wrong-profile probe exited nonzero. No fallback clone or
network lookup occurred.

## Load and semantic result

The unchanged v1.6.0 source built and loaded with the Redot binding before any
source backport. The final fixture registers the runtime and editor classes and
passes eleven named cases. Its normalized Godot 4.5.2 versus Redot 26.2
comparison contains zero differences.

The accepted API requires no downstream runtime compatibility shim. The only
API-version guard exposes the three upstream 4.5 plan-editor hints while
preserving compilation against the 4.4 Godot oracle. Other engine-facing
changes are build/version controls or isolated upstream bug-fix backports.

Evidence is stored outside the source repository under
`plugins/build/redot-limboai/tooling/redot-api-comparison.json`, build logs,
and fixture-run JSON.
