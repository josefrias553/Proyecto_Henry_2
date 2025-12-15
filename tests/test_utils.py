import sys
import unittest
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils import normalize_header, map_row_keys, hash_password

class TestUtils(unittest.TestCase):
    def test_normalize_header(self):
        self.assertEqual(normalize_header("  Nombre  "), "nombre")
        self.assertEqual(normalize_header("Año"), "ano")
        self.assertEqual(normalize_header("CÓDIGO POSTAL"), "codigopostal")

    def test_map_row_keys(self):
        raw = {" Nombre ": " Juan ", "Año": "2023"}
        mapped = map_row_keys(raw)
        self.assertEqual(mapped.get("nombre"), " Juan ")
        self.assertEqual(mapped.get("ano"), "2023")

    def test_hash_password(self):
        pwd = "secret_password"
        hashed = hash_password(pwd)
        self.assertNotEqual(pwd, hashed)
        self.assertTrue(len(hashed) > 0)
        self.assertEqual(hash_password(""), "")

if __name__ == "__main__":
    unittest.main()
