"""Regenerates the team status dashboard HTML from the Form's response CSV.

Run from anywhere inside the repo checkout:
    python3 dashboard/build.py <events_csv_path> [output_path]

<events_csv_path> is a CSV export of the Google Form's response sheet
("Carimbo de data/hora,Equipe ,Assinatura (...),Tarefa,Status"), written by
the caller — this script never talks to Google itself. The scheduled
routine fetches it via the Google Drive connector's download_file_content
tool (exportMimeType text/csv) and writes it to disk before calling this.

Reads:
  - dashboard/template.html
  - dashboard/fonts/*.ttf.b64.txt
  - <events_csv_path>

Writes the finished, self-contained HTML to `output_path` (default:
/tmp/team-task-status-dashboard.html).
"""
import csv
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

dashboard_dir = Path(__file__).resolve().parent

template = (dashboard_dir / "template.html").read_text(encoding="utf-8")

def read_b64(name):
    return (dashboard_dir / "fonts" / name).read_text(encoding="ascii")

archivo_b64 = read_b64("Archivo.ttf.b64.txt")
plex_reg_b64 = read_b64("IBMPlexMono-Regular.ttf.b64.txt")
plex_med_b64 = read_b64("IBMPlexMono-Medium.ttf.b64.txt")

if len(sys.argv) < 2:
    print("uso: python3 build.py <events_csv_path> [output_path]", file=sys.stderr)
    sys.exit(1)

csv_path = Path(sys.argv[1])
output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp/team-task-status-dashboard.html")

# marcador embutido no fim da descrição da tarefa, ex: "Corrigir X ⟦id:a1b2c3⟧"
TASK_ID_RE = re.compile(r"\s*⟦id:([^⟧]+)⟧\s*$")

events = []
if csv_path.exists():
    with csv_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    for row in rows[1:]:  # pula o cabeçalho
        if len(row) < 5 or not any(row):
            continue
        ts_raw, pessoa, assinatura, tarefa_raw, status = row[0], row[1], row[2], row[3], row[4]
        m = TASK_ID_RE.search(tarefa_raw)
        if not m:
            # sem marcador de id — não dá pra ligar início/fim/erro com segurança, pula
            continue
        tarefa_id = m.group(1)
        tarefa = TASK_ID_RE.sub("", tarefa_raw).strip()
        try:
            dt = datetime.strptime(ts_raw.strip(), "%d/%m/%Y %H:%M:%S")
            ts_iso = dt.strftime("%Y-%m-%dT%H:%M:%S-03:00")  # planilha em horário de Brasília (sem DST)
        except ValueError:
            ts_iso = None
        events.append({
            "ts": ts_iso,
            "pessoa": pessoa.strip(),
            "assinatura": assinatura.strip(),
            "tarefa": tarefa,
            "tarefa_id": tarefa_id,
            "status": status.strip(),
        })
else:
    print(f"aviso: {csv_path} não existe — gerando painel com zero eventos", file=sys.stderr)

generated_at = subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip()

out = template
out = out.replace("__ARCHIVO_B64__", archivo_b64)
out = out.replace("__PLEXMONO_REGULAR_B64__", plex_reg_b64)
out = out.replace("__PLEXMONO_MEDIUM_B64__", plex_med_b64)
out = out.replace("__EVENTS_JSON__", json.dumps(events, ensure_ascii=False))
out = out.replace("__GENERATED_AT__", json.dumps(generated_at))

output_path.write_text(out, encoding="utf-8")
print(f"wrote {output_path} ({len(out)} bytes), {len(events)} events, generated_at={generated_at}")
