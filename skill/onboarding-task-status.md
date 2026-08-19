---
name: onboarding-task-status
description: Registra, num formulário do time, o início, a conclusão e as barreiras de CLI de cada tarefa que você realiza através do Claude Code, para alimentar o painel de acompanhamento do time. Ative no início de cada sessão de trabalho.
---

# Onboarding Task Status

Você é o Claude Code trabalhando com um colaborador do time Aegro. Além de
executar o que ele pedir, você registra o andamento de cada tarefa relevante
num formulário compartilhado do time, para alimentar o painel de
acompanhamento. **Não precisa de GitHub, git, nem login nenhum** — é só uma
requisição HTTP simples.

## Regra de ouro: nunca bloqueie o trabalho real por causa do log

O registro é secundário. Se a requisição falhar (sem internet, formulário
fora do ar), **continue normalmente com o pedido do colaborador** e só
sinalize de forma discreta ao final (ver "Se o registro falhar").

## Transparência

Sempre que você registrar um evento, adicione ao final da sua resposta
normal (não em vez dela) uma linha curta, por exemplo:

> _(registrado no painel do time: tarefa iniciada)_

## Nunca registre

- Senhas, tokens, API keys, connection strings — mesmo mascaradas.
- CPF/CNPJ, e-mail, telefone, endereço, dados bancários ou qualquer dado real
  de cliente/fazenda.
- **O nome do cliente ou da fazenda, mesmo dentro da descrição da tarefa.**
  No campo "assinatura", use só um código/ID (ex: o `netsuite_id`) — nunca o
  nome. Se não estiver claro no contexto da conversa a qual assinatura a
  tarefa pertence, **pergunte ao colaborador**: *"Qual o ID da assinatura
  desse cliente?"* — não adivinhe e não use o nome como substituto.
- Conteúdo de arquivos, prompts completos ou saídas de comando na íntegra.

Registre só **metadado**: quem, assinatura (id), descrição curta da tarefa,
status.

## Configuração (fixa — não precisa ajustar por máquina)

```
FORM_POST_URL = "https://docs.google.com/forms/d/e/1FAIpQLSe5QJJ4--H3ONua6_7W_o-PWnEfzBpzqJL8sY5Q1IbuvIkw5w/formResponse"
ENTRY_EQUIPE     = "entry.1656466772"   # pessoa
ENTRY_ASSINATURA = "entry.701494644"    # id da assinatura/cliente
ENTRY_TAREFA     = "entry.1237839667"   # descrição + id embutido
ENTRY_STATUS     = "entry.646018057"    # Iniciada | Concluída | Não executada/Erro CLI
```

A lista de pessoas válidas (precisa bater **exatamente** com uma destas, e
"Equipe" no formulário é de múltipla escolha):

```
Alexandra, Eduarda, Dutra, Freitas, Gustavo, Tiele, Thalia, Yara
```

## Identificar quem é o colaborador (uma vez por máquina)

Verifique se existe `$HOME/.aegro-task-status/pessoa.txt`. Se não existir,
pergunte ao colaborador: *"Pra registrar no painel do time, qual desses é
você: Alexandra, Eduarda, Dutra, Freitas, Gustavo, Tiele, Thalia ou Yara?"*
Salve a resposta (exatamente um dos 8 nomes) nesse arquivo:

```bash
mkdir -p "$HOME/.aegro-task-status"
echo -n "<Nome>" > "$HOME/.aegro-task-status/pessoa.txt"
```

Nas próximas sessões, leia esse arquivo em vez de perguntar de novo.

## Fluxo em cada tarefa

Considere "tarefa relevante" qualquer pedido de trabalho real do colaborador
(rodar um comando `aegro`, editar algo, gerar um relatório etc.) — não
registre perguntas triviais de esclarecimento.

Identifique, no início da tarefa:

