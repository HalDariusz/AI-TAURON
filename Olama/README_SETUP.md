# 👉 START TUTAJ — instalacja i pierwsze uruchomienie

Dostałeś pakiet dający dostęp do modeli LLM (Ollama) na serwerze **HAL** —
**bez logowania się na serwer**. Wszystko idzie przez bezpieczny tunel SSH,
ograniczony wyłącznie do Ollamy.

Ten plik = jak zacząć. Pełna instrukcja obsługi jest w **`README_USE.md`**.

---

## Co jest w paczce

| Plik | Do czego |
| --- | --- |
| `connect.sh` | Uruchamianie na **Linux / macOS** |
| `connect.command` | **macOS** — to samo, klikalne w Finderze |
| `connect.ps1` / `connect.bat` | **Windows** — `.bat` do dwukliku |
| `ui/chat.html` | Interfejs czatu w przeglądarce |
| `id_ed25519_ollama` | Twój klucz dostępu — **trzymaj prywatnie** |
| `README_USE.md` | Pełny handbook (CLI, GUI, API, Python) |

---

## Czego potrzebujesz

- **`ssh`** — jest domyślnie na Linux, macOS i Windows 10/11.
  (Windows: jeśli brak, Ustawienia → Aplikacje → Funkcje opcjonalne → *OpenSSH Client*.)
- **Python** — tylko jeśli chcesz czat w przeglądarce (GUI). Linux/macOS mają go
  zwykle domyślnie; Windows: <https://www.python.org>.
- **`ollama`** (opcjonalnie) — tylko dla czatu w terminalu. Instalacja:
  <https://ollama.com/download>. Modele zostają na HAL — nic nie pobierasz.

> Do samego `curl`/API nie potrzebujesz **niczego** poza `ssh`.

---

## Uruchomienie — 2 kroki

### Linux

```bash
cd Olama                 # katalog z tej paczki
chmod +x connect.sh      # tylko raz
./connect.sh ui          # GUI w przeglądarce  (albo: ./connect.sh chat — terminal)
```

### macOS

1. Rozpakuj i wejdź do folderu.
2. Dwuklik na **`connect.command`**.
   - Przy pierwszym razie, gdy system zablokuje („niezidentyfikowany deweloper"):
     **prawy klik → Otwórz → Otwórz**.
3. Otworzy się terminal, tunel wstanie. Do GUI: w terminalu `./connect.sh ui`.

### Windows

1. Rozpakuj folder (**Wypakuj wszystko** — nie uruchamiaj z podglądu ZIP).
2. Dwuklik na **`connect.bat`**.
   - SmartScreen może ostrzec → **Więcej informacji → Uruchom mimo to**.
3. Do czatu w przeglądarce: `connect.bat ui`. Do terminala: `connect.bat chat`.

---

## Co dalej

Po połączeniu masz do wyboru (szczegóły w `README_USE.md`):

- **Przeglądarka (GUI):** `... ui` — czat jak ChatGPT.
- **Terminal (CLI):** `... chat` — wymaga klienta `ollama`.
- **API / Python / curl:** endpoint `http://127.0.0.1:11434`.

Rozłączenie w każdej chwili: `... stop`.

---

## Ważne / bezpieczeństwo

- 🔑 Plik `id_ed25519_ollama` to **klucz prywatny** — nie wysyłaj go dalej, nie
  wrzucaj do repo/chmury. Daje dostęp **wyłącznie** do Ollamy (port 11434) — bez
  shella, bez innych usług.
- Komunikat `This account is currently not available.` przy łączeniu jest
  **normalny** (konto nie ma powłoki) — tunel i tak działa.
- Problemy z dostępem (klucz, konto) → pisz do **Darka**.

Miłego korzystania! 🦙
