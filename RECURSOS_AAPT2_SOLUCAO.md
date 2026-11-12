# ReaDroid — registo de diagnóstico AAPT2 e recursos `$`

## Caso observado

Em 12-11-2026, no Termux/Android, a opção 11 falhou na reconstrução de um APK Seal porque o Apktool e o AAPT2 rejeitaram nomes de ficheiros de recursos drawable iniciados por `$`. O erro ocorria na compilação de recursos, **antes da assinatura**. O utilizador confirmou autorização para modificar o APK.

Exemplo do erro: `resource 'drawable/$mtrl_checkbox_button_icon_indeterminate_checked__0' has invalid entry name`.

Na pasta extraída havia 40 ficheiros em `res/drawable` cujo nome começava por `$`. O primeiro exemplo tinha referências em `res/drawable/avd_hide_password.xml` e `res/values/public.xml`: não bastava mudar o nome do ficheiro isoladamente.

## Procedimento que foi aplicado no caso

1. O utilizador copiou a pasta completa extraída do Apktool para uma pasta de backup separada. A existência da pasta foi confirmada; não foi verificada a integridade de cada ficheiro do backup.
2. Contou os 40 ficheiros e confirmou que, na mesma pasta de cada ficheiro, o nome sem `$` ainda não existia. Isto **não verifica todas as possibilidades de colisão entre recursos Android** nem referências dinâmicas.
3. Um script pontual alterou os 40 nomes de ficheiro, removendo o `$` inicial, e substituiu as ocorrências dos nomes antigos nos ficheiros de texto da extração. A saída informada foi: 40 ficheiros renomeados e 80 referências textuais atualizadas. O backup foi mantido.
4. O utilizador executou novamente a opção 11 e informou que o ReaDroid produziu um ficheiro `aligned.apk` e uma cópia em Downloads, sem o erro inicial de AAPT2. Não houve confirmação de instalação, execução, funcionamento das animações ou verificação detalhada da assinatura. Este resultado não prova compatibilidade para outros APKs.

## Precauções para o futuro

- Usar apenas em APKs próprios ou para os quais exista autorização para modificar.
- Preservar o APK original, a pasta extraída e a keystore. Fazer backup completo e confirmar que é recuperável antes de qualquer mudança.
- Identificar os nomes, todas as configurações do recurso e respetivas referências em XML, `public.xml`, smali e outros ficheiros. Verificar colisões no espaço de nomes de recursos, não apenas nomes de ficheiros na mesma pasta. Nomes podem também ser usados dinamicamente ou em ficheiros binários.
- Uma substituição textual ampla pode alterar texto que não é uma referência a recursos; referências binárias ou dinâmicas podem escapar. Não aplicar renomeações automaticamente sem análise, testes e revisão das alterações.
- Validar reconstrução, assinatura, instalação e funcionamento em ambiente apropriado. Reassinar altera a identidade do certificado e pode impedir atualização sobre o original. Concluir `apktool b` por si só não comprova que a aplicação funciona.
- A opção 11 do ReaDroid já assinala os ficheiros com `$` no início, mas **não os corrige automaticamente**. Este documento é um registo de um caso, não uma correção universal.

O APK, a extração, o backup e a chave do utilizador não fazem parte deste repositório.

## Script pontual utilizado no caso (registo histórico)

**Não executar diretamente noutro APK.** Este script altera a pasta extraída, verifica apenas conflitos de ficheiro na mesma pasta, procura apenas certas extensões e não encontra referências binárias/dinâmicas. Uma falha a meio pode deixar alterações parciais. Deve ser analisado e adaptado caso a caso; confirme antes o backup e as referências. O caminho abaixo corresponde ao dispositivo do utilizador na data do caso.

```python
from pathlib import Path
import re

base = Path("output/Seal-1.13.1-arm64-v8a-release_apktool")
backup = base.with_name(base.name + ".backup-20261112")
if not backup.is_dir():
    raise SystemExit("ERRO: não encontrei a cópia de segurança; nada foi alterado.")

files = sorted((base / "res").rglob("$*.xml"))
targets = [p.with_name(p.name[1:]) for p in files]
if not files:
    raise SystemExit("ERRO: não encontrei ficheiros com $; nada foi alterado.")
if any(p.exists() for p in targets) or len(set(targets)) != len(targets):
    raise SystemExit("ERRO: há conflito de nomes; nada foi alterado.")

renames = [(p.name[:-4].encode(), p.name[1:-4].encode()) for p in files]
text_ext = {".xml", ".smali", ".yml", ".yaml", ".txt", ".json",
            ".properties", ".java", ".kt", ".gradle", ".pro"}
updates = []
total = 0

for path in base.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in text_ext:
        continue
    data = path.read_bytes()
    if b"\0" in data:
        continue
    changed = data
    for old, new in renames:
        pattern = re.escape(old) + rb"(?![A-Za-z0-9_])"
        changed, count = re.subn(pattern, new, changed)
        total += count
    if changed != data:
        updates.append((path, changed))

for path, data in updates:
    path.write_bytes(data)
for old, new in zip(files, targets):
    old.rename(new)

print(f"Concluído: {len(files)} ficheiros renomeados; {total} referências atualizadas.")
print("O backup original foi mantido.")
```