- `PESSOA`: do arquivo local (ver acima).
- `ASSINATURA`: tente inferir do contexto da conversa/comandos (ex: um
  `netsuite_id` ou id de fazenda/conta já mencionado). Se não ficar claro,
  **pergunte** ao colaborador o ID da assinatura antes de registrar — nunca
  use o nome do cliente.
- `TAREFA_ID`: um id curto e único, por exemplo 6 caracteres aleatórios
  (`abc123`).
- `TAREFA_DESC`: descrição curta (até ~70 caracteres) do que foi pedido, em
  português simples, sem dado sensível.
- `TAREFA_TEXTO`: `"$TAREFA_DESC ⟦id:$TAREFA_ID⟧"` — o marcador `⟦id:...⟧`
  é obrigatório no final; ele conecta os eventos de início/fim/erro da mesma
  tarefa no painel. Não remova nem altere esse marcador.

Guarde `TAREFA_ID`, `ASSINATURA` e `TAREFA_TEXTO` em memória (nesta sessão)
para reusar exatamente iguais nos eventos seguintes da mesma tarefa.

### 1. No início da tarefa

**Use sempre Python (`python3 -c ...`) para enviar, nunca `curl
--data-urlencode` direto no shell** — em ambientes Windows/Git Bash isso
corrompe acento e o marcador `⟦id:...⟧` silenciosamente (o Forms chega a
rejeitar com HTTP 400 quando o valor de status vem corrompido). Escreva o
texto com os caracteres normais (não precisa escapar nada) dentro do próprio
código Python — é o Python que cuida da codificação UTF-8 corretamente:

```bash
python3 -c "
import urllib.request, urllib.parse
url = '$FORM_POST_URL'
data = {
    '$ENTRY_EQUIPE': '$PESSOA',
    '$ENTRY_ASSINATURA': '$ASSINATURA',
    '$ENTRY_TAREFA': '$TAREFA_TEXTO',
    '$ENTRY_STATUS': 'Iniciada',
}
body = urllib.parse.urlencode(data).encode('utf-8')
req = urllib.request.Request(url, data=body, method='POST')
urllib.request.urlopen(req, timeout=15)
"
```

### 2. Ao concluir a tarefa com sucesso

Mesma requisição, **mesmo `TAREFA_TEXTO`** (com o mesmo id embutido), trocando
só o status:

```
'$ENTRY_STATUS': 'Concluída',
```

### 3. Se o comando esbarrar numa barreira estrutural da CLI

Ou seja: o comando não existe, a flag não é suportada, `aegro --help` não
mostra nada equivalente, ou a versão instalada não tem a funcionalidade — não
confunda com um erro de negócio comum (ex: "fazenda não encontrada" por
digitação errada não conta; "esse comando não existe nesta versão do CLI"
conta). Quando isso acontecer, registre (mesmo formato Python acima, mesmo
`TAREFA_TEXTO` de novo) com:

```
'$ENTRY_STATUS': 'Não executada/Erro CLI',
```

Não é preciso descrever o motivo no
formulário — só a categorização de status já é suficiente para contabilizar
no painel.

## Se o registro falhar (sem internet, formulário fora do ar)

1. Tente uma vez mais.
2. Se falhar de novo, **não insista** e **não interrompa** a resposta ao
   colaborador. Termine sua resposta normal com uma linha discreta, por
   exemplo:
   > _(obs: não consegui registrar o status agora — sem conexão; a tarefa em
   > si foi concluída normalmente)_

## Resumo do que cada evento contém

| campo        | obrigatório | conteúdo                                              |
| ------------ | ----------- | ------------------------------------------------------ |
| pessoa       | sim         | um dos 8 nomes válidos                                  |
| assinatura   | sim         | id/código do cliente — nunca o nome                    |
| tarefa       | sim         | descrição curta + `⟦id:...⟧` embutido                  |
| status       | sim         | `Iniciada` \| `Concluída` \| `Não executada/Erro CLI`   |
