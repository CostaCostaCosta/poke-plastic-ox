"""Malformed-model checks, runnable without Metamon or its training packages."""
import json
from pathlib import Path
import struct
import tempfile
import unittest

from import_model import SCHEMA, expected_tensors, generate, read_export


class ExportValidation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.binary = self.root / "student.bin"
        self.manifest = self.root / "manifest.json"
        tensors, body = {}, bytearray()
        for name, (code, shape) in expected_tensors().items():
            count = 1
            for dim in shape: count *= dim
            payload = (struct.pack("<f", 1 if name.endswith("/scale") else 0) * count
                       if code == "f4" else bytes(count))
            name_bytes = name.encode()
            body += struct.pack("<H", len(name_bytes)) + name_bytes + code.encode()
            body += bytes([len(shape)]) + struct.pack("<" + "I" * len(shape), *shape) + payload
            tensors[name] = dict(code=code, shape=list(shape), bytes=len(payload))
        self.binary.write_bytes(b"MG3SINT8" + struct.pack("<IQ", 1, len(body)) + body)
        self.man = dict(format="MG3SINT8", version=1, preset="1m", window=4,
                        hidden=384, schema=SCHEMA, parameters=1011355, tensors=tensors)
        self.save_manifest()

    def save_manifest(self):
        self.manifest.write_text(json.dumps(self.man))

    def test_valid_and_aligned(self):
        report = generate(self.binary, self.manifest, self.root / "generated")
        self.assertEqual(report["macs_per_decision"], 1235584)
        self.assertEqual(report["aligned_tensor_bytes"] % 4, 0)

    def test_truncated_or_appended_body(self):
        original = self.binary.read_bytes()
        for data in (original[:-1], original + b"\0"):
            self.binary.write_bytes(data)
            with self.assertRaises(ValueError): read_export(self.binary, self.manifest)

    def test_schema_and_shape_mismatch(self):
        self.man["schema"] = "unknown"
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "schema"): read_export(self.binary, self.manifest)
        self.man["schema"] = SCHEMA
        self.man["tensors"]["actor"]["shape"] = [10, 640]
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "Manifest mismatch"): read_export(self.binary, self.manifest)

    def test_unsupported_architecture(self):
        self.man["window"] = 8
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "window"): read_export(self.binary, self.manifest)

    def test_invalid_scale(self):
        data = bytearray(self.binary.read_bytes())
        name = b"embed.species/scale"
        offset = data.index(name) + len(name) + 2 + 1 + 4
        for scale in (0.0, float("nan"), 1e30):
            struct.pack_into("<f", data, offset, scale)
            self.binary.write_bytes(data)
            with self.assertRaises(ValueError): read_export(self.binary, self.manifest)

    def test_rom_capacity(self):
        map_path = self.root / "rom.map"
        map_path.write_text("0x09ff0000 __rom_end = .\n")
        with self.assertRaisesRegex(ValueError, "ROM address space"):
            generate(self.binary, self.manifest, self.root / "generated", map_path)


if __name__ == "__main__":
    unittest.main()
