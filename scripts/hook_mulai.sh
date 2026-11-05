#!/usr/bin/env bash
# Hook SessionStart: pasang skill otomatis dari katalog/skill.yaml (terkunci ke commit). Diam bila semua sudah ada.
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/..}" || exit 0
PY=.venv/bin/python; [ -x "$PY" ] || PY=python3
out=$(timeout 240 "$PY" -m scripts.pasang_otomatis 2>/dev/null)
case "$out" in *terpasang*|*gagal*|*ditolak*) echo "skill katalog: $out";; esac
exit 0
