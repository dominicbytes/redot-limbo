#!/usr/bin/env python
"""
This is SConstruct file for building GDExtension variant using SCons build system.
For module variant, see SCsub file.

Use --project=DIR to customize output path for built targets.
 - Built targets are placed into "DIR/addons/limboai/bin".
 - For example: scons --project="../my_project"
   - built targets will be placed into "../my_project/addons/limboai/bin".
 - If not specified, built targets are put into the demo/ project.
"""

import hashlib
import os
import subprocess
import sys

from limboai_version import generate_module_version_header

sys.path.append("gdextension")
from fix_icon_imports import fix_icon_imports
from update_icon_entries import update_icon_entries

AddOption(
    "--project",
    dest="project",
    type="string",
    nargs=1,
    action="store",
    metavar="DIR",
    default="demo",
    help="Specify project directory",
)

AddOption(
    "--binding-profile",
    dest="binding_profile",
    type="choice",
    choices=("redot", "godot-oracle"),
    nargs=1,
    action="store",
    default="redot",
    help="Select the locked C++ binding contract (default: redot)",
)

help_text = """
Options:
  --project=DIR     Specify project directory (default: "demo");
                    built targets will be placed in DIR/addons/limboai/bin
  --binding-profile=PROFILE
                    Locked binding contract: redot or godot-oracle
"""
Help(help_text)


