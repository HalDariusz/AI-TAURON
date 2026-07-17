#!/usr/bin/env bash
# =============================================================================
#  Ollama @ HAL  —  jeden klik = połączenie
# -----------------------------------------------------------------------------
#  Uruchomienie:
#     ./connect.sh          -> otwiera tunel SSH i pokazuje jak używać
#     ./connect.sh chat     -> otwiera tunel i od razu wchodzi w czat z Bielikiem
#     ./connect.sh stop     -> zamyka tunel
#     ./connect.sh status   -> pokazuje stan tunelu
#
#  Nic nie trzeba instalować w ~/.ssh — klucz leży obok tego skryptu.
# =============================================================================
set -euo pipefail

HOST="95.217.89.69"
SSH_USER="llmtunnel"
REMOTE_PORT=11434
DEFAULT_MODEL="SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEY="$DIR/id_ed25519_ollama"
PIDFILE="$DIR/.tunnel.pid"
PORTFILE="$DIR/.tunnel.port"
UIDIR="$DIR/ui"
UIPIDFILE="$DIR/.ui.pid"

c_ok=$'\033[32m'; c_err=$'\033[31m'; c_inf=$'\033[36m'; c_off=$'\033[0m'
ok(){  printf "%s✅ %s%s\n" "$c_ok"  "$*" "$c_off"; }
err(){ printf "%s❌ %s%s\n" "$c_err" "$*" "$c_off"; }
inf(){ printf "%sℹ️  %s%s\n" "$c_inf" "$*" "$c_off"; }

port_busy(){
  if command -v ss >/dev/null 2>&1; then ss -tln 2>/dev/null | grep -q "[.:]$1 "
  else netstat -an 2>/dev/null | grep -q "[.:]$1 .*LISTEN"; fi
}

