# team-task-status

Código de apoio ao painel de status de tarefas do time (skill
`onboarding-task-status` + gerador do painel). Este repositório é público,
mas isso agora é inofensivo: ele só contém **código** (a skill e o script de
build do painel), nunca dado de tarefa.

Os dados em si (quem, assinatura, tarefa, status) **não ficam aqui** — vão
direto, via um Google Formulário, para uma planilha privada. Só quem tem
acesso à planilha (e a rotina agendada, via conector Google Drive) consegue
ler esses dados.

## Como instalar a skill (por pessoa)

1. Copie o conteúdo de [`skill/onboarding-task-status.md`](skill/onboarding-task-status.md)
   para a pasta de skills pessoais do seu Claude Code
   (`~/.claude/skills/onboarding-task-status.md`, ou o equivalente Windows
   `%USERPROFILE%\.claude\skills\onboarding-task-status.md`).
2. Ative digitando `/onboarding-task-status` no início de cada sessão de
   trabalho. Na primeira vez, ela pergunta qual das 8 pessoas do time você é
   e guarda a resposta localmente — não precisa de conta GitHub nem login.

## Estrutura

- `skill/onboarding-task-status.md` — a skill que cada colaborador instala;
  envia os eventos direto pro Google Formulário (sem git, sem GitHub).
- `dashboard/template.html` — layout do painel (fontes embutidas, CSS, JS de
  agregação).
- `dashboard/build.py` — lê um CSV de respostas do formulário (fornecido
  pela rotina agendada, via conector Google Drive) e gera o
  `dashboard.html` final, publicado como Artifact.

## Nunca commitar aqui

Dado de tarefa (nome, assinatura, status etc.) não pertence a este repo —
ele vai para a planilha do Google Forms. Aqui só entra código.
