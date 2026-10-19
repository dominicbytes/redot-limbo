# Locked binding patch

`redot-cpp-variant-forward-compat.patch` applies to redot-cpp commit
`598ec78e86b2c240a023f6de13daba70f7de8610`. Apply it with
`python scripts/prepare_binding.py --apply`; SCons verifies it again before
and after resolving effective API/interface inputs. Hashes are in `deps.env`.

`Variant::clear()` previously indexed a 39-entry table with a runtime type,
including Struct (39) on Redot 26.3. Unknown types now go directly to the engine
destructor, matching the existing Variant destructor ownership contract. The
missing PackedVector4Array entry is explicitly true so overwrite/clear releases
its backing buffer on both engines.

The remaining binding type-indexed tables were inspected: `from_type_constructor`
and `to_type_constructor` use compile-time destination types; VariantInternal's
getter table uses template type constants. Their initialization loops are bounded
by the compiled enum. Generated builtin constructor/operator caches likewise
use known compiled types. Copy construction calls engine `variant_new_copy`;
copy assignment calls the corrected `clear()` before engine copying; move
construction/assignment swap opaque storage. Destruction calls the engine.
Evaluation, type names, conversions, hashing, duplication, and property/index
access delegate to engine interface functions. None indexes these binding tables
with the incoming Variant type. No extra binding changes are justified by this
audit, and no enum maximum, API hash, interface hash, or binding revision changes.
