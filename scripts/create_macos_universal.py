#!/usr/bin/env python3
"""Combine x86-64 and arm64 thin Mach-O libraries into one deterministic binary."""

from __future__ import annotations

import argparse
from pathlib import Path
import struct


MACHO_64_LE = b"\xcf\xfa\xed\xfe"
FAT_MAGIC = 0xCAFEBABE
CPU_X86_64 = 0x01000007
CPU_ARM64 = 0x0100000C
ALIGN_EXPONENT = 14
ALIGNMENT = 1 << ALIGN_EXPONENT


def architecture(path: Path, expected: int) -> tuple[bytes, int]:
    data = path.read_bytes()
    if data[:4] != MACHO_64_LE:
        raise ValueError(f"Not a little-endian 64-bit Mach-O file: {path}")
    cpu_type, cpu_subtype = struct.unpack_from("<II", data, 4)
    if cpu_type != expected:
        raise ValueError(
            f"Unexpected CPU type 0x{cpu_type:08X} in {path}; "
            f"expected 0x{expected:08X}"
        )
    return data, cpu_subtype


def aligned(value: int) -> int:
    return (value + ALIGNMENT - 1) & ~(ALIGNMENT - 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--x86-64", type=Path, required=True)
    parser.add_argument("--arm64", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    inputs = [
        (CPU_X86_64, *architecture(args.x86_64, CPU_X86_64)),
        (CPU_ARM64, *architecture(args.arm64, CPU_ARM64)),
    ]
    header_size = 8 + len(inputs) * 20
    offset = aligned(header_size)
    records: list[tuple[int, int, int, int, int]] = []
    for cpu_type, data, cpu_subtype in inputs:
        records.append((cpu_type, cpu_subtype, offset, len(data), ALIGN_EXPONENT))
        offset = aligned(offset + len(data))

    output = bytearray(offset)
    struct.pack_into(">II", output, 0, FAT_MAGIC, len(records))
    for index, record in enumerate(records):
        struct.pack_into(">IIIII", output, 8 + index * 20, *record)
    for record, (_cpu_type, data, _cpu_subtype) in zip(records, inputs):
        output[record[2] : record[2] + len(data)] = data

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)
    print(f"{args.output} bytes={len(output)} architectures=x86_64,arm64")


if __name__ == "__main__":
    main()
