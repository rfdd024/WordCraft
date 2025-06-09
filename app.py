import streamlit as st
import requests
import json
import os
import urllib.parse
import inflect  # Untuk singular/plural

# —————— Konfigurasi Awal Aplikasi ——————
st.set_page_config(
    page_title="WordCraft: English ➡️ Indonesia",
    layout="wide",
    page_icon="🧩"
)

# —————— Bagian Hero / Landing ——————
logo_url = "https://cdn-icons-png.flaticon.com/512/5228/5228257.png"
col1, col2 = st.columns([1, 3], gap="small")
with col1:
    st.image(logo_url, width=210)
with col2:
    st.markdown("<h1 style='color:#1A5276; font-size:48px;'>WordCraft</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#2874A6;'>Transform English Vocabulary into Natural Indonesian</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#566573; font-size:16px;'>"
        "Cari arti kata, sinonim, dan contoh kalimat. Kolaborasikan dengan flashcards "
        "yang disimpan dalam satu kategori, sehingga memudahkan proses belajar."
        "</p>",
        unsafe_allow_html=True
    )

st.markdown("---")
st.warning(
    "⚠️ Aplikasi ini masih dalam pengembangan dan dapat mengalami kesalahan. "
    "Silakan verifikasi kembali definisi dan terjemahan melalui sumber resmi bila diperlukan."
)

# Nama file penyimpanan tunggal
DATA_FILE = "data_store.json"

# Peta kelas kata (Inggris → Indonesia) untuk tampilan kategori
POS_MAP = {
    'noun': 'Kata Benda',
    'verb': 'Kata Kerja',
    'adjective': 'Kata Sifat',
    'adverb': 'Kata Keterangan',
    'pronoun': 'Kata Ganti',
    'preposition': 'Kata Depan',
    'conjunction': 'Kata Hubung',
    'interjection': 'Kata Seru',
    'unknown': 'Tak Diketahui'
}

# Prioritas urutan POS
POS_PRIORITY = {
    'adjective': 0,
    'adverb': 1,
    'verb': 2,
    'noun': 3,
    'pronoun': 4,
    'preposition': 5,
    'conjunction': 6,
    'interjection': 7,
    'unknown': 8
}

# —————— Muat & Simpan JSON ——————
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"dictionary": {}, "flashcards": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# —————— Terjemahan (Google Translate tidak resmi) ——————
def translate_to_indonesian(text: str) -> str:
    if not text:
        return ""
    try:
        q = urllib.parse.quote(text)
        url = (
            "https://translate.googleapis.com/translate_a/single"
            "?client=gtx&sl=en&tl=id&dt=t&q=" + q
        )
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data[0][0][0]
        return text
    except Exception:
        return text

# —————— Ambil Data dari Dictionary API ——————
def get_word_data_api(word: str):
    # Gantilah YOUR-API-KEY dengan API milikmu
    url = f"https://api.example.com/v1/entries?key=YOUR-API-KEY&query={word}" 
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

# —————— Cari & Simpan Definisi ——————
def find_definition(word: str, data: dict):
    key = word.lower()
    if key in data["dictionary"]:
        return data["dictionary"][key], False

    api_data = get_word_data_api(key)
    if not api_data:
        return None, False

    raw_defs = []
    for meaning in api_data[0].get("meanings", []):
        pos_eng = meaning.get("partOfSpeech", "unknown").lower()
        pos_id = POS_MAP.get(pos_eng, POS_MAP["unknown"])
        for d in meaning.get("definitions", []):
            en_def = d.get("definition", "") or ""
            en_ex = d.get("example", "") or ""
            id_def = translate_to_indonesian(en_def)
            id_ex = translate_to_indonesian(en_ex) if en_ex else ""
            synonyms = d.get("synonyms", []) or []

            raw_defs.append({
                "pos_eng": pos_eng,
                "partOfSpeech": pos_id,
                "definition": id_def,
                "example_en": en_ex,
                "example_id": id_ex,
                "synonyms": synonyms
            })

    raw_defs.sort(key=lambda x: POS_PRIORITY.get(x["pos_eng"], POS_PRIORITY["unknown"]))
    data["dictionary"][key] = raw_defs
    save_data(data)
    return raw_defs, True

# —————— Inisialisasi Aplikasi ——————
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
dictionary = data["dictionary"]
flashcards = data["flashcards"]

