# CrypSafe — Relatório técnico

## Identificação

**Integrantes:** Davi Camargo e Ester Lohana  
**Turma:** oitavo período  
**Linguagem:** Python  
**Repositório:** [davi-cam/seguranca-criptografia](https://github.com/davi-cam/seguranca-criptografia)

## Solução e funcionalidades

A CLI em `cryptosafe.py` recebe os caminhos na ordem definida pelo enunciado. Usa a biblioteca padrão `hashlib` para SHA-256 e a biblioteca `cryptography`, com versão fixada em `requirements.txt`, para Ed25519. Os arquivos são lidos em modo binário. A declaração fictícia está em `exemplos/` e os testes em `tests/`.

| Requisito | Implementação |
| --- | --- |
| R01 | `keygen` gera chaves Ed25519. A chave privada é gravada em PEM PKCS#8 sem senha e a pública em PEM SubjectPublicKeyInfo. |
| R02 | `hash` imprime o SHA-256 do arquivo em 64 caracteres hexadecimais minúsculos. |
| R03 | `check` valida e compara a referência com o valor calculado. |
| R04 | `sign` aplica Ed25519 diretamente aos bytes do arquivo e grava os 64 bytes da assinatura. |
| R05 | `verify` confere a assinatura com a chave pública e informa o resultado. |
| R06 | Documento alterado, chave pública diferente e assinaturas de tamanho incorreto geram rejeição. |

`check` e `verify` usam os códigos `0` para validação bem-sucedida, `1` para divergência ou assinatura inválida e `2` para erros de uso ou acesso.

## Testes realizados

Os nove testes passaram em Python 3.13 no Windows. A coluna de evidência indica o método em [`tests/test_cryptosafe.py`](../tests/test_cryptosafe.py).

| ID | Resultado observado | Evidência |
| --- | --- | --- |
| TI01 | SHA-256 igual ao valor conhecido. | `test_ti01_hash_conhecido` |
| TI02 | Alteração detectada na comparação do hash. | `test_ti02_hash_diverge_apos_alteracao` |
| TI03 | PEMs válidos e chaves correspondentes. | `test_ti03_par_de_chaves_pem` |
| TI04 | Assinatura de 64 bytes válida para o original. | `test_ti04_assinatura_do_arquivo_original` |
| TI05 | Verificação rejeitou o documento alterado. | `test_ti05_arquivo_alterado` |
| TI06 | Verificação rejeitou outra chave pública. | `test_ti06_outra_chave_publica` |

Os três testes adicionais cobrem arquivo inexistente, chave incompatível e assinatura com tamanho inválido.

## Análise e conclusão

1. **SHA-256 e autoria.** Qualquer pessoa com acesso ao documento pode calcular seu hash. A comparação com uma referência confiável verifica integridade, mas não identifica quem produziu o arquivo.
2. **Papel das chaves.** A chave privada gera a assinatura e deve permanecer sob controle do titular. A pública permite verificar a assinatura. Associar a assinatura a uma pessoa ou instituição exige uma associação confiável entre a chave pública e essa identidade.
3. **Alteração do documento.** O Ed25519 verifica a assinatura em função dos bytes recebidos. Se o documento for alterado, os bytes apresentados deixam de corresponder à assinatura original.
4. **Uso em produção.** Seria necessário proteger as chaves privadas com armazenamento seguro e controle de acesso, autenticar a distribuição das chaves públicas e prever rotação, revogação e auditoria. A solução didática armazena a chave privada sem senha e lê o documento inteiro na assinatura e na verificação, o que limita o uso com arquivos grandes.

Os testes demonstram que o CrypSafe valida a integridade e a assinatura de arquivos nos cenários previstos na atividade.
