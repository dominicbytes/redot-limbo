"""Scan release bytes and redact private locations from retained evidence."""

from __future__ import annotations

import argparse
import gzip
import io
from pathlib import Path
import re
import sys
import tarfile
import zipfile


PATH_PATTERNS = (
    ("drive-root", re.compile(r"(?<!\w)[A-Za-z]:[\\/][^\r\n\x00\"<>|]*")),
    ("network-root", re.compile(r"(?<![:\w/\\])(?:\\\\|//)[^\\/\s\x00]+[\\/][^\r\n\x00\"<>|]+")),
    ("rooted-path", re.compile(r"(?<![\w\x3a/\\.])/(?:[^/\s\x00\"'<>|:]+/)+[^\s\x00\"'<>|:]*")),
    ("home-or-mount-root", re.compile(r"(?<![\w\x3a/\\.])/(?:home|Users|mnt|media|Volumes|workspace|workspaces|tmp)(?=[/\s\x00\"']|$)(?:/[^\r\n\x00\"'<>|]*)?", re.I)),
)
CONTENT_PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----")),
    ("credential", re.compile(r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]+")),
    ("fixture-evidence", re.compile(r"LIMBOAI_FIXTURE|fixture-result\.json")),
    ("internal-notes", re.compile(r"(?:docs[/\\](?:gamedev|softwaredev)|reports[/\\]test-results)[/\\]", re.I)),
)
MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_ARCHIVE_DEPTH = 8


def system_path(value: str) -> bool:
    return value.startswith(("/usr/lib/", "/System/Library/"))


def sanitize_text(value: str, replacements=()) -> str:
    for original, replacement in sorted(replacements, key=lambda pair: len(pair[0]), reverse=True):
        for spelling in (original, original.replace("\\", "/"), original.replace("\\", "\\\\")):
            if spelling:
                value = value.replace(spelling, replacement)
    for _category, pattern in PATH_PATTERNS:
        value = pattern.sub(lambda match: match[0] if system_path(match[0]) else "<private path>", value)
    return value


def sanitize(value, replacements=()):
    if isinstance(value, str):
        return sanitize_text(value, replacements)
    if isinstance(value, list):
        return [sanitize(item, replacements) for item in value]
    if isinstance(value, dict):
        return {sanitize_text(str(key), replacements): sanitize(item, replacements) for key, item in value.items()}
    return value


def display_path(path: Path, root: Path | None = None) -> str:
    root = root or Path(__file__).resolve().parents[1]
    try:
        name = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        name = "<external>/" + path.name
    return sanitize_text(name)


def text_categories(text: str) -> set[str]:
    categories = set()
    for category, pattern in PATH_PATTERNS:
        if any(not system_path(match[0]) for match in pattern.finditer(text)):
            categories.add(category)
    for category, pattern in CONTENT_PATTERNS:
        if pattern.search(text):
            categories.add(category)
    return categories


def scan_blob(name: str, data: bytes, depth: int = 0) -> list[tuple[str, str]]:
    safe_name = sanitize_text(name)
    categories = text_categories(name)
    decoded = data.decode("utf-8", errors="replace")
    for match in re.finditer(r"[^\x00-\x1f\x7f-\x9f\ufffd]{4,}", decoded):
        categories.update(text_categories(match[0]))
    for pattern, encoding in ((rb"(?:[\x20-\x7e]\x00){3,}", "utf-16le"),
                              (rb"(?:\x00[\x20-\x7e]){3,}", "utf-16be")):
        for match in re.finditer(pattern, data):
            categories.update(text_categories(match[0].decode(encoding)))
    hits = [(safe_name, category) for category in sorted(categories)]
    is_zip = data.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"))
    is_gzip = data.startswith(b"\x1f\x8b")
    is_tar = data[257:262] == b"ustar"
    if not (is_zip or is_gzip or is_tar):
        return hits
    if depth >= MAX_ARCHIVE_DEPTH or len(data) > MAX_ARCHIVE_BYTES:
        return hits + [(safe_name, "archive-limit")]
    try:
        if is_zip:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                if sum(item.file_size for item in archive.infolist()) > MAX_ARCHIVE_BYTES:
                    return hits + [(safe_name, "archive-limit")]
                for item in archive.infolist():
                    hits.extend(scan_blob(name + "!" + item.filename, archive.read(item), depth + 1))
        elif is_gzip:
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as archive:
                unpacked = archive.read(MAX_ARCHIVE_BYTES + 1)
            if len(unpacked) > MAX_ARCHIVE_BYTES:
                return hits + [(safe_name, "archive-limit")]
            hits.extend(scan_blob(name + "!<gzip member>", unpacked, depth + 1))
        else:
            with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                members = archive.getmembers()
                if sum(item.size for item in members) > MAX_ARCHIVE_BYTES:
                    return hits + [(safe_name, "archive-limit")]
                for item in members:
                    handle = archive.extractfile(item) if item.isfile() else None
                    hits.extend(scan_blob(name + "!" + item.name, handle.read() if handle else b"", depth + 1))
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, tarfile.TarError):
        hits.append((safe_name, "invalid-archive"))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", type=Path, nargs="*")
    parser.add_argument("--evidence", action="store_true")
    parser.add_argument("--sanitize-stdin", action="store_true")
    args = parser.parse_args()
    if args.sanitize_stdin:
        print(sanitize_text(sys.stdin.read()), end="")
        return 0
    failed = False
    import glob
    paths = [Path(match) for path in args.paths for match in (glob.glob(str(path)) or [str(path)])]
    for path in paths:
        files = sorted(item for item in path.rglob("*") if item.is_file()) if path.is_dir() else [path]
        for item in files:
            name = display_path(item)
            try:
                hits = scan_blob(name, item.read_bytes())
            except OSError:
                hits = [(name, "unreadable-file")]
            if args.evidence:
                hits = [hit for hit in hits if hit[1] != "fixture-evidence"]
            for file, category in hits:
                print(f"FAIL {file}: {category}", file=sys.stderr)
            failed = failed or bool(hits)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
