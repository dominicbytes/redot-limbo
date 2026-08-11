#!/bin/sh
set -eu

if [ "$#" -eq 0 ]; then
	echo "usage: audit_linux_binary.sh LIBRARY [...]" >&2
	exit 2
fi

for library in "$@"; do
	file "$library"
	readelf -h "$library" | grep -E "Class:|Machine:|Type:"
	readelf -d "$library" | grep NEEDED
	nm -D --defined-only "$library" | grep " limboai_init$"
	glibc_max="$(readelf --version-info "$library" | grep -oE 'GLIBC_[0-9]+(\.[0-9]+)+' | sed 's/^GLIBC_//' | sort -Vu | tail -n 1)"
	if [ -z "$glibc_max" ]; then
		echo "GLIBC_VERSION_NOT_FOUND $library" >&2
		exit 5
	fi
	if [ "$(printf '%s\n' "$glibc_max" '2.38' | sort -V | tail -n 1)" != '2.38' ]; then
		echo "GLIBC_VERSION_TOO_NEW $library requires $glibc_max (maximum 2.38)" >&2
		exit 6
	fi
	echo "GLIBC_MAX $glibc_max"
	if strings -a "$library" | grep -E 'D:\\|/workspace|Claude Vault|LIMBOAI_FIXTURE|ghp_|BEGIN (RSA|OPENSSH|EC) PRIVATE'; then
		echo "FORBIDDEN_STRING_FOUND $library" >&2
		exit 4
	fi
done
