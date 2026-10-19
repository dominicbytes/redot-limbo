Getting LimboAI
===============

This fork ports the LimboAI 1.8.0 source baseline to Redot 26.2 as a
single-precision desktop GDExtension. Engine-module builds, C#/.NET, mobile,
and Web are outside its supported scope. See the source checkout's
``COMPATIBILITY.md``, ``LIMITATIONS.md``, and ``UPSTREAM_LOCK.md`` for exact
inputs, build targets, and validation boundaries.

Upstream Godot binaries and Asset Library packages are not Redot builds.

Get GDExtension version
------------------------

Use the core archive assembled from this fork by ``scripts/package_release.py``,
or build from the pinned source inputs as described in :doc:`contributing`.
A source version or CI artifact does not establish a published binary release.

GDExtension is the most convenient way of using the LimboAI plugin, but it comes
with certain limitations:

* Documentation tooltips are not available.
* Handy :ref:`class_BBParam` property editor is not available in the extension due to dependencies on the engine classes that are not available in the locked GDExtension API.

    **🛈 See also:** `What is GDExtension? <https://docs.godotengine.org/en/stable/tutorials/scripting/gdextension/what_is_gdextension.html#what-is-gdextension>`_

Installation instructions:

1. Use Redot ``26.2.stable.official.4f5b14aba`` and the matching core archive.
2. Extract ``addons/limboai`` into your project root before opening the editor.
3. Open the project and allow import to finish. Resolve native-load, parse, or resource errors before proceeding.
4. For the optional demo, install the matching-version core into the separate demo project and retain its CC BY 4.0 and OFL notices.
5. Run ``demo/scenes/showcase.tscn`` in that demo project.

Read the core package's ``MIGRATION.md`` before replacing an existing installation.

Upstream-only module edition
----------------------------

Upstream LimboAI also offers a Godot engine-module edition with custom editors
and export templates. Those Godot builds are outside this Redot fork's support
contract and must not replace the Redot GDExtension installation above.
