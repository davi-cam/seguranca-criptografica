CrypSafe

CrypSafe é uma ferramenta de linha de comando para calcular e comparar hashes SHA-256 e assinar arquivos com Ed25519.

Integrantes: Davi Camargo e Ester Lohana.

Instalação

Na pasta do projeto, use Python 3.11 ou superior com pip e venv.

PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe cryptosafe.py --help
```

Bash (Linux ou macOS)

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python cryptosafe.py --help
```

Comandos

Execute cryptosafe.py com o Python do ambiente, seguido do subcomando e dos argumentos na ordem abaixo. Use aspas em caminhos com espaços.

- keygen CHAVE_PRIVADA CHAVE_PUBLICA. Gera chaves Ed25519 em PEM: privada PKCS#8 sem senha e pública SubjectPublicKeyInfo. (R01)
- hash ARQUIVO. Exibe o SHA-256 em 64 caracteres hexadecimais minúsculos. (R02)
- check ARQUIVO HASH_REFERENCIA. Compara o SHA-256 com uma referência no mesmo formato. (R03)
- sign ARQUIVO CHAVE_PRIVADA ASSINATURA. Assina os bytes originais com Ed25519, sem pré-hash, e grava uma assinatura binária de 64 bytes. (R04)
- verify ARQUIVO CHAVE_PUBLICA ASSINATURA. Usa a chave pública para validar a assinatura, rejeitando arquivos alterados e assinaturas inválidas. (R05, R06)

O programa lê os arquivos em modo binário. Usa hashlib para SHA-256 e cryptography para Ed25519, com a versão fixada em requirements.txt. keygen e sign exigem caminhos de saída novos. Guarde as chaves privadas fora do repositório.

Códigos de saída: 0 para sucesso, 1 para hash divergente ou assinatura inválida e 2 para erro, como caminho inválido, arquivo inexistente, chave incompatível ou referência malformada.

Demonstração

Os exemplos usam a declaração fictícia em exemplos/declaracao.txt. Após a alteração da cópia, check e verify devem retornar 1.

PowerShell

```powershell
$python = '.\.venv\Scripts\python.exe'
$arquivo = 'exemplos/declaracao.txt'
$demo = Join-Path ([System.IO.Path]::GetTempPath()) ('cryp-safe-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $demo | Out-Null

$privada = Join-Path $demo 'privada.pem'
$publica = Join-Path $demo 'publica.pem'
$assinatura = Join-Path $demo 'declaracao.sig'
$alterado = Join-Path $demo 'declaracao-alterada.txt'

$referencia = & $python cryptosafe.py hash $arquivo
$referencia
& $python cryptosafe.py check $arquivo $referencia
& $python cryptosafe.py keygen $privada $publica
& $python cryptosafe.py sign $arquivo $privada $assinatura
& $python cryptosafe.py verify $arquivo $publica $assinatura

Copy-Item -LiteralPath $arquivo -Destination $alterado
Add-Content -LiteralPath $alterado -Value 'Texto acrescentado depois da assinatura.'
& $python cryptosafe.py check $alterado $referencia
$LASTEXITCODE
& $python cryptosafe.py verify $alterado $publica $assinatura
$LASTEXITCODE
```

Bash

```bash
python=./.venv/bin/python
arquivo=exemplos/declaracao.txt
demo=$(mktemp -d)

referencia=$("$python" cryptosafe.py hash "$arquivo")
printf '%s\n' "$referencia"
"$python" cryptosafe.py check "$arquivo" "$referencia"
"$python" cryptosafe.py keygen "$demo/privada.pem" "$demo/publica.pem"
"$python" cryptosafe.py sign "$arquivo" "$demo/privada.pem" "$demo/declaracao.sig"
"$python" cryptosafe.py verify "$arquivo" "$demo/publica.pem" "$demo/declaracao.sig"

cp "$arquivo" "$demo/declaracao-alterada.txt"
printf '\n%s\n' 'Texto acrescentado depois da assinatura.' >> "$demo/declaracao-alterada.txt"
"$python" cryptosafe.py check "$demo/declaracao-alterada.txt" "$referencia" || printf 'Código: %s\n' "$?"
"$python" cryptosafe.py verify "$demo/declaracao-alterada.txt" "$demo/publica.pem" "$demo/declaracao.sig" || printf 'Código: %s\n' "$?"
```

Testes

No PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

No Bash:

```bash
./.venv/bin/python -m unittest discover -s tests -v
```

A suíte cobre os seis testes obrigatórios (TI01 a TI06) e três casos de erro. Consulte o relatório técnico em docs/RELATORIO_TECNICO.md para ver os resultados, as evidências e as limitações.
