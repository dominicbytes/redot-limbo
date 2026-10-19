:orphan:

.. _csharp:

Using LimboAI with C#
=====================

C#/.NET is not supported by this Redot GDExtension fork. Use typed GDScript
for custom tasks and states. The instructions below are retained solely as
upstream Godot module reference; this fork ships no NuGet or GodotSharp packages.

1. Locate LimboAI NuGet package files.

Upstream .NET module builds provide a GodotSharp folder with packages under
"GodotSharp/Tools/nupkgs/". Note down the directory path; you'll need it in the next step.

2. Add a local source for NuGet packages using the following command:

.. code:: shell

    dotnet nuget add source path/to/limboai/nupkgs --name LimboNugetSource

3. Your C# project should be able to see LimboAI classes and compile.

These upstream module steps do not enable C# support in this fork's
GDExtension libraries.
