# Third-party notices

## LimboAI

This downstream is based on LimboAI 1.6.0 by Serhii Snitsaruk and contributors,
upstream commit `91b22a187f7cd701e25eedd6dcff34179795e687`.
The source and core addon are distributed under the MIT-style license in
`LICENSE.md`.

## Build-only dependencies

Redot C++ bindings at commit
`598ec78e86b2c240a023f6de13daba70f7de8610` and SCons 4.10.1 are pinned
build inputs. Their source trees, generated API scratch files, and build caches
are not included in the core archive.

Desktop binaries use only the platform system libraries permitted by the
binary-audit reports. No MSVC debug runtime or vendored non-system shared
library is approved for distribution.

## Separate content

The LimboAI logo and demo graphics are copyright Aleksandra Snitsaruk and
licensed CC BY 4.0. They are excluded from the core archive and included only
in the separate demo package with `LOGO_LICENSE.md` and
`demo/LICENSE_ASSETS.md`.

The demo fonts are separately licensed under SIL OFL 1.1. Their notices and
license text are in `demo/THIRD_PARTY_FONTS.md` and `demo/OFL-1.1.txt`.
