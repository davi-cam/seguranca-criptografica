# CrypSafe

CrypSafe é uma ferramenta de linha de comando para verificar a integridade e a assinatura digital de arquivos. A declaração acadêmica fictícia em [`exemplos/declaracao.txt`](exemplos/declaracao.txt) permite experimentar os comandos sem usar dados pessoais reais.

**Integrantes:** Davi Camargo e Ester Lohana.

## Instalação

Use Python 3.11 ou superior com `pip`. Abra o terminal na pasta que contém `cryptosafe.py` e `requirements.txt`. No Bash, use `python3` para criar o ambiente. Em algumas distribuições Linux, é necessário instalar o suporte a `venv` da própria distribuição.

### PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe cryptosafe.py --help
```

### Bash (Linux ou macOS)

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python cryptosafe.py --help
```

## Comandos

Execute os subcomandos abaixo com o Python do ambiente, como nos exemplos. Coloque entre aspas os caminhos que contêm espaços.

| Subcomando e argumentos | Resultado |
| --- | --- |
| `keygen CHAVE_PRIVADA CHAVE_PUBLICA` | Gera um par Ed25519 e grava as duas chaves. |
| `hash ARQUIVO` | Exibe somente o SHA-256 em hexadecimal minúsculo. |
| `check ARQUIVO HASH_REFERENCIA` | Informa se o SHA-256 corresponde à referência de 64 caracteres hexadecimais minúsculos. |
| `sign ARQUIVO CHAVE_PRIVADA ASSINATURA` | Assina o arquivo e grava a assinatura no caminho indicado. |
| `verify ARQUIVO CHAVE_PUBLICA ASSINATURA` | Informa se a assinatura é válida para o arquivo e a chave fornecidos. |

Os códigos de saída são `0` para sucesso, `1` para hash divergente ou assinatura inválida e `2` para erro de uso ou de operação, como arquivo inexistente, chave incompatível ou hash de referência malformado. As mensagens de erro de código `2` são enviadas à saída de erro. O `keygen` e o `sign` exigem caminhos de saída novos. As chaves privadas geradas ficam em PEM PKCS#8 sem senha e devem permanecer fora do repositório.

## Demonstração

Os dois exemplos calculam o hash da declaração, conferem o valor, geram as chaves, assinam e verificam o arquivo. Depois acrescentam texto a uma cópia e repetem as verificações. É esperado que tanto o hash quanto a assinatura falhem na cópia e que o código de saída seja `1` em ambos os casos.

### PowerShell

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

### Bash

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

## Como funciona

**Integridade com SHA-256.** `hash` e `check` abrem o arquivo em modo binário e usam `hashlib.file_digest` para calcular o SHA-256 sem carregar todo o conteúdo de uma vez. O resultado tem 256 bits e é exibido como 64 dígitos hexadecimais minúsculos. `check` valida o formato da referência e compara os dois valores. Uma referência obtida por um canal confiável permite detectar alterações. Qualquer pessoa pode calcular o hash do arquivo, por isso o valor sozinho não comprova autoria. [Documentação do `hashlib`](https://docs.python.org/3.11/library/hashlib.html#hashlib.file_digest)

**Geração de chaves.** A biblioteca `cryptography` gera a chave privada Ed25519 e deriva a chave pública correspondente. A chave privada é armazenada em PEM PKCS#8 e serve para assinar. A chave pública é armazenada em PEM SubjectPublicKeyInfo e pode ser distribuída para verificação. A identidade do assinante depende de obter essa chave pública de uma fonte confiável. [Documentação de serialização](https://cryptography.io/en/48.0.0/hazmat/primitives/asymmetric/serialization/)

**Assinatura e verificação.** `sign` passa os bytes originais do documento ao Ed25519, sem calcular um pré-hash na aplicação, e grava exatamente os 64 bytes retornados pela biblioteca. `verify` confere o tamanho da assinatura e verifica os bytes do documento com a chave pública. Mudanças de conteúdo, codificação ou finais de linha alteram os bytes e invalidam a assinatura. A extensão do arquivo pode ser qualquer uma. As duas operações leem o documento inteiro em memória. [Documentação de Ed25519](https://cryptography.io/en/48.0.0/hazmat/primitives/asymmetric/ed25519/)

## Como os requisitos foram atendidos

| ID | Implementação | Verificação automatizada |
| --- | --- | --- |
| R01 | `keygen` gera o par Ed25519 e grava os dois arquivos PEM nos formatos exigidos. | TI03 carrega os PEMs, verifica os tipos e confirma que as chaves correspondem. |
| R02 | `hash` calcula o SHA-256 a partir dos bytes do arquivo. | TI01 compara o resultado com o SHA-256 conhecido de `abc`. |
| R03 | `check` compara o hash calculado com o valor de referência. | TI02 confere o original e exige código `1` após alteração. |
| R04 | `sign` usa a chave privada para assinar o conteúdo original e grava a assinatura binária. | TI04 mede os 64 bytes e verifica a assinatura diretamente sobre o conteúdo com a biblioteca. |
| R05 | `verify` usa a chave pública correspondente e retorna `0` se a assinatura for válida. | TI04 confirma a mensagem e o código de sucesso da CLI. |
| R06 | `verify` retorna `1` se a assinatura não corresponder ao documento ou à chave pública. | TI05 altera o documento e TI06 troca a chave pública. Ambos exigem código `1`. |

Os testes também exercitam arquivo inexistente, assinatura com tamanho inválido e chave de algoritmo incompatível. A ordem dos argumentos e os formatos compartilhados seguem o contrato de interoperabilidade da atividade.

## Executar os testes

No PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

No Bash:

```bash
./.venv/bin/python -m unittest discover -s tests -v
```

A suíte usa arquivos temporários e chaves geradas durante a execução. O [relatório técnico](docs/RELATORIO_TECNICO.md) resume as decisões, os resultados e as limitações do projeto.