tunnel_alive(){ [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; }

stop_tunnel(){
  local killed=0
  # 1) po zapisanym PID
  if [ -f "$PIDFILE" ]; then
    local pid; pid=$(cat "$PIDFILE" 2>/dev/null)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then kill "$pid" 2>/dev/null && killed=1; fi
  fi
  # 2) fallback: ubij ewentualne osierocone tunele do naszego hosta
  local strays; strays=$(pgrep -f "$SSH_USER@$HOST" 2>/dev/null || true)
  if [ -n "$strays" ]; then kill $strays 2>/dev/null && killed=1; fi
  # 3) zatrzymaj lokalny serwer interfejsu WWW, jeśli działał
  if [ -f "$UIPIDFILE" ]; then kill "$(cat "$UIPIDFILE" 2>/dev/null)" 2>/dev/null || true; rm -f "$UIPIDFILE"; fi
  rm -f "$PIDFILE" "$PORTFILE"
  if [ "$killed" = 1 ]; then ok "Tunel zamknięty."; else inf "Tunel nie był uruchomiony."; fi
}

start_tunnel(){
  chmod 600 "$KEY" 2>/dev/null || true

  if tunnel_alive; then
    LOCAL_PORT="$(cat "$PORTFILE" 2>/dev/null || echo "$REMOTE_PORT")"
    inf "Tunel już działa (port $LOCAL_PORT) — używam istniejącego."
    return 0
  fi

  # brak śladu w PIDFILE — posprzątaj ewentualne osierocone tunele,
  # żeby nie mnożyć połączeń i nie blokować portów
  pkill -f "$SSH_USER@$HOST" 2>/dev/null || true

  # znajdź wolny lokalny port (na wypadek własnej Ollamy na 11434)
  LOCAL_PORT=$REMOTE_PORT
  while port_busy "$LOCAL_PORT"; do LOCAL_PORT=$((LOCAL_PORT+1)); done

  inf "Łączę z HAL ($HOST) ..."
  ssh -i "$KEY" \
      -o IdentitiesOnly=yes \
      -o StrictHostKeyChecking=accept-new \
      -o ExitOnForwardFailure=yes \
      -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
      -fN -L "127.0.0.1:$LOCAL_PORT:127.0.0.1:$REMOTE_PORT" "$SSH_USER@$HOST" \
      2>/dev/null || { err "Nie udało się otworzyć tunelu (SSH)."; exit 1; }

  local pid
  pid=$(pgrep -f "127.0.0.1:$LOCAL_PORT:127.0.0.1:$REMOTE_PORT $SSH_USER@$HOST" | head -1 || true)
  [ -n "$pid" ] && echo "$pid" > "$PIDFILE"
  echo "$LOCAL_PORT" > "$PORTFILE"

  # weryfikacja
  local i
  for i in 1 2 3 4 5; do
    if curl -s --max-time 5 "http://127.0.0.1:$LOCAL_PORT/api/tags" >/dev/null 2>&1; then
      ok "Połączono. Ollama dostępna na  http://127.0.0.1:$LOCAL_PORT"
      return 0
    fi
    sleep 1
  done
  err "Tunel otwarty, ale Ollama nie odpowiada. Sprawdź później lub napisz do Darka."
  return 1
}

show_usage_hint(){
  local p; p="$(cat "$PORTFILE" 2>/dev/null || echo "$REMOTE_PORT")"
  echo
  echo "  Jak używać:"
  if [ "$p" = "11434" ]; then
    echo "    ollama run $DEFAULT_MODEL"
  else
    echo "    OLLAMA_HOST=127.0.0.1:$p ollama run $DEFAULT_MODEL"
  fi
  echo "    curl http://127.0.0.1:$p/api/tags        # lista modeli"
  echo
  echo "  Interfejs WWW:  ./connect.sh ui        # czat w przeglądarce"
  echo "  Czat w CLI:     ./connect.sh chat"
  echo "  Rozłączenie:    ./connect.sh stop"
}

open_chat(){
  local p; p="$(cat "$PORTFILE" 2>/dev/null || echo "$REMOTE_PORT")"
  if ! command -v ollama >/dev/null 2>&1; then
    err "Nie znaleziono polecenia 'ollama'. Zainstaluj: https://ollama.com/download"
    show_usage_hint; return 0
  fi
  inf "Otwieram czat z Bielikiem (wyjście: /bye)"
  OLLAMA_HOST="127.0.0.1:$p" ollama run "$DEFAULT_MODEL"
}

open_ui(){
  local p; p="$(cat "$PORTFILE" 2>/dev/null || echo "$REMOTE_PORT")"
  local PY; PY="$(command -v python3 || command -v python || true)"
  if [ -z "$PY" ]; then
    err "Do interfejsu WWW potrzebny jest Python (lokalny serwer). Zainstaluj python3"
    inf "Bez tego użyj czatu w terminalu:  ./connect.sh chat"
    return 1
  fi
  if [ ! -f "$UIDIR/chat.html" ]; then err "Brak pliku ui/chat.html"; return 1; fi

  # jeśli serwer UI już działa — nie startuj drugiego
  local uiport
  if [ -f "$UIPIDFILE" ] && kill -0 "$(cat "$UIPIDFILE" 2>/dev/null)" 2>/dev/null; then
    uiport="$(cat "$DIR/.ui.port" 2>/dev/null || echo 8800)"
  else
    uiport=8800
    while port_busy "$uiport"; do uiport=$((uiport+1)); done
    ( cd "$UIDIR" && exec "$PY" -m http.server "$uiport" --bind 127.0.0.1 ) >/dev/null 2>&1 &
    echo $! > "$UIPIDFILE"; echo "$uiport" > "$DIR/.ui.port"
    sleep 1
  fi

  local url="http://127.0.0.1:$uiport/chat.html?api=$p"
  ok "Interfejs WWW: $url"
  if   command -v xdg-open >/dev/null 2>&1; then xdg-open "$url" >/dev/null 2>&1 &
  elif command -v open     >/dev/null 2>&1; then open "$url" >/dev/null 2>&1 &
  else inf "Otwórz ten adres w przeglądarce: $url"; fi
}

case "${1:-connect}" in
  stop|down|disconnect) stop_tunnel ;;
  status)
    if tunnel_alive; then ok "Tunel działa (port $(cat "$PORTFILE" 2>/dev/null), pid $(cat "$PIDFILE"))"
    else inf "Tunel nie działa."; fi ;;
  chat)    start_tunnel && open_chat ;;
  ui|web)  start_tunnel && open_ui ;;
  connect|"") start_tunnel && show_usage_hint ;;
  *) echo "Użycie: $0 [connect|chat|ui|stop|status]"; exit 1 ;;
esac
