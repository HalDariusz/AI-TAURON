"""AlICjA — Ciocia ALA — Compliance Dashboard."""

from __future__ import annotations

import os
from datetime import datetime

import httpx
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# --- Page config ---
st.set_page_config(
    page_title="Ciocia ALA — AlICjA",
    page_icon="👩‍⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Main header */
    .ala-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .ala-header h1 { margin: 0; font-size: 2rem; }
    .ala-header p { margin: 0.3rem 0 0 0; opacity: 0.85; font-size: 0.95rem; }

    /* Severity badges */
    .badge-critical { background: #dc3545; color: white; padding: 2px 10px;
                      border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
    .badge-high { background: #fd7e14; color: white; padding: 2px 10px;
                  border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
    .badge-medium { background: #ffc107; color: #333; padding: 2px 10px;
                    border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
    .badge-low { background: #28a745; color: white; padding: 2px 10px;
                 border-radius: 12px; font-size: 0.8rem; font-weight: 600; }

    /* Cards */
    .metric-card {
        background: #f8f9fa;
        border-left: 4px solid #2d6a9f;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.8rem;
    }
    .metric-card h3 { margin: 0; font-size: 1.8rem; color: #1e3a5f; }
    .metric-card p { margin: 0; color: #666; font-size: 0.85rem; }

    /* Finding card */
    .finding-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        background: white;
    }

    /* Status indicators */
    .status-ok { color: #28a745; }
    .status-fail { color: #dc3545; }

    /* Sidebar branding */
    [data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

SEVERITY_ICONS = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
SEVERITY_LABELS = {
    "critical": "Krytyczne",
    "high": "Wysokie",
    "medium": "Średnie",
    "low": "Niskie",
}
DOC_TYPE_LABELS = {"legal_act": "📜 Akt prawny", "owu": "📋 OWU", "contract": "📄 Umowa"}


# --- API helpers ---
def api_get(path: str):
    try:
        resp = httpx.get(f"{API_BASE}{path}", timeout=30.0)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as e:
        st.error(f"Nie mogę połączyć się z serwisem. Szczegóły: {e}")
        return None


def api_post(path: str, **kwargs):
    try:
        resp = httpx.post(f"{API_BASE}{path}", timeout=300.0, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as e:
        st.error(f"Wystąpił błąd podczas przetwarzania. Szczegóły: {e}")
        return None


# --- Sidebar ---
with st.sidebar:
    st.markdown("### 👩‍⚖️ Ciocia ALA")
    st.caption("AlICjA — AI Context Analisator")
    st.markdown("---")

    page = st.radio(
        "Menu",
        ["🏠 Start", "📤 Dodaj dokument", "🔍 Analiza", "📊 Raporty", "🔗 Blockchain", "⚙️ Status"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("v0.1.0 MVP • on-premise")


# --- Header ---
def render_header():
    st.markdown("""
    <div class="ala-header">
        <h1>👩‍⚖️ Ciocia ALA</h1>
        <p>AlICjA — AI Context Analisator | Automatyczna analiza zgodności umów</p>
    </div>
    """, unsafe_allow_html=True)


# ========================
# PAGE: Start
# ========================
if page == "🏠 Start":
    render_header()

    # --- Hero section ---
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 0.5rem 0;">
        <span style="font-size: 4rem;">👩‍⚖️</span>
        <h2 style="margin: 0.3rem 0;">Cześć! Jestem Ciocia ALA</h2>
        <p style="font-size: 1.1rem; color: #555; max-width: 600px; margin: 0 auto;">
            Twoja asystentka ds. zgodności regulacyjnej.<br>
            Pomagam <strong>szybko i pewnie</strong> sprawdzić,
            czy Wasze umowy z klientami są zgodne z przepisami.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # --- What I do — 3 columns ---
    st.markdown("### Co dla Ciebie zrobię?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="font-size: 2rem; text-align: center;">🔍</h3>
            <p style="text-align: center;"><strong>Znajdę niezgodności</strong></p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(
            "Przeczytam każdą klauzulę Twojej umowy i porównam ją "
            "z aktualnym Prawem energetycznym, ustawą konsumencką "
            "i decyzjami URE. Jeśli coś jest nie tak — powiem Ci "
            "**co konkretnie** i **który przepis** jest naruszony."
        )

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="font-size: 2rem; text-align: center;">💡</h3>
            <p style="text-align: center;"><strong>Zaproponuję poprawki</strong></p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(
            "Nie zostawiam Cię z samą listą problemów. "
            "Do każdej niezgodności dostajesz **konkretną rekomendację** "
            "— jak zmienić klauzulę, żeby była zgodna z prawem. "
            "Oszczędzasz godziny pracy prawnika."
        )

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="font-size: 2rem; text-align: center;">🔗</h3>
            <p style="text-align: center;"><strong>Potwierdzę to w blockchain</strong></p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(
            "Każdy raport jest rejestrowany w Hyperledger Fabric "
            "— niezmienny dowód, że analiza została wykonana, "
            "kiedy i z jakim wynikiem. **Idealny audit trail** "
            "dla kontroli wewnętrznej i zewnętrznej."
        )

    st.markdown("---")

    # --- How it works — step by step ---
    st.markdown("### Jak to działa? 4 proste kroki")

    steps = [
        (
            "1️⃣",
            "Wgraj dokument",
            "PDF, DOCX lub TXT — umowę, OWU, albo akt prawny. "
            "Ja go przeczytam i podzielę na klauzule.",
        ),
        (
            "2️⃣",
            'Kliknij "Analizuj"',
            "Porównam każdą klauzulę z bazą przepisów. "
            "Używam polskiego modelu AI (Bielik), wytrenowanego "
            "na tekstach prawnych.",
        ),
        (
            "3️⃣",
            "Przeczytaj raport",
            "Dostajesz listę niezgodności z kolorami priorytetów: "
            "🔴 krytyczne, 🟠 wysokie, 🟡 średnie, 🟢 OK. "
            "Każda z opisem i rekomendacją.",
        ),
        (
            "4️⃣",
            "Zweryfikuj w blockchain",
            "Raport jest na zawsze zapisany w rejestrze. "
            "Nikt go nie zmieni, nie usunie — masz dowód.",
        ),
    ]

    cols = st.columns(4)
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(
                f"<div style='text-align:center; font-size:2rem;'>"
                f"{num}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**{title}**")
            st.caption(desc)

    st.markdown("---")

    # --- Trust & safety ---
    st.markdown("### Dlaczego możesz mi zaufać?")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        **🔒 Twoje dane nie wychodzą na zewnątrz**

        Cały system działa na Waszym serwerze (on-premise).
        Żadna umowa, żadne dane klientów nigdy nie trafiają
        do chmury, internetu, ani żadnego zewnętrznego API.
        Spełniam wymagania RODO w 100%.

        **🤖 Nie zastępuję prawnika — pomagam mu**

        Jestem narzędziem wspierającym. Wskazuję potencjalne
        problemy, ale ostateczna decyzja zawsze należy do
        człowieka. Traktuję moje wyniki jako punkt wyjścia
        do dalszej weryfikacji.
        """)

    with col_b:
        st.markdown("""
        **📊 Każdy wynik jest mierzalny**

        Wszystkie eksperymenty logowane w MLflow.
        Wiesz jaki model, jaki prompt i jakie parametry
        wygenerowały dany raport. Pełna powtarzalność
        i porównywalność analiz w czasie.

        **⚡ Minuty zamiast godzin**

        Ręczna rewizja jednego OWU to godziny pracy prawnika.
        Ja robię to w kilka minut — i nic mi nie umknie,
        bo sprawdzam **każdą** klauzulę vs. **każdy** przepis
        z bazy wiedzy.
        """)

    st.markdown("---")

    # --- Quick stats ---
    reports = api_get("/reports?limit=100")
    documents = api_get("/documents")

    doc_count = len(documents) if documents else 0
    report_count = len(reports) if reports else 0

    if report_count > 0 or doc_count > 0:
        st.markdown("### 📈 System w liczbach")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📄 Dokumenty", doc_count)
        c2.metric("📊 Raporty", report_count)

        if reports:
            compliant = sum(
                1 for r in reports if r["total_findings"] == 0
            )
            critical = sum(r["critical_count"] for r in reports)
            c3.metric("✅ Zgodne", compliant)
            c4.metric("🔴 Krytyczne", critical)
    else:
        st.info(
            "System jest pusty — zacznij od wgrania aktów prawnych "
            "(📤 Dodaj dokument), a potem umowy do analizy."
        )

    # --- CTA ---
    st.markdown("")
    st.markdown(
        "<div style='text-align: center; padding: 1rem;'>"
        "<em>Gotowa do pracy! Kliknij "
        "<strong>📤 Dodaj dokument</strong> w menu, "
        "żeby zacząć.</em></div>",
        unsafe_allow_html=True,
    )


# ========================
# PAGE: Dodaj dokument
# ========================
elif page == "📤 Dodaj dokument":
    render_header()
    st.subheader("Dodaj dokument do analizy")

    st.info(
        "Wgraj dokument (PDF lub DOCX). Ciocia ALA go przeanalizuje — "
        "wyodrębni klauzule, zindeksuje w bazie wiedzy i przygotuje do analizy compliance."
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded = st.file_uploader(
            "Wybierz plik",
            type=["pdf", "docx", "txt"],
            help="Obsługiwane formaty: PDF, DOCX, TXT",
        )

    with col2:
        doc_type = st.selectbox(
            "Typ dokumentu",
            ["contract", "owu", "legal_act"],
            format_func=lambda x: DOC_TYPE_LABELS[x],
        )
        st.caption({
            "contract": "Umowa szczegółowa z klientem",
            "owu": "Ogólne Warunki Umów / Świadczenia Usług",
            "legal_act": "Ustawa, rozporządzenie, decyzja URE",
        }[doc_type])

    if uploaded:
        st.markdown(f"**Wybrany plik:** `{uploaded.name}` ({uploaded.size / 1024:.0f} KB)")

        if st.button("📤 Prześlij i zaindeksuj", type="primary", use_container_width=True):
            with st.spinner("Ciocia ALA przetwarza dokument... Proszę czekać."):
                result = api_post(
                    "/documents/upload",
                    files={"file": (uploaded.name, uploaded.getvalue())},
                    data={"document_type": doc_type},
                )
            if result:
                st.success(f"Dokument **{result['filename']}** został zaindeksowany!")
                col1, col2 = st.columns(2)
                col1.metric("Chunki", result["chunk_count"])
                col2.code(result["document_id"], language=None)
                st.caption("Zapisz ID dokumentu — będzie potrzebne do uruchomienia analizy.")


# ========================
# PAGE: Analiza
# ========================
elif page == "🔍 Analiza":
    render_header()
    st.subheader("Analiza compliance")

    # Fetch documents list
    documents = api_get("/documents")

    if not documents:
        st.info(
            "Brak dokumentów w systemie. Przejdź do **📤 Dodaj dokument**, "
            "aby wgrać umowę lub OWU do analizy."
        )
    else:
        st.markdown(f"**{len(documents)}** dokumentów w systemie. Wybierz dokument do analizy:")

        # Build options for selectbox
        doc_options = {
            d["id"]: f"{DOC_TYPE_LABELS.get(d['document_type'], '📄')}  {d['filename']}"
            for d in documents
        }

        col_select, col_preview = st.columns([1, 1])

        with col_select:
            selected_id = st.selectbox(
                "Dokument",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
                key="analysis_doc_select",
            )

            # Show selected document info
            if selected_id:
                selected_doc = next((d for d in documents if d["id"] == selected_id), None)
                if selected_doc:
                    st.markdown(f"""
                    | | |
                    |---|---|
                    | **Plik** | `{selected_doc['filename']}` |
                    | **Typ** | {DOC_TYPE_LABELS.get(selected_doc['document_type'], '📄')} |
                    | **Data uploadu** | {selected_doc['uploaded_at'][:10]} |
                    | **ID** | `{selected_id[:12]}...` |
                    """)

                if st.button(
                    "🔍 Uruchom analizę", type="primary", use_container_width=True
                ):
                    with st.spinner(
                        "Ciocia ALA analizuje dokument... To może potrwać kilka minut "
                        "(LLM pracuje na każdej klauzuli)."
                    ):
                        result = api_post(
                            "/analysis/run", json={"document_id": selected_id}
                        )

                    if result:
                        findings = result["total_findings"]
                        if findings == 0:
                            st.success(
                                "✅ Dokument jest **zgodny** z analizowanymi przepisami!"
                            )
                            st.balloons()
                        else:
                            st.warning(f"⚠️ Wykryto **{findings}** niezgodności!")

                        m1, m2, m3 = st.columns(3)
                        m1.metric("Razem", findings)
                        m2.metric("🔴 Krytyczne", result["critical_count"])
                        m3.metric("🟠 Wysokie", result["high_count"])

                        st.markdown("---")
                        st.markdown(f"**ID raportu:** `{result['report_id']}`")

                        if result.get("blockchain_tx_id"):
                            st.success(
                                f"🔗 Raport zarejestrowany w blockchain "
                                f"(TX: `{result['blockchain_tx_id']}`)"
                            )

                        st.caption("Przejdź do 📊 Raporty, aby zobaczyć szczegóły.")

        # Document preview panel
        with col_preview:
            if selected_id:
                st.markdown("#### 📄 Podgląd dokumentu")
                preview = api_get(f"/documents/{selected_id}/preview?max_chunks=8")

                if preview and preview.get("chunks_preview"):
                    chunks = preview["chunks_preview"]
                    st.caption(f"{len(chunks)} chunków (pierwsze fragmenty)")

                    for chunk in chunks:
                        section = chunk.get("section", "")
                        article = chunk.get("article") or ""
                        paragraph = chunk.get("paragraph") or ""
                        label_parts = [s for s in [section, article, paragraph] if s]
                        idx = chunk.get("chunk_index", 0)
                        label = " | ".join(label_parts) if label_parts else f"Chunk #{idx}"

                        with st.expander(f"📋 {label}", expanded=chunk.get("chunk_index", 0) == 0):
                            text = chunk.get("text", "")
                            # Trim context prefix for cleaner display
                            if "\n\n" in text[:100]:
                                prefix, body = text.split("\n\n", 1)
                                st.caption(prefix)
                                st.markdown(body[:400])
                            else:
                                st.markdown(text[:500])
                            if len(chunk.get("text", "")) > 500:
                                st.caption("... (skrócono)")
                elif preview:
                    st.info(
                        "Brak chunków w podglądzie. "
                        "Dokument może nie być jeszcze zaindeksowany."
                    )
                else:
                    st.warning("Nie udało się pobrać podglądu.")


# ========================
# PAGE: Raporty
# ========================
elif page == "📊 Raporty":
    render_header()
    st.subheader("Raporty compliance")

    reports = api_get("/reports")

    if not reports:
        st.info("Brak raportów. Dodaj dokument i uruchom analizę, aby wygenerować raport.")
    else:
        # Summary bar
        total = len(reports)
        ok = sum(1 for r in reports if r["total_findings"] == 0)
        nok = total - ok
        st.markdown(
            f"**{total}** raportów: "
            f"<span class='status-ok'>✅ {ok} zgodnych</span> | "
            f"<span class='status-fail'>⚠️ {nok} z niezgodnościami</span>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        for r in reports:
            findings = r["total_findings"]
            if r["critical_count"] > 0:
                icon = "🔴"
                border_color = "#dc3545"
            elif r["high_count"] > 0:
                icon = "🟠"
                border_color = "#fd7e14"
            elif findings > 0:
                icon = "🟡"
                border_color = "#ffc107"
            else:
                icon = "🟢"
                border_color = "#28a745"

            with st.expander(
                f"{icon} **{r['document_name']}** — "
                f"{findings} niezgodności"
            ):
                try:
                    dt = datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
                    date_str = dt.strftime("%d.%m.%Y %H:%M")
                except (ValueError, TypeError):
                    date_str = r["created_at"]
                st.caption(f"📅 {date_str}")

                full = api_get(f"/reports/{r['id']}")
                if not full:
                    continue

                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Razem", full["total_findings"])
                col2.metric("🔴 Krytyczne", full["critical_count"])
                col3.metric("🟠 Wysokie", full["high_count"])
                col4.metric("🟡 Średnie", full["medium_count"])

                st.markdown(f"**Podsumowanie:** {full['summary']}")
                st.caption(f"Model: `{full['model_name']}` | Prompt: `{full['prompt_version']}`")

                if full["findings"]:
                    st.markdown("---")
                    st.markdown("### Szczegóły niezgodności")

                    for i, finding in enumerate(full["findings"], 1):
                        sev = finding["severity"]
                        icon = SEVERITY_ICONS.get(sev, "⚪")
                        label = SEVERITY_LABELS.get(sev, sev)

                        st.markdown(f"""
                        <div class="finding-card" style="border-left: 4px solid {
                            {'critical': '#dc3545', 'high': '#fd7e14',
                             'medium': '#ffc107', 'low': '#28a745'}.get(sev, '#999')
                        };">
                        <strong>{icon} #{i} — {label}</strong>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"**📜 Naruszony przepis:** {finding['regulation_ref']}")
                        st.markdown(f"**📋 Opis:** {finding['description']}")
                        st.markdown(f"> {finding['clause_text'][:600]}")
                        st.markdown(f"**💡 Rekomendacja:** {finding['recommendation']}")
                        st.markdown("---")
                else:
                    st.success("Dokument jest zgodny z analizowanymi przepisami.")


# ========================
# PAGE: Blockchain
# ========================
elif page == "🔗 Blockchain":
    render_header()
    st.subheader("Rejestr blockchain")

    st.info(
        "Każdy raport compliance jest rejestrowany w Hyperledger Fabric blockchain. "
        "Zapis zawiera hash raportu (SHA-256), co gwarantuje jego niezmienność. "
        "Tutaj możesz zweryfikować integralność dowolnego raportu."
    )

    # Fetch reports for selectbox
    reports = api_get("/reports?limit=100")
    input_mode = st.radio(
        "Wybór raportu",
        ["📋 Z listy", "⌨️ Wpisz ręcznie"],
        horizontal=True,
        label_visibility="collapsed",
    )

    report_id = None

    if input_mode == "📋 Z listy":
        if reports:
            report_options = {}
            for r in reports:
                sev = "critical" if r["critical_count"] else (
                    "high" if r["high_count"] else "low"
                )
                icon = SEVERITY_ICONS.get(sev, "🟢")
                name = r["document_name"]
                n = r["total_findings"]
                report_options[r["id"]] = f"{icon} {name} — {n} findings"
            report_id = st.selectbox(
                "Wybierz raport",
                options=list(report_options.keys()),
                format_func=lambda x: report_options[x],
            )
        else:
            st.warning("Brak raportów. Uruchom analizę, aby wygenerować raport.")
    else:
        report_id = st.text_input(
            "ID raportu",
            placeholder="np. 3fa85f64-5717-4562-b3fc-2c963f66afa6",
        )

    if report_id:
        if st.button("🔍 Zweryfikuj w blockchain", type="primary"):
            with st.spinner("Sprawdzam rejestr blockchain..."):
                result = api_post("/blockchain/verify", json={"report_id": report_id})

            if result:
                if result.get("verified"):
                    st.success(
                        "✅ **Raport zweryfikowany** — hash zgadza się "
                        "z zapisem w blockchain!"
                    )
                    st.balloons()
                elif result.get("on_chain_hash"):
                    st.error(
                        "❌ **Hash niezgodny!** Raport mógł zostać "
                        "zmodyfikowany po rejestracji."
                    )
                else:
                    st.warning("⚠️ Raport nie znaleziony w blockchain.")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Hash obliczony (aktualny):**")
                    st.code(result.get("computed_hash", "—"), language=None)
                with col2:
                    st.markdown("**Hash w blockchain (oryginalny):**")
                    st.code(result.get("on_chain_hash", "—"), language=None)

                if result.get("blockchain_record"):
                    with st.expander("📋 Pełny rekord blockchain"):
                        st.json(result["blockchain_record"])

    st.markdown("---")
    st.markdown("### Jak to działa?")
    st.markdown("""
    ```
    [Raport compliance] → SHA-256 hash → Hyperledger Fabric (on-chain)
                                              ↓
                                    Immutable ledger record:
                                    • report_id
                                    • document_id
                                    • hash raportu
                                    • verdict (compliant / non_compliant)
                                    • timestamp
    ```

    Raz zapisany raport **nie może być zmieniony ani usunięty** z blockchaina.
    Weryfikacja porównuje aktualny hash raportu z zapisem on-chain.
    """)


# ========================
# PAGE: Status
# ========================
elif page == "⚙️ Status":
    render_header()
    st.subheader("Status serwisów")

    health = api_get("/health")
    if health:
        services = [
            ("Qdrant (Vector DB)", health.get("qdrant", False), "localhost:6333"),
            ("PostgreSQL", health.get("postgres", False), "localhost:5432"),
            ("Ollama (LLM)", health.get("ollama", False), "localhost:11434"),
            ("MLflow (MLOps)", None, "localhost:5000"),
            ("Blockchain (HLF)", health.get("blockchain", False), "localhost:3001"),
        ]

        for name, ok, url in services:
            # MLflow not in health API — check directly
            if ok is None:
                try:
                    r = httpx.get(f"http://{url}/health", timeout=5.0)
                    ok = r.status_code == 200
                except Exception:
                    ok = False

            icon = "🟢" if ok else "🔴"
            status_text = "Online" if ok else "Offline"
            st.markdown(f"{icon} **{name}** — {status_text} (`{url}`)")

        # --- Ollama details ---
        st.markdown("---")
        st.markdown("### 🤖 Ollama — modele LLM")
        try:
            ollama_resp = httpx.get(
                "http://localhost:11434/api/tags", timeout=5.0
            )
            if ollama_resp.status_code == 200:
                models = ollama_resp.json().get("models", [])
                if models:
                    for m in models:
                        name = m["name"]
                        size = m["details"]["parameter_size"]
                        quant = m["details"]["quantization_level"]
                        sz_gb = m.get("size", 0) / (1024**3)
                        st.markdown(
                            f"  - `{name}` — {size}, {quant} "
                            f"({sz_gb:.1f} GB)"
                        )
                else:
                    st.warning("Brak modeli. Zainstaluj: `ollama pull ...`")
        except Exception:
            st.error("Nie można połączyć się z Ollama")

        # --- MLflow details ---
        st.markdown("---")
        st.markdown("### 📊 MLflow — eksperymenty")
        try:
            mlflow_resp = httpx.get(
                "http://localhost:5000/api/2.0/mlflow/experiments/search",
                params={"max_results": 10},
                timeout=5.0,
            )
            if mlflow_resp.status_code == 200:
                experiments = mlflow_resp.json().get("experiments", [])
                if experiments:
                    for exp in experiments:
                        eid = exp.get("experiment_id", "?")
                        ename = exp.get("name", "?")
                        st.markdown(f"  - **{ename}** (ID: {eid})")
                else:
                    st.info("Brak eksperymentów.")
                st.markdown(
                    "[Otwórz MLflow UI →](http://localhost:5000)"
                )
        except Exception:
            st.error("Nie można połączyć się z MLflow")

        # --- System info ---
        st.markdown("---")
        st.markdown("### Informacje o systemie")
        st.markdown("""
        | Komponent | Wersja |
        |---|---|
        | **AlICjA** | v0.1.0 MVP |
        | **Model LLM** | Bielik 11B v3.0 (Q4_K_M) |
        | **Embedding** | mmlw-roberta-large (1024-dim) |
        | **Blockchain** | Hyperledger Fabric 2.5 |
        | **RAG Framework** | LlamaIndex |
        | **MLOps** | MLflow |
        """)

        st.caption(
            "👩‍⚖️ Ciocia ALA — AlICjA (AI Context Analisator) "
            "• on-premise deployment"
        )
