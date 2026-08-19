---
name: onboarding-task-status
description: Registra, num repositório Git compartilhado do time, o início, a conclusão e os erros de cada tarefa que você realiza através do Claude Code, para alimentar o painel de acompanhamento do time. Ative no início de cada sessão de trabalho.
---

# Onboarding Task Status

Você é o Claude Code trabalhando com um colaborador do time Aegro. Além de
executar o que ele pedir, você mantém um **registro de status** de cada
tarefa relevante num arquivo compartilhado, para alimentar o painel do time.

## Regra de ouro: nunca bloqueie o trabalho real por causa do log

O registro é secundário. Se o `git push` falhar (sem internet, conflito,
sem autenticação), **continue normalmente com o pedido do colaborador** e só
sinalize o problema de forma discreta ao final (ver "Se o push falhar").

## Transparência

Isso não é silencioso: sempre que você registrar um evento, adicione ao final
da sua resposta normal (não em vez dela) uma linha curta, por exemplo:

> _(registrado no painel do time: tarefa iniciada)_

O colaborador deve sempre conseguir ver que o registro está acontecendo.

## Nunca registre

- Senhas, tokens, API keys, connection strings — mesmo mascarados.
- CPF/CNPJ, e-mail, telefone, endereço, dados bancários ou qualquer dado real
  de cliente/fazenda.
- Conteúdo de arquivos, prompts completos ou saídas de comando na íntegra.

Registre só **metadado**: quem, projeto, descrição curta da tarefa, status,
timestamp, e — em caso de erro — uma mensagem de erro **sanitizada** (sem os
itens acima).

## Configuração (ajuste uma vez por máquina, na primeira ativação)

```
REPO      = "yaraoliveira-onb/team-task-status"
BRANCH    = "main"
FILE_PATH = "data/status.jsonl"
LOCAL_DIR = "$HOME/.aegro-task-status"
```

### Pré-requisito: acesso de escrita ao repositório

O repositório é público para leitura, mas escrita (`git push`) ainda exige
ser colaborador. Se o `git push` falhar por permissão, avise o colaborador
que ele precisa ser adicionado como colaborador em
`https://github.com/yaraoliveira-onb/team-task-status/settings/access` antes
da skill funcionar — não tente contornar isso.

**Importante:** por ser público, redobre o cuidado com "Nunca registre"
abaixo — qualquer pessoa na internet pode ler `data/status.jsonl`.

## Fluxo em cada tarefa

Considere "tarefa relevante" qualquer pedido de trabalho real do colaborador
(rodar um comando, editar algo, gerar um relatório etc.) — não logue
perguntas triviais de esclarecimento.

Identifique:

- `pessoa`: `git config --get user.name` (ou, se vazio, o nome de usuário do
  sistema operacional).
- `projeto`: nome do projeto/fazenda em contexto, ou, na falta disso, o nome
  da pasta atual.
- `tarefa`: descrição curta (até ~80 caracteres) do que foi pedido, em
  português simples, sem dado sensível.
- `tarefa_id`: um id curto e único, por exemplo `date +%Y%m%dT%H%M%S%N` mais 4
  caracteres aleatórios.

### 1. No início da tarefa

Garanta que o repositório local existe e está atualizado:

```bash
if [ ! -d "$LOCAL_DIR/.git" ]; then
  git clone --depth 1 "https://github.com/$REPO.git" "$LOCAL_DIR"
else
  git -C "$LOCAL_DIR" pull --rebase --quiet
fi
```

Acrescente uma linha JSON e envie:

```bash
LINE=$(printf '{"ts":"%s","pessoa":"%s","projeto":"%s","tarefa_id":"%s","tarefa":"%s","status":"iniciada"}' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$PESSOA" "$PROJETO" "$TAREFA_ID" "$TAREFA")
mkdir -p "$(dirname "$LOCAL_DIR/$FILE_PATH")"
echo "$LINE" >> "$LOCAL_DIR/$FILE_PATH"
git -C "$LOCAL_DIR" add "$FILE_PATH"
git -C "$LOCAL_DIR" commit -m "log: inicio tarefa $TAREFA_ID" --quiet
git -C "$LOCAL_DIR" pull --rebase --quiet
git -C "$LOCAL_DIR" push --quiet
```

Guarde `tarefa_id` em memória (nesta sessão) para usar no evento final.

### 2. Ao concluir a tarefa com sucesso

Repita pull + append + commit + pull --rebase + push com:

```json
{"ts":"...","pessoa":"...","projeto":"...","tarefa_id":"<mesmo id>","tarefa":"...","status":"concluida"}
```

### 3. Se a tarefa falhar por erro no CLI (ou em qualquer execução)

Registre com status `erro` e uma mensagem **curta e sanitizada** (remova
qualquer token, caminho de arquivo com dado sensível, ou payload bruto — só a
causa em uma frase, ex: "comando aegro retornou código 1: fazenda não
encontrada"):

```json
{"ts":"...","pessoa":"...","projeto":"...","tarefa_id":"<mesmo id>","tarefa":"...","status":"erro","erro_msg":"..."}
```

## Se o `git push` falhar (conflito, sem rede, sem auth)

1. Tente uma vez: `git -C "$LOCAL_DIR" pull --rebase --quiet && git -C "$LOCAL_DIR" push --quiet`.
2. Se falhar de novo, **não insista mais de 2 vezes** e **não interrompa** a
   resposta ao colaborador. Apenas termine sua resposta normal com uma linha
   discreta, por exemplo:
   > _(obs: não consegui sincronizar o registro de status agora — sem
   > conexão ou sem permissão de escrita no repo; a tarefa em si foi
   > concluída normalmente)_
3. Nunca exponha mensagens de erro de autenticação que contenham token ou
   URL com credencial embutida.

## Resumo do que cada evento contém

| campo       | obrigatório | conteúdo                                     |
| ----------- | ----------- | --------------------------------------------- |
| `ts`        | sim         | timestamp UTC ISO 8601                         |
| `pessoa`    | sim         | nome do colaborador                            |
| `projeto`   | sim         | projeto/fazenda associado                      |
| `tarefa_id` | sim         | id único da tarefa (liga início → fim)         |
| `tarefa`    | sim         | descrição curta, sem dado sensível             |
| `status`    | sim         | `iniciada` \| `concluida` \| `erro`            |
| `erro_msg`  | só se erro  | mensagem curta e sanitizada                    |
