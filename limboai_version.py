# Edit the following variables to change version info

major = 1
minor = 8
patch = 0
status = ""
downstream = "redot.26.2.1"
doc_branch = "v1.8.0"

# *** Code that generates version header


def _git_hash(short: bool = False):
    import os
    import subprocess

    ret = "unknown"
    try:
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        if short:
            cmd = [
                "git", "-c", f"safe.directory={repo_dir}", "-C", repo_dir,
                "rev-parse", "--short", "HEAD"
            ]
        else:
            cmd = [
                "git", "-c", f"safe.directory={repo_dir}", "-C", repo_dir,
                "rev-parse", "HEAD"
            ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        ret = proc.communicate()[0].strip().decode("utf-8")
    except:
        pass
    return ret


def _get_version_info():
    return {
        "major": major,
        "minor": minor,
        "patch": patch,
        "status": status,
        "downstream": downstream,
        "doc_branch": doc_branch,
        "git_short_hash": _git_hash(short=True),
        "git_hash": _git_hash(short=False),
    }


def generate_module_version_header():
    version_info = _get_version_info()
    f = open("util/limboai_version.gen.h", "w")
    f.write(
        """/* THIS FILE IS GENERATED DO NOT EDIT */
#ifndef LIMBOAI_VERSION_GEN_H
#define LIMBOAI_VERSION_GEN_H

#define LIMBOAI_VERSION_MAJOR {major}
#define LIMBOAI_VERSION_MINOR {minor}
#define LIMBOAI_VERSION_PATCH {patch}
#define LIMBOAI_VERSION_STATUS "{status}"
#define LIMBOAI_VERSION_DOWNSTREAM "{downstream}"

#define LIMBOAI_VERSION_HASH "{git_hash}"
#define LIMBOAI_VERSION_SHORT_HASH "{git_short_hash}"

#define LIMBOAI_VERSION_DOC_BRANCH "{doc_branch}"
#define LIMBOAI_VERSION_DOC_URL "https://limboai.readthedocs.io/en/" LIMBOAI_VERSION_DOC_BRANCH "/"

#endif // LIMBOAI_VERSION_GEN_H
""".format(**version_info)
    )
    f.close()
