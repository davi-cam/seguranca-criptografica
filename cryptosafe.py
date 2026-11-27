import hashlib
import os
import re
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def write_new_file(path, data, mode=0o666):
    file = open(path, "xb", opener=lambda name, flags: os.open(name, flags, mode))
    try:
        with file:
            file.write(data)
    except OSError:
        path.unlink()
        raise


def keygen(private_path, public_path):
    private_key = Ed25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    write_new_file(private_path, private_pem, mode=0o600)
    try:
        write_new_file(public_path, public_pem)
    except OSError:
        private_path.unlink()
        raise
    print("Par de chaves Ed25519 gerado.")
    return 0


def sha256(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def show_hash(path):
    print(sha256(path))
    return 0


def check(path, reference):
    if not re.fullmatch(r"[0-9a-f]{64}", reference):
        raise ValueError("O hash de referência deve ter 64 caracteres hexadecimais minúsculos.")
    if sha256(path) == reference:
        print("O hash corresponde à referência.")
        return 0
    print("O hash diverge da referência.")
    return 1


def sign(path, private_path, signature_path):
    private_pem = private_path.read_bytes()
    try:
        private_key = serialization.load_pem_private_key(private_pem, password=None)
    except (ValueError, TypeError, UnsupportedAlgorithm):
        raise ValueError("Chave privada inválida. Use uma chave Ed25519 em PEM PKCS#8 sem senha.") from None
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("A chave privada deve ser Ed25519.")
    write_new_file(signature_path, private_key.sign(path.read_bytes()))
    print("Assinatura gerada.")
    return 0


def verify(path, public_path, signature_path):
    public_pem = public_path.read_bytes()
    try:
        public_key = serialization.load_pem_public_key(public_pem)
    except (ValueError, UnsupportedAlgorithm):
        raise ValueError("Chave pública inválida. Use uma chave Ed25519 em PEM SubjectPublicKeyInfo.") from None
    if not isinstance(public_key, Ed25519PublicKey):
        raise ValueError("A chave pública deve ser Ed25519.")
    with signature_path.open("rb") as file:
        signature = file.read(65)
    if len(signature) != 64:
        print("Assinatura inválida. O arquivo de assinatura deve ter 64 bytes.")
        return 1
    try:
        public_key.verify(signature, path.read_bytes())
    except InvalidSignature:
        print("Assinatura inválida.")
        return 1
    print("Assinatura válida.")
    return 0


COMMANDS = {
    "keygen": (keygen, "CHAVE_PRIVADA CHAVE_PUBLICA", "Gera um par de chaves Ed25519."),
    "hash": (show_hash, "ARQUIVO", "Calcula o SHA-256 do arquivo."),
    "check": (check, "ARQUIVO HASH_REFERENCIA", "Compara o SHA-256 com a referência."),
    "sign": (sign, "ARQUIVO CHAVE_PRIVADA ASSINATURA", "Assina o arquivo."),
    "verify": (verify, "ARQUIVO CHAVE_PUBLICA ASSINATURA", "Verifica a assinatura do arquivo."),
}


def main(args):
    if not args or args in (["-h"], ["--help"]):
        print("CrypSafe | Integridade e assinatura digital de arquivos")
        for command, (_, parameters, description) in COMMANDS.items():
            print(f"  python cryptosafe.py {command} {parameters}\n    {description}")
        return 0 if args else 2

    command, *values = args
    if command not in COMMANDS:
        print(f"Comando desconhecido: {command!r}. Use --help para ver os comandos.", file=sys.stderr)
        return 2

    run, parameters, description = COMMANDS[command]
    usage = f"Uso: python cryptosafe.py {command} {parameters}"
    if values in (["-h"], ["--help"]):
        print(f"{usage}\n{description}")
        return 0
    if len(values) != len(parameters.split()):
        print(f"Quantidade incorreta de argumentos.\n{usage}", file=sys.stderr)
        return 2

    try:
        if command == "check":
            return run(Path(values[0]), values[1])
        return run(*(Path(value) for value in values))
    except FileNotFoundError as error:
        message = f"Arquivo ou pasta não encontrado: {error.filename!r}."
    except FileExistsError as error:
        message = f"O caminho já existe: {error.filename!r}. Escolha outro destino."
    except PermissionError as error:
        message = f"Acesso negado ou caminho inacessível: {error.filename!r}."
    except OSError as error:
        message = f"Não foi possível acessar o caminho: {error.filename!r}."
    except ValueError as error:
        message = str(error)
    except UnsupportedAlgorithm:
        message = "Ed25519 não está disponível nesta instalação da biblioteca cryptography."
    print(f"Erro: {message}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
