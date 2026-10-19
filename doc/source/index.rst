LimboAI Documentation
=====================

**Redot LimboAI** is a desktop GDExtension port of the **LimboAI 1.8.0**
source baseline for **Redot 26.2**, combining **Behavior Trees** and
**State Machines** with an editor and visual debugger. Use typed GDScript for
:ref:`creating your own tasks <custom_tasks>` and states. Start with
:doc:`getting-started/getting-limboai` for the pinned installation contract.
The API tutorials remain applicable; upstream Godot engine-module, AssetLib,
and .NET instructions do not describe supported installation routes for this fork.

.. SCREENSHOT

**Behavior Trees** are powerful hierarchical structures used to model and control the behavior
of agents in a game (e.g., characters, enemies, entities). They are designed to
make it easier to create complex and highly modular behaviors for your games.
To learn more about behavior trees, check out :ref:`introduction`.

**Hierarchical State Machines** are finite state machines that allow any state to host their own
sub-state machine. This allows you to tackle your AI's state and transition complexity by breaking down
one big state machine into multiple smaller ones.

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Getting started

   getting-started/getting-limboai
   getting-started/contributing

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Behavior Trees

   behavior-trees/introduction
   behavior-trees/create-tree
   behavior-trees/custom-tasks
   behavior-trees/using-blackboard
   behavior-trees/accessing-nodes

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Hierarchical State MachineS

   hierarchical-state-machines/create-hsm

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Class reference
   :glob:

   classes/featured-classes
   classes/class_*
