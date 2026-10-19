"""Scan release bytes and redact private locations from retained evidence."""

from __future__ import annotations

import argparse
import base64
import binascii
import gzip
import io
from pathlib import Path
import re
import sys
import tarfile
import zipfile
import zlib


# Unquoted command paths end at whitespace; quotes and diagnostic locations
# supply the context needed to retain spaces inside a path value.
PATH_PATTERNS = (
    ("drive-root", re.compile(r"(?<!\w)[A-Za-z]:[\\/][^\s\x00\"'<>|(),;:]*")),
    ("network-root", re.compile(r"(?<![:\w/\\])(?:\\\\|//)[^\\/\s\x00]+[\\/](?![\\/])[^\s\x00\"'<>|(),;:]+")),
    ("rooted-path", re.compile(r"(?<![\w\x3a/\\.])/(?!\.{1,2}/)(?:[\w.~@%+$-]+/)+[\w.~@%+$-]+")),
    ("home-or-mount-root", re.compile(r"(?<![\w\x3a/\\.])/(?:home|Users|mnt|media|Volumes|workspace|workspaces|tmp)(?=[/\s\x00\"']|$)(?:/[^\s\x00\"'<>|(),;:]*)?", re.I)),
)
ABSOLUTE_START = r"(?:[A-Za-z]:[\\/]|/(?!/)|\\\\|//)"
QUOTED_PATH = re.compile(r"(?P<quote>[\"'])(?P<path>" + ABSOLUTE_START + r"[^\r\n\x00]*?)(?P=quote)")
DIAGNOSTIC_PATH = re.compile(
    r"(?<![\w\x3a/\\])(?P<path>" + ABSOLUTE_START + r"[^\r\n\x00\"'<>|]*?)"
    r"(?=\(\d+(?:,\d+)?\):|:\d+(?::\d+)?:)"
)
COMPILER_PATH = re.compile(
    r"(?<!\w)(?:-isystem|-iquote|-I|-L|/I|/Fo|/Fd|-Wl,-rpath,|--sysroot=|@)"
    r"(?P<quote>[\"'])?(?P<path>" + ABSOLUTE_START
    + r"(?(quote)[^\r\n\x00]*?|[^\s\x00\"'<>|(),;:]*))(?(quote)(?P=quote))"
)


def path_spans(text: str):
    compiler = list(COMPILER_PATH.finditer(text))
    for match in compiler:
        yield match.start("path"), match.end("path"), "compiler-path"
    patterns = (("rooted-path", QUOTED_PATH), ("rooted-path", DIAGNOSTIC_PATH), *PATH_PATTERNS)
    for category, pattern in patterns:
        for match in pattern.finditer(text):
            if any(match.start() < option.end() and match.end() > option.start() for option in compiler):
                continue
            group = "path" if pattern in (QUOTED_PATH, DIAGNOSTIC_PATH) else 0
            yield match.start(group), match.end(group), category


CONTENT_PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----")),
    ("credential", re.compile(r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]+")),
    ("fixture-evidence", re.compile(r"LIMBOAI_FIXTURE|fixture-result\.json")),
    ("internal-notes", re.compile(r"(?:docs[/\\](?:gamedev|softwaredev)|reports[/\\]test-results)[/\\]", re.I)),
)
MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_ARCHIVE_DEPTH = 8


def system_path(value: str) -> bool:
    return value.startswith(("/usr/lib/", "/System/Library/", "/dev/"))


def sanitize_text(value: str, replacements=()) -> str:
    for original, replacement in sorted(replacements, key=lambda pair: len(pair[0]), reverse=True):
        for spelling in (original, original.replace("\\", "/"), original.replace("\\", "\\\\")):
            if spelling:
                value = value.replace(spelling, replacement)
    spans = sorted((start, end) for start, end, category in path_spans(value)
                   if category == "compiler-path" or not system_path(value[start:end]))
    # Merge overlapping recognizers so a quoted or diagnostic path is replaced
    # once, with its quotes, line numbers and following message left intact.
    merged = []
    for start, end in spans:
        if merged and start < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    for start, end in reversed(merged):
        value = value[:start] + "<private path>" + value[end:]
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


def text_categories(text: str, minimum_path: int = 0) -> set[str]:
    categories = set()
    for start, end, category in path_spans(text):
        # Short slash fragments also occur by chance in compressed image data.
        if end - start >= minimum_path and (category == "compiler-path" or not system_path(text[start:end])):
            categories.add(category)
    for category, pattern in CONTENT_PATTERNS:
        if pattern.search(text):
            categories.add(category)
    return categories


