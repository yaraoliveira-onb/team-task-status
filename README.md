# team-task-status

Registro interno de status de tarefas do time (via skill `onboarding-task-status`) —
alimenta o painel de acompanhamento. Repositório privado, contém apenas
metadados (pessoa, projeto, tarefa, status), sem dados sensíveis.

## Como instalar (por pessoa)

1. Peça acesso de colaborador a este repositório (Settings → Collaborators) a
   quem administra o repo.
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
