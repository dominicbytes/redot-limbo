# Third-party notices

## LimboAI

This downstream is based on LimboAI 1.8.0 by Serhii Snitsaruk and contributors,
upstream commit `3fbd85118b924d50c10a495ad5c7175028649d77`.
The source and core addon are distributed under the MIT-style license in
`LICENSE.md`.

## Redot C++ bindings and build tools

Native addon libraries include statically linked Redot C++ bindings at commit
`598ec78e86b2c240a023f6de13daba70f7de8610`. Their complete MIT copyright and
permission notice is included in `LICENSE_REDOT_CPP.md`. The binding source
checkout, generated API scratch files, and build caches are not included in
the core archive. SCons 4.10.1 is a build tool and is not redistributed in
the addon.

Desktop binary audits check platform system-library dependencies. The core
package excludes MSVC debug runtimes and vendored non-system shared libraries.

## Separate content

The LimboAI logo and demo graphics are copyright Aleksandra Snitsaruk and
licensed CC BY 4.0. They are excluded from the core archive and included only
in the separate demo package with `LOGO_LICENSE.md` and `LICENSE_ASSETS.md`
at its root (`demo/LICENSE_ASSETS.md` in the source checkout).

The demo fonts are separately licensed under SIL OFL 1.1. In the source
checkout, their notices and license text are `demo/THIRD_PARTY_FONTS.md` and
`demo/OFL-1.1.txt`. In the separate demo archive, both files are at its root;
the core archive contains no fonts.
