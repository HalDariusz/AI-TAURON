# Ollama @ HAL — dostęp przez tunel SSH

Ten folder daje dostęp do modeli LLM (Ollama) działających na serwerze **HAL**,
bez logowania się na serwer. Wszystko idzie przez zaszyfrowany tunel SSH,
ograniczony **wyłącznie** do portu Ollamy — nie ma dostępu do shella ani niczego innego.

## Zawartość

| Plik | System | Do czego |
| ---- | ------ | -------- |
| `connect.sh` | Linux / macOS | Główny skrypt — łączy, czatuje, rozłącza |
| `connect.command` | macOS | To samo, ale klikalne w Finderze |
| `connect.ps1` | Windows | Odpowiednik dla PowerShell |
| `connect.bat` | Windows | Dwuklik — uruchamia `connect.ps1` |
| `ui/chat.html` | — | Interfejs czatu w przeglądarce (uruchamiany przez `connect ... ui`) |
| `id_ed25519_ollama` | — | Klucz prywatny (nie udostępniaj dalej!) |

## Wymagania

- **Linux / macOS**: `ssh` i `curl` (są domyślnie).
- **Windows 10/11**: wbudowany klient OpenSSH (zwykle jest; jak nie —
  Ustawienia → Aplikacje → Funkcje opcjonalne → *OpenSSH Client*).
- Opcjonalnie [`ollama`](https://ollama.com/download) — żeby używać poleceń `ollama run ...`.
  Bez niego i tak zadziała `curl` / dowolny klient wskazujący na `http://127.0.0.1:11434`.

## Użycie — jeden klik

**Linux:**

```bash
chmod +x connect.sh      # tylko raz, po rozpakowaniu
./connect.sh             # łączy i pokazuje jak używać
./connect.sh ui          # łączy i otwiera czat w przeglądarce (GUI)
./connect.sh chat        # łączy i od razu czat w terminalu (CLI)
./connect.sh stop        # rozłącz
./connect.sh status      # stan tunelu
```

**macOS:** dwuklik na **`connect.command`** w Finderze (albo `./connect.sh` w Terminalu).
Za pierwszym razem, gdy Gatekeeper zablokuje: prawy klik → *Otwórz* → *Otwórz*.

**Windows:** dwuklik na **`connect.bat`** (albo w PowerShell: `.\connect.ps1`).
Komendy: `connect.bat chat`, `connect.bat stop`, `connect.bat status`.

> Wszystkie warianty robią to samo — otwierają ten sam tunel. Wybierz plik dla swojego systemu.

## Jak to działa

`connect.sh` otwiera tunel:

```text
twój_komputer:127.0.0.1:11434  →  (SSH)  →  HAL:127.0.0.1:11434 (Ollama)
```

Po połączeniu Ollama na HAL wygląda jakby działała lokalnie:

```bash
ollama run SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M
curl http://127.0.0.1:11434/api/tags
```

Jeśli masz **własną** Ollamę na `11434`, skrypt automatycznie wybierze kolejny wolny
port (np. `11435`) i pokaże, jak go użyć:
`OLLAMA_HOST=127.0.0.1:11435 ollama run ...`

## Dostępne modele

- `SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M`
- `SpeakLeash/bielik-4.5b-v3.0-instruct:FP16`
- `qwen2.5:7b`
- `deepseek-r1:latest`
- `deepseek-r1:671b`
- `gpt-oss:120b`
- `llama4:latest`
- `llama4-8k:latest`

## Uwagi / bezpieczeństwo

- Klucz `id_ed25519_ollama` jest **prywatny** — trzymaj go tylko u siebie.
- Klucz pozwala **wyłącznie** na tunel do Ollamy (port 11434). Bez shella, bez innych portów.
- Komunikat `This account is currently not available.` przy łączeniu jest **normalny**
  — konto nie ma powłoki, tunel i tak działa.
- Dostęp można w każdej chwili odebrać (po stronie HAL: `sudo userdel -r llmtunnel`).
