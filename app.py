import re
from collections import Counter

import streamlit as st


# ---------------------------
# Mətn təmizləmə
# ---------------------------
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "because", "as", "of", "at",
    "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "to", "from", "in", "out", "on", "off",
    "over", "under", "again", "further", "then", "once", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "that", "this", "these", "those", "it", "its", "he", "she", "they", "them",
    "his", "her", "their", "we", "you", "i", "me", "my", "our", "your",
    "very", "can", "will", "just", "than", "so", "such", "too", "also"
}


def cumlelere_bol(metn: str) -> list[str]:
    metn = metn.strip()
    if not metn:
        return []
    cumleler = re.split(r'(?<=[.!?])\s+', metn)
    return [c.strip() for c in cumleler if c.strip()]


def sozlere_bol(metn: str) -> list[str]:
    sozler = re.findall(r"[a-zA-Z']+", metn.lower())
    return [s for s in sozler if s not in STOP_WORDS and len(s) > 2]


# ---------------------------
# Xülasə çıxarma
# ---------------------------
def metni_qisalt(metn: str, max_cumle: int = 3) -> str:
    cumleler = cumlelere_bol(metn)
    if len(cumleler) <= max_cumle:
        return metn

    sozler = sozlere_bol(metn)
    tezlik = Counter(sozler)

    cumle_bal = {}
    for cumle in cumleler:
        c_sozler = sozlere_bol(cumle)
        if c_sozler:
            cumle_bal[cumle] = sum(tezlik[s] for s in c_sozler)

    secilmis = sorted(cumle_bal, key=cumle_bal.get, reverse=True)[:max_cumle]

    netice = [c for c in cumleler if c in secilmis]
    return " ".join(netice)


# ---------------------------
# Açar sözlər
# ---------------------------
def acar_sozleri_cixar(metn: str, say: int = 8) -> list[str]:
    sozler = sozlere_bol(metn)
    tezlik = Counter(sozler)
    return [s for s, _ in tezlik.most_common(say)]


# ---------------------------
# Ton müəyyən etmə
# ---------------------------
POZITIV_SOZLER = {
    "good", "great", "excellent", "amazing", "happy", "success",
    "useful", "helpful", "love", "enjoy", "interesting", "strong"
}

NEGATIV_SOZLER = {
    "bad", "terrible", "sad", "angry", "problem", "hard",
    "difficult", "hate", "boring", "weak", "stress", "tired"
}


def tonu_tap(metn: str) -> str:
    sozler = sozlere_bol(metn)
    pos = sum(1 for s in sozler if s in POZITIV_SOZLER)
    neg = sum(1 for s in sozler if s in NEGATIV_SOZLER)

    if pos > neg:
        return "Pozitiv"
    elif neg > pos:
        return "Negativ"
    return "Neytral"


# ---------------------------
# Quiz sualları
# ---------------------------
def suallar_yarat(metn: str) -> list[str]:
    cumleler = cumlelere_bol(metn)
    acar = acar_sozleri_cixar(metn, 5)

    suallar = []

    if acar:
        suallar.append(f"'{acar[0]}' bu mətndə nə rol oynayır?")
    if len(acar) > 1:
        suallar.append(f"'{acar[1]}' niyə vacibdir?")
    if cumleler:
        suallar.append("Bu mətnin əsas ideyası nədir?")

    while len(suallar) < 3:
        suallar.append("Bu mətndən nə öyrəndin?")

    return suallar[:3]


# ---------------------------
# Oxu tövsiyələri
# ---------------------------
def tovsiyeler(acar: list[str]) -> list[str]:
    tips = [
        "Əvvəl xülasəni oxu, sonra tam mətnə qayıt.",
        "Açar sözləri öz sözlərinlə izah etməyə çalış.",
        "Suallara mətnə baxmadan cavab ver."
    ]

    if acar:
        tips.append(f"Bu sözlər üçün kart hazırla: {', '.join(acar[:4])}")

    return tips[:4]


# ---------------------------
# Streamlit interfeys
# ---------------------------
st.set_page_config(page_title="Smart Notes AI", page_icon="🧠")

st.title("🧠 Smart Notes AI")
st.write("Mətni daxil et və xülasə, açar sözlər, ton və suallar əldə et.")

metn = st.text_area("Mətn daxil et:", height=250)

if st.button("Analiz et"):
    if not metn.strip():
        st.warning("Zəhmət olmasa mətn daxil et.")
    else:
        xulase = metni_qisalt(metn)
        acar = acar_sozleri_cixar(metn)
        ton = tonu_tap(metn)
        suallar = suallar_yarat(metn)
        tips = tovsiyeler(acar)

        st.subheader("📌 Xülasə")
        st.write(xulase)

        st.subheader("🔑 Açar sözlər")
        st.write(", ".join(acar))

        st.subheader("🎭 Ton")
        st.write(ton)

        st.subheader("❓ Suallar")
        for i, s in enumerate(suallar, 1):
            st.write(f"{i}. {s}")

        st.subheader("📚 Tövsiyələr")
        for i, t in enumerate(tips, 1):
            st.write(f"{i}. {t}")