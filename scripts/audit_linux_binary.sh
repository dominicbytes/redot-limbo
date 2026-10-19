#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "$0")" && pwd)"

audit() {
	"$@" 2>&1 | python3 "$script_dir/content_policy.py" --sanitize-stdin
}

if [ "$#" -eq 0 ]; then
	echo "usage: audit_linux_binary.sh LIBRARY [...]" >&2
	exit 2
fi

for library in "$@"; do
	python3 "$script_dir/content_policy.py" "$library"
	audit file -b "$library"
	audit readelf -h "$library" | grep -E "Class:|Machine:|Type:"
	audit readelf -d "$library" | grep NEEDED
	audit nm -D --defined-only "$library" | grep " limboai_init$"
	glibc_max="$(audit readelf --version-info "$library" | grep -oE 'GLIBC_[0-9]+(\.[0-9]+)+' | sed 's/^GLIBC_//' | sort -Vu | tail -n 1)"
	if [ -z "$glibc_max" ]; then
		echo "GLIBC_VERSION_NOT_FOUND" >&2
		exit 5
	fi
	if [ "$(printf '%s\n' "$glibc_max" '2.38' | sort -V | tail -n 1)" != '2.38' ]; then
		echo "GLIBC_VERSION_TOO_NEW library requires $glibc_max (maximum 2.38)" >&2
		exit 6
	fi
	echo "GLIBC_MAX $glibc_max"
done
