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
	if strings -a "$library" | grep -E 'D:\\|/workspace|Claude Vault|LIMBOAI_FIXTURE|ghp_|BEGIN (RSA|OPENSSH|EC) PRIVATE'; then
		echo "FORBIDDEN_STRING_FOUND $library" >&2
		exit 4
	fi
done