def read_dependency_lock(name):
    with open("deps.env", "r", encoding="utf-8") as deps_file:
        for line in deps_file:
            if line.startswith(name + "="):
                return line.strip().split("=", 1)[1]
    print("Dependency lock not found in deps.env: " + name)
    Exit(1)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def verify_binding_checkout(profile):
    binding_dir = os.path.abspath("godot-cpp")
    if not os.path.isdir(binding_dir):
        print("Locked binding checkout not found: " + binding_dir)
        print("Populate godot-cpp/ with the exact checkout recorded in deps.env.")
        Exit(1)

    if profile == "redot":
        expected_ref = read_dependency_lock("REDOT_CPP_REF")
        api_path = os.path.join(binding_dir, "gdextension", "extension_api.json")
        expected_api = read_dependency_lock("REDOT_EXTENSION_API_SHA256")
        interface_path = os.path.join(binding_dir, "gdextension", "gdextension_interface.h")
        expected_interface = read_dependency_lock("REDOT_GDEXTENSION_INTERFACE_SHA256")
    else:
        expected_ref = read_dependency_lock("GODOT_CPP_ORACLE_REF")
        api_version = read_dependency_lock("GODOT_CPP_ORACLE_API_VERSION")
        if ARGUMENTS.get("api_version") != api_version:
            print("godot-oracle requires api_version=" + api_version)
            Exit(1)
        api_path = os.path.join(binding_dir, "gdextension", "extension_api-4-4.json")
        expected_api = read_dependency_lock("GODOT_CPP_ORACLE_API_SHA256")
        interface_path = None
        expected_interface = None

    result = subprocess.run(
        [
            "git", "-c", "safe.directory=" + binding_dir, "-C", binding_dir,
            "rev-parse", "HEAD",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    actual_ref = result.stdout.strip()
    if result.returncode != 0 or actual_ref != expected_ref:
        print("Binding commit mismatch: expected " + expected_ref + ", got " + actual_ref)
        Exit(1)

    actual_api = sha256_file(api_path)
    if actual_api != expected_api:
        print("Binding API mismatch: expected " + expected_api + ", got " + actual_api)
        Exit(1)

    if interface_path is not None:
        actual_interface = sha256_file(interface_path)
        if actual_interface != expected_interface:
            print("GDExtension interface mismatch: expected " + expected_interface + ", got " + actual_interface)
            Exit(1)

    print("Verified locked " + profile + " binding: " + actual_ref)


binding_profile = GetOption("binding_profile")
verify_binding_checkout(binding_profile)

project_dir = GetOption("project")
if not os.path.isdir(project_dir):
    print("Project directory not found: " + project_dir)
    Exit(2)

# Parse LimboAI-specific variables.
vars = Variables()
vars.AddVariables(
    BoolVariable("deploy_manifest", help="Deploy limboai.gdextension into PROJECT/addons/limboai/bin", default=True),
    BoolVariable("deploy_icons", help="Deploy icons into PROJECT/addons/limboai/icons", default=True),
)
env = Environment(tools=["default"], PLATFORM="", variables=vars)
Help(vars.GenerateHelpText(env))

# Read LimboAI-specific variables.
deploy_manifest = env["deploy_manifest"]
deploy_icons = env["deploy_icons"]

# Remove processed variables from ARGUMENTS to avoid godot-cpp warnings.
for o in vars.options:
    if o.key in ARGUMENTS:
        del ARGUMENTS[o.key]

# For reference:
# - CCFLAGS are compilation flags shared between C and C++
# - CFLAGS are for C-specific compilation flags
# - CXXFLAGS are for C++-specific compilation flags
# - CPPFLAGS are for pre-processor flags
# - CPPDEFINES are for pre-processor defines
# - LINKFLAGS are for linking flags

env = SConscript("godot-cpp/SConstruct")

# Error macros embed __FILE__. Keep Windows release artifacts independent of the
# checkout location while preserving paths relative to this source root.
if env["platform"] == "windows":
    env.Append(CCFLAGS=["/d1trimfile:" + os.path.abspath(".")])

# Generate version header.
print("Generating LimboAI version header...")
generate_module_version_header()

# Update icon entries in limboai.gdextension file.
# Note: This will remove everything after [icons] section, and rebuild it with generated icon entries.
print("Updating LimboAI icon entries...")
update_icon_entries(silent=True)

# Fix icon imports in the PROJECT/addons/limboai/icons/.
# Enables scaling and color conversion in the editor for imported SVG icons.
try:
    fix_icon_imports(project_dir)
except FileNotFoundError as e:
    print(e)
except Exception as e:
    print("Unknown error: " + str(e))

# Tweak this if you want to use different folders, or more folders, to store your source code in.
env.Append(CPPDEFINES=["LIMBOAI_GDEXTENSION"])
sources = Glob("*.cpp")
sources += Glob("blackboard/*.cpp")
sources += Glob("blackboard/bb_param/*.cpp")
sources += Glob("bt/*.cpp")
sources += Glob("bt/tasks/*.cpp")
sources += Glob("bt/tasks/blackboard/*.cpp")
sources += Glob("bt/tasks/composites/*.cpp")
sources += Glob("bt/tasks/decorators/*.cpp")
sources += Glob("bt/tasks/scene/*.cpp")
sources += Glob("bt/tasks/utility/*.cpp")
sources += Glob("compat/*.cpp")
sources += Glob("editor/debugger/*.cpp")
sources += Glob("editor/*.cpp")
sources += Glob("gdextension/*.cpp")
sources += Glob("hsm/*.cpp")
sources += Glob("util/*.cpp")

# Generate documentation header.
if env["target"] in ["editor", "template_debug"]:
    doc_data = env.GodotCPPDocData("gen/doc_data.gen.cpp", source=Glob("doc_classes/*.xml"))
    sources.append(doc_data)

# Build library.
if env["platform"] == "macos":
    macos_library_name = "liblimboai.{}.{}".format(env["platform"], env["target"])
    # Apple's linker otherwise records the absolute build output as LC_ID_DYLIB,
    # leaking the checkout path and making otherwise identical packages differ.
    env.Append(LINKFLAGS=["-Wl,-install_name,@rpath/" + macos_library_name])
    library = env.SharedLibrary(
        project_dir
        + "/addons/limboai/bin/{}.framework/{}".format(macos_library_name, macos_library_name),
        source=sources,
    )
else:
    library = env.SharedLibrary(
        project_dir + "/addons/limboai/bin/liblimboai{}{}".format(env["suffix"], env["SHLIBSUFFIX"]),
        source=sources,
    )

Default(library)

# Deploy icons into PROJECT/addons/limboai/icons.
if deploy_icons:
    cmd_deploy_icons = env.Command(
        project_dir + "/addons/limboai/icons/",
        "icons/",
        Copy("$TARGET", "$SOURCE"),
    )
    Default(cmd_deploy_icons)

# Deploy limboai.gdextension into PROJECT/addons/limboai/bin.
if deploy_manifest:
    cmd_deploy_manifest = env.Command(
        project_dir + "/addons/limboai/bin/limboai.gdextension",
        "gdextension/limboai.gdextension",
        Copy("$TARGET", "$SOURCE"),
    )
    Default(cmd_deploy_manifest)
