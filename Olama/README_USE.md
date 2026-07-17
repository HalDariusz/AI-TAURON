# Ollama @ HAL — handbook użytkownika

Prosty przewodnik: jak połączyć się z modelami LLM na serwerze HAL i jak ich używać
z terminala, przez API albo z Pythona. Nie musisz nic wiedzieć o serwerze — łączysz
się jednym skryptem i gadasz z modelem tak, jakby działał na Twoim laptopie.

---

## 1. Czym jest Ollama?

**Ollama** to lokalny „silnik" do uruchamiania modeli językowych (LLM) — coś jak
ChatGPT, tylko że model działa na naszym serwerze, dane nie wychodzą na zewnątrz.

- Rozmawiasz z modelem w terminalu (`ollama run ...`) **albo**
- przez zwykłe HTTP API (`curl`, Python, dowolny język) na `http://127.0.0.1:11434`.

Na HAL jest kilka modeli — od małych i szybkich, po duże i „mądre" (patrz sekcja 7).

---

## 2. Połączenie (raz)

W tym folderze wybierz plik dla swojego systemu:

- **Linux:** `chmod +x connect.sh` (raz), potem `./connect.sh`
- **macOS:** dwuklik na `connect.command` (albo `./connect.sh` w Terminalu)
- **Windows:** dwuklik na `connect.bat` (albo `.\connect.ps1` w PowerShell)

Zobaczysz `✅ Połączono. Ollama dostępna na http://127.0.0.1:11434`.
Od tej chwili wszystkie polecenia poniżej działają. Wszystkie warianty robią to samo.

> Komunikat `This account is currently not available.` przy łączeniu jest **normalny**
> — konto nie ma powłoki, tunel i tak działa.

Rozłączenie: `connect stop` (`./connect.sh stop`, `connect.bat stop`).
Stan tunelu: `... status`.

---

## 3. Interfejs w przeglądarce (GUI) — najłatwiej 🖥️

Wolisz klikać zamiast pisać w terminalu? Jest gotowy czat w przeglądarce
(wygląda jak ChatGPT: wybór modelu, historia rozmowy, streaming odpowiedzi).

**Jak uruchomić — jedna komenda:**

```bash
./connect.sh ui          # macOS: connect.command ui | Windows: connect.bat ui
```

To polecenie:

1. otwiera tunel do HAL,
2. startuje **mały lokalny serwer** (potrzebny — przeglądarka blokuje `file://`),
3. otwiera stronę czatu w Twojej przeglądarce.

Zobaczysz adres w stylu `http://127.0.0.1:8800/chat.html?api=11434` — jeśli
przeglądarka nie otworzy się sama, wklej ten adres ręcznie.

