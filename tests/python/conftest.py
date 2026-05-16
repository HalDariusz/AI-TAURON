import pytest
from src.python.domain.models import Document, DocumentType

SAMPLE_LEGAL_TEXT = """\
Rozdział I
Przepisy ogólne

Art. 1. Ustawa określa zasady kształtowania polityki energetycznej państwa, \
zasady i warunki zaopatrzenia i użytkowania paliw i energii, w tym ciepła, \
oraz działalność przedsiębiorstw energetycznych, a także określa organy \
właściwe w sprawach gospodarki paliwami i energią.

Art. 2. 1. Użyte w ustawie określenia oznaczają:
1) energia – energię elektryczną i ciepło;
2) paliwa – paliwa stałe, ciekłe i gazowe będące nośnikami energii chemicznej.

Art. 3. Polityka energetyczna państwa określa:
1) bilans paliwowo-energetyczny kraju;
2) zdywersyfikowanie struktury nośników energii;
3) bezpieczeństwo energetyczne kraju.

Rozdział II
Dostarczanie paliw i energii

Art. 4. 1. Przedsiębiorstwo energetyczne zajmujące się przesyłaniem lub \
dystrybucją paliw gazowych lub energii jest obowiązane utrzymywać zdolność \
urządzeń, instalacji i sieci do realizacji zaopatrzenia w te paliwa lub energię \
w sposób ciągły i niezawodny, przy zachowaniu obowiązujących wymagań jakościowych.

Art. 4j. 1. Odbiorca paliw gazowych lub energii elektrycznej może wypowiedzieć \
umowę zawartą na czas nieokreślony.
2. Wypowiedzenie umowy przez odbiorcę nie wymaga podania przyczyny.
3. W przypadku wypowiedzenia umowy okres wypowiedzenia nie może być dłuższy niż \
jeden miesiąc, ze skutkiem na koniec miesiąca kalendarzowego.
3a. Odbiorca w gospodarstwie domowym może wypowiedzieć umowę zawartą na czas \
określony z zachowaniem miesięcznego okresu wypowiedzenia.

Art. 5. 1. Dostarczanie paliw gazowych lub energii odbywa się, po uprzednim \
przyłączeniu do sieci, na podstawie umowy sprzedaży i umowy o świadczenie usług \
przesyłania lub dystrybucji.
2. Umowa sprzedaży energii elektrycznej powinna zawierać co najmniej:
1) oznaczenie stron umowy;
2) miejsce i datę zawarcia umowy;
3) okres obowiązywania umowy;
4) sposób i tryb rozwiązywania sporów.
"""

SAMPLE_CONTRACT_TEXT = """\
UMOWA SPRZEDAŻY ENERGII ELEKTRYCZNEJ NR 2024/001
zawarta w dniu 15 marca 2024 r. w Katowicach

§ 1. Przedmiot umowy
1. Przedmiotem niniejszej umowy jest sprzedaż energii elektrycznej przez Sprzedawcę \
na rzecz Odbiorcy do punktu poboru energii.

§ 2. Definicje
1. Odbiorca – osoba fizyczna nabywająca energię na potrzeby własne.
2. Sprzedawca – przedsiębiorstwo energetyczne posiadające koncesję.

§ 3. Warunki sprzedaży
1. Sprzedawca zobowiązuje się do sprzedaży energii elektrycznej na warunkach \
określonych w niniejszej umowie oraz obowiązujących przepisach prawa.

§ 4. Cena i rozliczenia
1. Cena energii elektrycznej jest zgodna z taryfą G11-2022 zatwierdzoną \
decyzją Prezesa URE z dnia 17 grudnia 2022 r.
2. Rozliczenia dokonywane są w okresach miesięcznych.

§ 5. Prawa i obowiązki stron
1. Odbiorca ma prawo do informacji o warunkach umowy.

§ 6. Odpowiedzialność stron
1. Strony ponoszą odpowiedzialność za niewykonanie zobowiązań.

§ 7. Okres obowiązywania i wypowiedzenie
1. Umowa zostaje zawarta na czas nieokreślony.
2. Okres wypowiedzenia wynosi 3 miesiące.

§ 8. Postanowienia końcowe
1. W sprawach nieuregulowanych stosuje się przepisy Kodeksu cywilnego.
"""


@pytest.fixture
def sample_legal_document() -> Document:
    return Document(
        filename="prawo_energetyczne.pdf",
        document_type=DocumentType.LEGAL_ACT,
        raw_text=SAMPLE_LEGAL_TEXT,
    )


@pytest.fixture
def sample_contract_document() -> Document:
    return Document(
        filename="umowa_sprzedaz_01.pdf",
        document_type=DocumentType.CONTRACT,
        raw_text=SAMPLE_CONTRACT_TEXT,
    )
