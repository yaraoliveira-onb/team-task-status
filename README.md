# team-task-status

Registro interno de status de tarefas do time (via skill `onboarding-task-status`) —
alimenta o painel de acompanhamento.

⚠️ **Este repositório é público** (necessário para a rotina agendada de refresh
do painel conseguir ler os dados). Por isso, `data/status.jsonl` deve conter
**apenas metadado não sensível**: nome da pessoa, projeto, descrição curta da
tarefa e status. Nunca dado de cliente, credencial, ou conteúdo de arquivo —
ver regras completas em [`skill/onboarding-task-status.md`](skill/onboarding-task-status.md).
Nomes de colaboradores ficam visíveis publicamente neste repo — está ciente
disso quem decidiu tornar o repo público.

## Como instalar (por pessoa)

1. Peça acesso de colaborador a este repositório (Settings → Collaborators) a
   quem administra o repo, para conseguir dar push nos próprios eventos.
2. Copie o conteúdo de [`skill/onboarding-task-status.md`](skill/onboarding-task-status.md)
   para a pasta de skills pessoais do seu Claude Code.
3. Ative a skill no início de cada sessão de trabalho.

## Estrutura

- `skill/onboarding-task-status.md` — a skill que cada colaborador instala.
- `data/status.jsonl` — um evento por linha (`iniciada` / `concluida` / `erro`),
  append-only. Não editar manualmente.

## Nunca commitar aqui

Senhas, tokens, dados de clientes, ou qualquer conteúdo além do metadado de
status descrito na skill.
