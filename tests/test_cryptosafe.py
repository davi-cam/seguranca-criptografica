import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "exemplos" / "declaracao.txt"
ABC_SHA256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


class CrypSafeTests(unittest.TestCase):
    def setUp(self):
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.document = directory / "declaração acadêmica.txt"
        self.document.write_bytes(EXAMPLE.read_bytes())
        self.private_key = directory / "privada.pem"
        self.public_key = directory / "publica.pem"
        self.signature = directory / "declaracao.sig"

    def cli(self, *args, expected=0):
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(ROOT / "cryptosafe.py"), *map(str, args)],
            capture_output=True,
            encoding="utf-8",
            timeout=15,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def sign_document(self):
        self.cli("keygen", self.private_key, self.public_key)
        self.cli("sign", self.document, self.private_key, self.signature)

    def test_ti01_hash_conhecido(self):
        self.document.write_bytes(b"abc")
        result = self.cli("hash", self.document)
        self.assertEqual(result.stdout.strip(), ABC_SHA256)

    def test_ti02_hash_diverge_apos_alteracao(self):
        reference = self.cli("hash", self.document).stdout.strip()
        self.assertIsNotNone(re.fullmatch(r"[0-9a-f]{64}", reference))
        self.cli("check", self.document, reference)
        self.document.write_bytes(self.document.read_bytes() + b"\nAlterado.")
        result = self.cli("check", self.document, reference, expected=1)
        self.assertIn("diverge", result.stdout)

    def test_ti03_par_de_chaves_pem(self):
        self.cli("keygen", self.private_key, self.public_key)
        private_pem = self.private_key.read_bytes()
        public_pem = self.public_key.read_bytes()
        self.assertTrue(private_pem.startswith(b"-----BEGIN PRIVATE KEY-----"))
        self.assertTrue(public_pem.startswith(b"-----BEGIN PUBLIC KEY-----"))
        private_key = serialization.load_pem_private_key(private_pem, password=None)
        public_key = serialization.load_pem_public_key(public_pem)
        self.assertIsInstance(private_key, Ed25519PrivateKey)
        self.assertIsInstance(public_key, Ed25519PublicKey)
        self.assertEqual(private_key.public_key().public_bytes_raw(), public_key.public_bytes_raw())

    def test_ti04_assinatura_do_arquivo_original(self):
        self.sign_document()
        signature = self.signature.read_bytes()
        self.assertEqual(len(signature), 64)
        public_key = serialization.load_pem_public_key(self.public_key.read_bytes())
        public_key.verify(signature, self.document.read_bytes())
        result = self.cli("verify", self.document, self.public_key, self.signature)
        self.assertEqual(result.stdout.strip(), "Assinatura válida.")

    def test_ti05_arquivo_alterado(self):
        self.sign_document()
        self.document.write_bytes(self.document.read_bytes() + b"\nAlterado.")
        result = self.cli("verify", self.document, self.public_key, self.signature, expected=1)
        self.assertEqual(result.stdout.strip(), "Assinatura inválida.")

    def test_ti06_outra_chave_publica(self):
        self.sign_document()
        other_public_key = self.public_key.with_name("outra-publica.pem")
        self.cli("keygen", self.private_key.with_name("outra-privada.pem"), other_public_key)
        result = self.cli("verify", self.document, other_public_key, self.signature, expected=1)
        self.assertEqual(result.stdout.strip(), "Assinatura inválida.")

    def test_assinatura_com_tamanho_invalido(self):
        self.sign_document()
        signature = self.signature.read_bytes()
        for invalid_signature in (signature[:-1], signature + b"\x00"):
            with self.subTest(size=len(invalid_signature)):
                self.signature.write_bytes(invalid_signature)
                result = self.cli("verify", self.document, self.public_key, self.signature, expected=1)
                self.assertIn("deve ter 64 bytes", result.stdout)

    def test_arquivo_inexistente(self):
        result = self.cli("hash", self.document.with_name("inexistente.txt"), expected=2)
        self.assertIn("não encontrado", result.stderr)

    def test_chave_incompativel(self):
        private_key = X25519PrivateKey.generate()
        self.private_key.write_bytes(private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ))
        result = self.cli("sign", self.document, self.private_key, self.signature, expected=2)
        self.assertIn("deve ser Ed25519", result.stderr)
        self.assertFalse(self.signature.exists())