def scan_blob(name: str, data: bytes, depth: int = 0) -> list[tuple[str, str]]:
    safe_name = sanitize_text(name)
    for category, pattern in CONTENT_PATTERNS:
        if category in ("private-key", "credential"):
            safe_name = pattern.sub("<private content>", safe_name)
    categories = text_categories(name)
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        if depth >= MAX_ARCHIVE_DEPTH:
            return [(safe_name, "archive-limit")]
        hits = [(safe_name, category) for category in sorted(categories)]
        cursor = 8
        try:
            while cursor < len(data):
                if cursor + 12 > len(data):
                    raise ValueError("truncated image chunk")
                size = int.from_bytes(data[cursor:cursor + 4], "big")
                kind = data[cursor + 4:cursor + 8]
                if cursor + 12 + size > len(data):
                    raise ValueError("truncated image metadata")
                payload = data[cursor + 8:cursor + 8 + size]
                # Pixel data is not text; inspect metadata and trailing bytes.
                compressed = False
                if kind in (b"zTXt", b"iCCP"):
                    keyword, payload = payload.split(b"\0", 1)
                    hits.extend(scan_blob(name + "!<keyword>", keyword, depth + 1))
                    if payload[0] != 0:
                        raise ValueError("unknown metadata compression")
                    payload, compressed = payload[1:], True
                elif kind == b"iTXt":
                    keyword, fields = payload.split(b"\0", 1)
                    flag, method = fields[:2]
                    language, translated, payload = fields[2:].split(b"\0", 2)
                    hits.extend(scan_blob(name + "!<text fields>", keyword + b"\0" + language + b"\0" + translated, depth + 1))
                    if flag not in (0, 1) or method != 0:
                        raise ValueError("unknown text compression")
                    compressed = flag == 1
                if compressed:
                    decoder = zlib.decompressobj()
                    payload = decoder.decompress(payload, MAX_ARCHIVE_BYTES + 1)
                    if len(payload) > MAX_ARCHIVE_BYTES or not decoder.eof:
                        raise ValueError("invalid compressed metadata")
                if kind in (b"tEXt", b"zTXt", b"iTXt", b"iCCP", b"eXIf"):
                    hits.extend(scan_blob(name + "!" + kind.decode("ascii"), payload, depth + 1))
                cursor += size + 12
                if kind == b"IEND":
                    hits.extend(scan_blob(name + "!<trailing bytes>", data[cursor:], depth + 1))
                    return hits
            raise ValueError("missing image end")
        except (ValueError, IndexError, zlib.error):
            return hits + [(safe_name, "invalid-image-metadata")]
    is_zip = data.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"))
    is_gzip = data.startswith(b"\x1f\x8b")
    is_tar = data[257:262] == b"ustar"
    container = is_zip or is_gzip or is_tar
    embedded_hits = []
    decoded = "" if container else data.decode("utf-8", errors="replace")
    def embedded(match):
        if depth >= MAX_ARCHIVE_DEPTH:
            embedded_hits.append((safe_name, "archive-limit"))
        else:
            try:
                payload = base64.b64decode(re.sub(r"\s", "", match[1]), validate=True)
                embedded_hits.extend(scan_blob(name + "!<embedded data>", payload, depth + 1))
            except (ValueError, binascii.Error):
                embedded_hits.append((safe_name, "invalid-embedded-data"))
        return "<embedded data>"
    decoded = re.sub(r"data:[\w.+/-]+;base64,([A-Za-z0-9+/=\s]+)", embedded, decoded)
    textual_payload = all(character.isprintable() or character in "\n\r\t" for character in decoded) and "\ufffd" not in decoded
    for match in re.finditer(r"[^\x00-\x1f\x7f-\x9f\ufffd]{4,}", decoded):
        categories.update(text_categories(match[0], 0 if textual_payload else 8))
    for pattern, encoding in ((rb"(?:[\x20-\x7e]\x00){3,}", "utf-16le"),
                              (rb"(?:\x00[\x20-\x7e]){3,}", "utf-16be")):
        for match in re.finditer(pattern, b"" if container else data):
            categories.update(text_categories(match[0].decode(encoding)))
    hits = [(safe_name, category) for category in sorted(categories)] + embedded_hits
    if not (is_zip or is_gzip or is_tar):
        return hits
    if depth >= MAX_ARCHIVE_DEPTH or len(data) > MAX_ARCHIVE_BYTES:
        return hits + [(safe_name, "archive-limit")]
    try:
        if is_zip:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                hits.extend(scan_blob(name + "!<archive comment>", archive.comment, depth + 1))
                if sum(item.file_size for item in archive.infolist()) > MAX_ARCHIVE_BYTES:
                    return hits + [(safe_name, "archive-limit")]
                for item in archive.infolist():
                    hits.extend(scan_blob(name + "!" + item.filename + "!<metadata>", item.extra + item.comment, depth + 1))
                    hits.extend(scan_blob(name + "!" + item.filename, archive.read(item), depth + 1))
        elif is_gzip:
            cursor = 10
            if data[3] & 4:
                size = int.from_bytes(data[cursor:cursor + 2], "little")
                hits.extend(scan_blob(name + "!<gzip extra>", data[cursor + 2:cursor + 2 + size], depth + 1))
                cursor += size + 2
            for flag in (8, 16):
                if data[3] & flag:
                    end = data.index(b"\0", cursor)
                    hits.extend(scan_blob(name + "!<gzip metadata>", data[cursor:end], depth + 1))
                    cursor = end + 1
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
                    hits.extend(scan_blob(name + "!" + item.name, handle.read() if handle else item.linkname.encode(), depth + 1))
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
