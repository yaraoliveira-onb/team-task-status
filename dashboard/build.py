"""Regenerates the team status dashboard HTML from the raw JSONL event log.

Run from anywhere inside the repo checkout:
    python3 dashboard/build.py [output_path]

Reads:
  - dashboard/template.html
  - dashboard/fonts/*.ttf.b64.txt
  - data/status.jsonl

Writes the finished, self-contained HTML to `output_path` (default:
/tmp/team-task-status-dashboard.html) — deliberately OUTSIDE the repo so this
job never needs to commit or push anything back.
"""
import json
import subprocess
import sys
from pathlib import Path

dashboard_dir = Path(__file__).resolve().parent
repo_root = dashboard_dir.parent

template = (dashboard_dir / "template.html").read_text(encoding="utf-8")

def read_b64(name):
    return (dashboard_dir / "fonts" / name).read_text(encoding="ascii")

archivo_b64 = read_b64("Archivo.ttf.b64.txt")
plex_reg_b64 = read_b64("IBMPlexMono-Regular.ttf.b64.txt")
plex_med_b64 = read_b64("IBMPlexMono-Medium.ttf.b64.txt")

jsonl_path = repo_root / "data" / "status.jsonl"
events = []
if jsonl_path.exists():
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"skipping malformed line: {line[:80]}", file=sys.stderr)

generated_at = subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip()

out = template
out = out.replace("__ARCHIVO_B64__", archivo_b64)
out = out.replace("__PLEXMONO_REGULAR_B64__", plex_reg_b64)
out = out.replace("__PLEXMONO_MEDIUM_B64__", plex_med_b64)
out = out.replace("__EVENTS_JSON__", json.dumps(events, ensure_ascii=False))
out = out.replace("__GENERATED_AT__", json.dumps(generated_at))

output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/team-task-status-dashboard.html")
output_path.write_text(out, encoding="utf-8")
print(f"wrote {output_path} ({len(out)} bytes), {len(events)} events, generated_at={generated_at}")