# Inisialisasi engine inflect
p = inflect.engine()

# —————— Tabs UI ——————
tab_search, tab_cards = st.tabs(["🔍 Cari Kata", "📚 Flashcards"])

with tab_search:
    st.markdown("<h3 style='color:#2E4053;'>Cari dan Pelajari Kata Baru</h3>", unsafe_allow_html=True)
    word_input = st.text_input(
        label="Masukkan kata Bahasa Inggris:",
        placeholder="contoh: handsome",
        key="input_word",
        help="Ketikkan kata dalam Bahasa Inggris, lalu tekan Enter."
    )

    if word_input:
        definitions, from_api = find_definition(word_input, data)

        if definitions:
            item = definitions[0]

            col_left, col_right = st.columns([1, 2], gap="large")

            with col_left:
                st.markdown("<h4 style='color:#117A65;'>ℹ️ Info Kata</h4>", unsafe_allow_html=True)
                st.markdown(f"- **Kelas Kata (POS):** `{item['partOfSpeech']}`")

                if item["pos_eng"] == "noun":
                    key_lower = word_input.lower()
                    singular_form = p.singular_noun(key_lower)
                    if not singular_form:
                        singular_form = key_lower
                        plural_form = p.plural(key_lower)
                    else:
                        plural_form = key_lower
                else:
                    key_lower = word_input.lower()
                    singular_form = p.singular_noun(key_lower) or key_lower
                    plural_form = key_lower if p.singular_noun(key_lower) else p.plural(key_lower)

                st.markdown(f"- **Singular (EN):** `{singular_form}`")
                st.markdown(f"- **Plural (EN):** `{plural_form}`")

                if item["synonyms"]:
                    st.markdown(f"- **Sinonim:** {', '.join(item['synonyms'][:5])}")
                else:
                    st.markdown("- **Sinonim:** (tidak tersedia)")

            with col_right:
                st.markdown("<h4 style='color:#C0392B;'>📝 Definisi & Contoh</h4>", unsafe_allow_html=True)
                st.markdown(f"**{item['partOfSpeech']}**: {item['definition']}")

                if item["example_en"]:
                    st.markdown(
                        f"<span style='color:gray;'>💬 Contoh (EN):</span> _{item['example_en']}_",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<span style='color:blue;'>📘 Contoh (ID):</span> _{item['example_id']}_",
                        unsafe_allow_html=True
                    )

            if st.button("➕ Tambah ke Flashcards", key="btn_add"):
                exists = any(card["word"].lower() == word_input.lower() for card in flashcards)
                if not exists:
                    flashcard = {
                        "word": word_input,
                        "partOfSpeech": item["partOfSpeech"],
                        "definition": item["definition"],
                        "example_en": item["example_en"],
                        "example_id": item["example_id"],
                        "synonyms": item["synonyms"][:5],
                        "singular": singular_form,
                        "plural": plural_form
                    }
                    flashcards.append(flashcard)
                    save_data(data)
                    st.success(f"Kata **{word_input}** berhasil ditambahkan ke Flashcards!")
                else:
                    st.info(f"Kata **{word_input}** sudah ada di Flashcards.")
        else:
            st.error("🚫 Definisi tidak ditemukan. Coba ketik kata lain.")

with tab_cards:
    st.markdown("<h3 style='color:#2E86C1;'>Daftar Flashcards Anda</h3>", unsafe_allow_html=True)
    if flashcards:
        grouped = {}
        for card in flashcards:
            pos = card["partOfSpeech"]
            grouped.setdefault(pos, []).append(card)

        for pos_id, cards in grouped.items():
            with st.expander(f"▶️ {pos_id} ({len(cards)} kata)"):
                for card in cards:
                    st.markdown(f"### {card['word']}")
                    st.markdown(f"- **Kelas Kata:** `{card['partOfSpeech']}`")
                    st.markdown(f"- **Singular:** `{card['singular']}` | **Plural:** `{card['plural']}`")
                    st.markdown(f"- **Definisi:** {card['definition']}")
                    if card["example_en"]:
                        st.markdown(f"- 💬 _{card['example_en']}_")
                        st.markdown(f"- 📘 _{card['example_id']}_")
                    if card["synonyms"]:
                        st.markdown(f"- **Sinonim:** {', '.join(card['synonyms'])}")
                    st.markdown("---")
    else:
        st.info("📭 Belum ada kata dalam Flashcards.")
