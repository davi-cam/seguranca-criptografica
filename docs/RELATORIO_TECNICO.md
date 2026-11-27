CrypSafe - Relatório técnico

Integrantes: Davi Camargo e Ester Lohana
Turma: oitavo período
Linguagem: Python
Repositório: https://github.com/davi-cam/seguranca-criptografia

Como a ferramenta funciona

O programa fica em cryptosafe.py e lê os arquivos em modo binário. Usa hashlib, que vem com o Python, para calcular o SHA-256. Para gerar chaves e lidar com assinaturas, usa cryptography, com a versão definida em requirements.txt. A declaração fictícia está em exemplos/declaracao.txt e os testes ficam em tests/.

O comando keygen gera um par Ed25519. A chave privada fica em PEM PKCS#8 sem senha e a pública em PEM SubjectPublicKeyInfo (R01). O comando hash mostra o SHA-256 em 64 caracteres hexadecimais minúsculos (R02). O check compara esse valor com a referência informada (R03).

O sign usa a chave privada para assinar os bytes originais do arquivo, sem pré-hash, e grava uma assinatura binária de 64 bytes (R04). O verify usa a chave pública para verificar a assinatura (R05). Se o documento for alterado, a chave pública for diferente ou a assinatura for inválida, a verificação falha (R06). Os comandos check e verify retornam 0 para sucesso, 1 para divergência ou assinatura inválida e 2 para erros de uso ou acesso.

Testes

Os nove testes passaram em Python 3.13 no Windows. Os métodos abaixo ficam em tests/test_cryptosafe.py.

```
ID    Resultado observado               Evidência (método)
TI01  Hash igual ao valor conhecido     test_ti01_hash_conhecido
TI02  Mudança detectada pelo hash       test_ti02_hash_diverge_apos_alteracao
TI03  PEMs válidos e chaves do par      test_ti03_par_de_chaves_pem
TI04  Assinatura de 64 bytes válida     test_ti04_assinatura_do_arquivo_original
TI05  Documento alterado rejeitado      test_ti05_arquivo_alterado
TI06  Outra chave pública rejeitada     test_ti06_outra_chave_publica
```

Os outros três testes cobrem arquivo inexistente, chave de tipo incompatível e assinatura com tamanho inválido.

Análise e conclusão

Qualquer pessoa com acesso ao arquivo consegue calcular seu SHA-256. O hash ajuda a detectar mudanças quando comparado com uma referência confiável. Por si só, ele não comprova quem criou o arquivo.

A chave privada é usada para assinar e deve ficar sob controle do titular. A pública é usada para verificar. Para identificar o assinante, é preciso saber de forma confiável a quem pertence a chave pública.

A assinatura é calculada para os bytes originais. Se o documento mudar, os bytes usados na verificação já não correspondem à assinatura gravada.

Para uso em produção, seria preciso proteger o acesso à chave privada, distribuir as chaves públicas por um canal autenticado e prever rotação, revogação e auditoria. Nesta versão, a chave privada é gravada sem senha. A assinatura e a verificação também leem o arquivo inteiro em memória, o que limita o uso com arquivos grandes.

Os testes confirmaram que a ferramenta detecta alterações e valida assinaturas nos casos da atividade.