**Wymaga:** Pythona (do lokalnego serwera; Linux/macOS mają go zwykle domyślnie,
na Windows zainstaluj z <https://www.python.org>). Nie masz Pythona? Użyj czatu w
terminalu (sekcja 4).

W interfejsie:

- wybierz **model** z listy u góry (domyślnie Bielik 11B),
- `⚙︎ System` — ustaw rolę modelu (np. „Jesteś zwięzłym analitykiem"),
- `🗑 Wyczyść` — nowa rozmowa,
- **Enter** wysyła, **Shift+Enter** = nowa linia.

Zamknięcie: `./connect.sh stop` (ubija tunel i serwer).

> ⚠️ Nie otwieraj `chat.html` przez podwójne kliknięcie (adres `file://`) — Ollama
> odrzuci takie żądanie (CORS). Zawsze uruchamiaj przez `./connect.sh ui`.

---

## 4. Czat w terminalu (CLI) ⭐

Najwygodniej rozmawiać z modelem jak w ChatGPT, tylko w terminalu. Do tego
potrzebujesz **klienta `ollama`** u siebie (sam klient — modele zostają na HAL,
nic się nie pobiera).

**Krok 1 — zainstaluj klienta `ollama` (raz):**

```bash
# Linux / macOS:
curl -fsSL https://ollama.com/install.sh | sh
# macOS (Homebrew) alternatywnie:  brew install ollama
# Windows: pobierz instalator z https://ollama.com/download
```

**Krok 2 — połącz się i wejdź w czat (jedna komenda):**

```bash
./connect.sh chat        # macOS: connect.command chat | Windows: connect.bat chat
```

`chat` otwiera tunel do HAL **i** od razu uruchamia rozmowę z Bielikiem.
Równoważnie ręcznie (gdy tunel już stoi):

```bash
ollama run SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M
```

**Jak wygląda rozmowa:**

```text
>>> Napisz krótki e-mail do klienta o opóźnieniu dostawy o 3 dni.
(model odpowiada...)

>>> A teraz bardziej formalnie.
(model pamięta kontekst rozmowy)

>>> /bye
```

**Przydatne komendy w czacie:**

- `Enter` — wyślij pytanie; model pamięta całą rozmowę (kontekst),
- wieloliniowy tekst — otocz potrójnym cudzysłowem `"""` … `"""`,
- `/set system "Jesteś zwięzłym analitykiem."` — ustaw rolę/zachowanie modelu,
- `/clear` — wyczyść kontekst rozmowy,
- `/?` — pełna lista komend,
- `/bye` — wyjście z czatu (tunel zostaje; zamkniesz go przez `connect stop`).

**Zmiana modelu w locie** — po prostu odpal inny:

```bash
ollama run qwen2.5:7b          # szybki, do kodu
ollama run deepseek-r1:latest  # do trudniejszego rozumowania
```

> Jeśli masz **własną** lokalną Ollamę, tunel pójdzie na inny port (np. 11435).
> Wtedy przed komendą dodaj `OLLAMA_HOST=127.0.0.1:11435` — dokładny port pokaże
> `./connect.sh status`.

---

## 5. Polecenia CLI (`ollama`)

> Jeśli tunel wystartował na innym porcie niż 11434 (bo masz własną Ollamę),
> poprzedź polecenia `OLLAMA_HOST=127.0.0.1:PORT`. Port pokazuje `connect status`.

```bash
ollama list                       # jakie modele są dostępne
ollama run <model>                # interaktywny czat
ollama run <model> "pytanie"      # jednorazowe pytanie (bez wchodzenia w czat)
ollama ps                         # co jest teraz załadowane w pamięci
```

Przykłady jednorazowe:

```bash
ollama run qwen2.5:7b "Wyjaśnij czym jest mean reversion w 3 zdaniach."
ollama run SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M "Streść ten tekst: ..."
```

---

## 6. API — `curl` (bez instalowania Ollamy)

Ollama wystawia HTTP API. Nie musisz mieć klienta `ollama` — wystarczy `curl`.

**Lista modeli:**

```bash
curl http://127.0.0.1:11434/api/tags
```

**Jednorazowe wygenerowanie tekstu** (`/api/generate`):

```bash
curl http://127.0.0.1:11434/api/generate -d '{
  "model": "SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M",
  "prompt": "Wymień 3 zalety analizy szeregów czasowych.",
  "stream": false
}'
```

**Czat z historią i rolą systemową** (`/api/chat`):

```bash
curl http://127.0.0.1:11434/api/chat -d '{
  "model": "SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M",
  "stream": false,
  "messages": [
    {"role": "system", "content": "Jesteś zwięzłym analitykiem finansowym."},
    {"role": "user", "content": "Co to jest spread bid-ask?"}
  ]
}'
```

> `"stream": false` = cała odpowiedź naraz. Ustaw `true`, żeby dostawać
> odpowiedź token po tokenie (strumień JSON-linii).

**Parametry** (opcjonalne, w polu `"options"`):

```bash
curl http://127.0.0.1:11434/api/generate -d '{
  "model": "qwen2.5:7b",
  "prompt": "Podaj 5 pomysłów.",
  "stream": false,
  "options": { "temperature": 0.2, "num_predict": 300 }
}'
```

- `temperature` — kreatywność (0 = precyzyjnie/powtarzalnie, 0.8 = luźniej),
- `num_predict` — maks. długość odpowiedzi (tokeny),
- `num_ctx` — rozmiar kontekstu (ile tekstu model „widzi").

---

## 7. Dostępne modele — który wybrać?

| Model | Rozmiar | Do czego |
| ----- | ------- | -------- |
| `SpeakLeash/bielik-4.5b-v3.0-instruct:FP16` | mały | **polski**, szybki, proste zadania |
| `SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M` | średni | **polski**, dobry kompromis jakość/szybkość ⭐ |
| `qwen2.5:7b` | mały-średni | szybki, wielojęzyczny, dobry do kodu |
| `llama4:latest` / `llama4-8k:latest` | średni | ogólny, angielski; `8k` = większy kontekst |
| `deepseek-r1:latest` | średni | **reasoning** — pokazuje tok rozumowania |
| `gpt-oss:120b` | duży | mocny ogólny, wolniejszy |
| `deepseek-r1:671b` | **bardzo duży** | najmocniejszy reasoning, **najwolniejszy** 🐢 |

**Praktycznie:**

- Polski tekst (maile, streszczenia, umowy) → **Bielik 11B**.
- Szybkie pytania / kod → `qwen2.5:7b`.
- Trudne zadania logiczne/matematyka → `deepseek-r1` (ale wolniej).
- Duże modele (`120b`, `671b`) ładują się dłużej i liczą wolniej — używaj świadomie.

> Pierwsze uruchomienie danego modelu może chwilę potrwać (ładowanie do pamięci).
> Kolejne odpowiedzi są szybsze, dopóki model siedzi w RAM (`ollama ps`).

---

## 8. Python

**Wariant A — biblioteka `ollama`:**

```bash
pip install ollama
```

```python
from ollama import Client

client = Client(host="http://127.0.0.1:11434")
resp = client.chat(
    model="SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M",
    messages=[{"role": "user", "content": "Wyjaśnij czym jest fuzzy logic."}],
)
print(resp["message"]["content"])
```

**Wariant B — endpoint zgodny z OpenAI** (`pip install openai`):

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")  # klucz dowolny
resp = client.chat.completions.create(
    model="qwen2.5:7b",
    messages=[{"role": "user", "content": "Podaj 3 wskaźniki dla mean-reversion."}],
)
print(resp.choices[0].message.content)
```

> Dzięki temu podłączysz też narzędzia oczekujące „OpenAI API" — wystarczy zmienić
> `base_url` na `http://127.0.0.1:11434/v1`.

---

## 9. Troubleshooting

| Problem | Rozwiązanie |
| ------- | ----------- |
| `connection refused` na 11434 | Tunel nie działa → uruchom `connect` (albo `connect status`) |
| `This account is currently not available.` | To normalne, zignoruj — tunel działa |
| Port 11434 zajęty (masz własną Ollamę) | Skrypt weźmie 11435 — użyj `OLLAMA_HOST=127.0.0.1:11435 ...` |
| `ollama: command not found` | Zainstaluj z <https://ollama.com/download> albo używaj `curl`/Pythona |
| GUI: pusta strona / „Brak połączenia" | Tunel padł — odśwież po `./connect.sh ui`; nie otwieraj `chat.html` jako `file://` |
| GUI: `python: command not found` | Zainstaluj Pythona albo użyj czatu w terminalu (sekcja 4) |
| Windows: `permissions ... too open` | Uruchom przez `connect.bat` — sam naprawia uprawnienia klucza |
| Model odpowiada bardzo wolno | To duży model (`120b`/`671b`) — wybierz mniejszy |
| Tunel zrywa się po czasie | Uruchom ponownie `connect`; ma keepalive, ale sieć bywa kapryśna |

W razie problemów z dostępem (klucz, konto) — pisz do **Darka**.

---

*Dostęp jest ograniczony wyłącznie do modeli LLM na HAL (port 11434). Miłego korzystania!* 🦙
