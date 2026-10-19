from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_macos_binary as audit


def thin(cpu, symbol_type=0x0F, section=1, value=0x1000, library_name="liblimboai.macos.editor"):
    name = ("@rpath/" + library_name).encode() + b"\0"
    size = (24 + len(name) + 7) & ~7
    identity = struct.pack("<IIIIII", audit.LC_ID_DYLIB, size, 24, 0, 0, 0) + name
    identity += b"\0" * (size - len(identity))
    version = struct.pack("<IIIIII", audit.LC_BUILD_VERSION, 24, 1, 11 << 16, 0, 0)
    segment_size = 72 + 80
    segment = struct.pack("<II16sQQQQIIII", audit.LC_SEGMENT_64, segment_size, b"__TEXT", 0x1000, 1, 0, 1, 5, 5, 1, 0)
    segment += struct.pack("<16s16sQQIIIIIIII", b"__text", b"__TEXT", 0x1000, 1, 0, 0, 0, 0, 0x80000400, 0, 0, 0)
    symoff = 32 + len(identity) + len(version) + len(segment) + 24
    strings = b"\0_limboai_init\0"
    symtab = struct.pack("<IIIIII", audit.LC_SYMTAB, 24, symoff, 1, symoff + 16, len(strings))
    commands = identity + version + segment + symtab
    header = struct.pack("<IiiIIIII", audit.MACHO_64_LE, cpu, 0, audit.MH_DYLIB, 4, len(commands), 0, 0)
    return header + commands + struct.pack("<IBBHQ", 1, symbol_type, section, 0, value) + strings


def universal(symbol_type=0x0F, library_name="liblimboai.macos.editor"):
    slices = [thin(cpu, symbol_type, library_name=library_name) for cpu in audit.CPU_NAMES]
    offset = 48
    header = struct.pack(">II", audit.FAT_MAGIC, 2)
    for cpu, data in zip(audit.CPU_NAMES, slices):
        header += struct.pack(">IIIII", cpu, 0, offset, len(data), 0)
        offset += len(data)
    return header + b"".join(slices)


class MacOSAuditTests(unittest.TestCase):
    def test_undefined_local_private_absolute_and_debug_symbols_are_rejected(self):
        for cpu in audit.CPU_NAMES:
            for symbol_type in (0, 1, 0x0E, 0x1F, 0x03, 0xEF):
                with self.subTest(cpu=cpu, symbol_type=symbol_type):
                    with self.assertRaisesRegex(ValueError, "Exported symbol"):
                        audit.audit_thin(thin(cpu, symbol_type), cpu)
            for section, value in ((0, 0x1000), (2, 0x1000), (1, 0), (1, 0x1001)):
                with self.assertRaisesRegex(ValueError, "Exported symbol"):
                    audit.audit_thin(thin(cpu, section=section, value=value), cpu)

    def test_defined_external_entry_in_both_executable_slices_passes(self):
        result = audit.audit_library_data(universal(), "liblimboai.macos.editor")
        self.assertEqual(result["architectures"], ["arm64", "x86_64"])


if __name__ == "__main__":
    unittest.main()
