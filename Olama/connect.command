#!/usr/bin/env bash
# =============================================================================
#  Ollama @ HAL — launcher dla macOS (dwuklik w Finderze)
#  Cała logika jest w connect.sh — ten plik tylko ustawia katalog i go odpala.
# =============================================================================
cd "$(dirname "$0")" || exit 1
chmod +x ./connect.sh 2>/dev/null || true
./connect.sh "${1:-connect}"

echo
echo "Okno możesz zamknąć — tunel działa w tle."
echo "Rozłączenie:  ./connect.sh stop"
