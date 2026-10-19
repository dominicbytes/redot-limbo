.. _contributing:

Contributing
============

This fork targets the LimboAI 1.8.0 baseline on Redot
``26.2.stable.official.4f5b14aba``, single precision, as a desktop GDExtension.
Use the exact engine, binding commit, API, and interface hashes in the source
checkout's ``UPSTREAM_LOCK.md`` and ``deps.env``. A matching Godot API-lineage
version alone is not sufficient.

We follow the `Godot code style guidelines <https://docs.godotengine.org/en/stable/contributing/development/code_style_guidelines.html#doc-code-style-guidelines>`_.
Please use ``clang-format`` to maintain consistent styling. You can install
``pre-commit`` hooks for Git using ``pre-commit install`` to automate this process.

Please keep the minor versions backward-compatible when submitting pull requests.

The downstream desktop CI builds and audits GDExtension editor and
template-release libraries, runs headless fixtures on built addons, and compares
assembled package bytes. It does not validate extracted installations, visible
editor behavior, or native game exports. The inherited module/.NET material
below describes upstream Godot only; those configurations are not supported
Redot build targets.

Upstream-only Godot module build
--------------------------------

1. Clone the Godot Engine repository.
2. Switch to the latest stable tag.
3. Clone the LimboAI repository into the ``modules/limboai`` directory.

.. code-block:: bash

   git clone https://github.com/godotengine/godot.git
   git checkout 4.3-stable  # Replace "4.3-stable" with the latest stable tag
   git clone https://github.com/limbonaut/limboai modules/limboai

Consult the `Godot Engine documentation <https://docs.godotengine.org/en/stable/engine_details/development/compiling/index.html>`_
for detailed instructions on building the engine.

**Unit tests** can be compiled using the ``tests=yes`` build option. To execute them,
run the compiled Godot binary with the ``--test --tc="*[LimboAI]*"`` command-line options.

Upstream-only C# packages
~~~~~~~~~~~~~~~~~~~~~~~~

If you want C# Support for LimboAI when building from source, follow Godot's instructions for building from source with
C# Support: `Compiling with .NET <https://docs.godotengine.org/en/stable/engine_details/development/compiling/compiling_with_dotnet.html>`_.
LimboAI's classes will be included in the output from that build process.

Compiling as GDExtension library
--------------------------------

Use SCons 4.10.1 and a platform C++ compiler. Populate ``godot-cpp/`` with the
exact Redot C++ commit in ``deps.env`` before building; SCons does not clone it.
Generate ``extension_api.json`` from the locked Redot editor, verify its hash,
and copy it to ``godot-cpp/gdextension/extension_api.json``. Verify the binding's
``gdextension/gdextension_interface.h`` hash too. ``SConstruct`` rejects a
mismatched binding commit, API, interface, or build profile.

Create an external output project directory, then build both profiles:

.. code-block:: text

   scons --project=<external-project> platform=<windows|linux|macos> target=editor
   scons --project=<external-project> platform=<windows|linux|macos> target=template_release

Use ``arch=x86_64`` on Windows/Linux or
``arch=universal macos_deployment_target=11.0`` on a native macOS builder.
Libraries are placed under the output project's ``addons/limboai/bin/``.
See the source ``README.md`` for the build contract and run the Python harness
tests with ``python -I -m unittest discover -s tests -p "test_*.py" -v``.
The inherited module-only C++ tests are not the GDExtension fixture runner.

Contributing to the documentation
---------------------------------

Online documentation is created using `Sphinx <https://www.sphinx-doc.org/en/master/>`_.
Source files are located in the ``doc/source`` directory in RST format and can
be built locally with ``sphinx-build``. See the
`Sphinx documentation <https://www.sphinx-doc.org/en/master/tutorial/getting-started.html>`_
for more details.

Class documentation resides in XML files within the ``doc_classes/`` directory.
The following engine ``--doctool`` procedure is upstream-only module tooling;
it is not a Redot GDExtension build requirement.
If you create a new class or modify an existing one, you can run the compiled
Godot binary with the ``--doctool`` option in the root of the Godot source code
to generate the missing XML files or sections within those files in the class documentation.
After editing the XML files, please run the compiled editor binary with the ``--doctool``
option again to update and tidy up the XML files.

Sphinx RST files for the class documentation are generated from
XML files using the Godot script ``make_rst.py`` and stored in the ``doc/source/classes`` directory.
This process is performed using our own script ``scripts/update_rst.sh``. RST files
in ``doc/source/classes`` should not be edited manually.
