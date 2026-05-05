import streamlit as st
import joblib
import spacy
import re
import pandas as pd
import altair as alt
# from duckduckgo_search import DDGS
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

import csv
import os
from datetime import datetime


def salveaza_feedback(text, predictie, feedback):
    fisier_csv = "feedback_colectat.csv"
    fisier_exista = os.path.isfile(fisier_csv)

    with open(fisier_csv, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not fisier_exista:
            writer.writerow(["Data_Ora", "Text_Analizat", "Predictie_Model", "Feedback_Utilizator"])

        rezultat_text = "Fake News" if predictie == 0 else "Știre Reală"
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text, rezultat_text, feedback])

def proceseaza_feedback(text, predictie, feedback):
    salveaza_feedback(text, predictie, feedback)
    st.session_state.feedback_dat = True
    if feedback == "Corect":
        st.toast("Mulțumim pentru validare! Datele au fost salvate.", icon="✅")
    else:
        st.toast("Mulțumim pentru corectură! Vom reevalua acest tipar.", icon="🙏")


st.set_page_config(page_title="Șerloc Ro - Verifică Știrea", page_icon="🔎", layout="centered")
if 'arata_rezultate' not in st.session_state:
    st.session_state.arata_rezultate = False
if 'feedback_dat' not in st.session_state:
    st.session_state.feedback_dat = False

if 'pwa_popup_inchis' not in st.session_state:
    st.session_state.pwa_popup_inchis = False


def afiseaza_popup_mobil():
    if not st.session_state.pwa_popup_inchis:
        # textul HTML rămâne aliniat la stânga pentru a evita formatarea Markdown tip "Cod"
        st.markdown("""
<style>
#pwa-modal-container {
    display: none;
}

/*  DOAR mobil (sub 768px) */

@media (max-width: 768px) {
    #pwa-modal-container {
        display: flex;
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        z-index: 999999;
        justify-content: center;
        align-items: center;
        font-family: 'Source Sans Pro', sans-serif;
    }

    .pwa-modal-content {
        background-color: white;
        width: 90%;
        max-width: 400px;
        max-height: 90vh;
        overflow-y: auto;
        padding: 25px;
        border-radius: 24px;
        text-align: center;
        position: relative;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }

    .pwa-icon {
        background-color: #e8f0fe;
        width: 50px; height: 50px;
        border-radius: 12px;
        margin: 0 auto 15px;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px;
    }

    .pwa-title {
        font-size: 20px; font-weight: 700;
        color: #1f1f1f; margin-bottom: 8px;
    }

    .pwa-subtitle {
        font-size: 14px; color: #666;
        margin-bottom: 20px; line-height: 1.4;
    }

    .pwa-instructions {
        background-color: #f8f9fa;
        padding: 15px; border-radius: 15px;
        text-align: left; margin-bottom: 20px;
    }

    .os-title {
        font-weight: 700; font-size: 14px; color: #1f1f1f;
        margin-bottom: 12px;
    }

    .step {
        display: flex; align-items: flex-start;
        margin-bottom: 12px; font-size: 13px;
        color: #333;
    }

    .step-number {
        background-color: #3b82f6; color: white;
        min-width: 20px; height: 20px;
        border-radius: 50%; display: flex;
        align-items: center; justify-content: center;
        margin-right: 10px; font-weight: bold; font-size: 11px;
        margin-top: 2px;
    }

    .pwa-btn-primary {
        background-color: #3b82f6; color: white;
        padding: 12px; width: 100%;
        border-radius: 20px; border: none;
        font-weight: 600; margin-bottom: 10px;
        cursor: pointer;
        font-size: 15px;
    }

    .pwa-btn-secondary {
        background-color: transparent; color: #666;
        padding: 10px; width: 100%;
        border-radius: 20px; border: 1px solid #ddd;
        font-weight: 600;
        cursor: pointer;
        font-size: 15px;
    }
}

/* ascunde pop-up-ul dacă aplicația a fost deschisă de pe Home Screen */
@media all and (display-mode: standalone) {
    #pwa-modal-container {
        display: none !important;
    }
}
</style>

<div id="pwa-modal-container">
<div class="pwa-modal-content">
<div class="pwa-icon">📱</div>
<div class="pwa-title">Instalează Șerloc Ro</div>
<div class="pwa-subtitle">Adaugă aplicația pe ecranul de start pentru acces rapid, direct de pe telefonul tău.</div>

<div class="pwa-instructions">
<div class="os-title">🍎 Cum adaugi Șerloc Ro pe iPhone</div>
<div class="step">
<div class="step-number">1</div>
<div>Apasă cele <b>...</b> (trei puncte) din meniul de jos al Safari.</div>
</div>
<div class="step">
<div class="step-number">2</div>
<div>Apasă <b>Partajează</b> <i>[Share]</i> din meniul care apare.</div>
</div>
<div class="step">
<div class="step-number">3</div>
<div>Derulează în jos și apasă <b>Adăugați pe ecranul de pornire</b> <i>[Add to Home Screen]</i>.</div>
</div>
<div class="step">
<div class="step-number">4</div>
<div>Apasă <b>Adăugați</b> <i>[Add]</i> pentru a confirma.</div>
</div>

<hr style="border: 0; border-top: 1px solid #eaeaea; margin: 15px 0;">

<div class="os-title">🤖 Cum adaugi Șerloc Ro pe Android</div>
<div class="step">
<div class="step-number">1</div>
<div>Apasă meniul cu <b>⋮</b> (trei puncte) din colțul din dreapta sus al Chrome.</div>
</div>
<div class="step">
<div class="step-number">2</div>
<div>Selectează <b>Adaugă pe ecranul de pornire</b> <i>[Add to Home screen]</i>.</div>
</div>
<div class="step">
<div class="step-number">3</div>
<div>Apasă <b>Adaugă</b> pentru a confirma instalarea.</div>
</div>
</div>

<form method="get">
    <button name="inchide_pwa" value="true" class="pwa-btn-primary" onclick="document.getElementById('pwa-modal-container').style.display='none';">Am adăugat</button>
    <button name="inchide_pwa" value="true" class="pwa-btn-secondary" onclick="document.getElementById('pwa-modal-container').style.display='none';">Mai târziu</button>
</form>
</div>
</div>
""", unsafe_allow_html=True)

        # logica din Python pentru închiderea ferestrei
        query_params = st.query_params
        if query_params.get("inchide_pwa") == "true":
            st.session_state.pwa_popup_inchis = True
            st.query_params.clear()
            st.rerun()

afiseaza_popup_mobil()

@st.cache_resource
def incarca_resurse():
    nlp = spacy.load("ro_core_news_sm")

    model = joblib.load('model_final.pkl')
    vectorizer = joblib.load('vectorizator_final.pkl')

    stop_words_ro = nlp.Defaults.stop_words
    custom_stop_words = {
        "romania", "româniei", "roman", "român", "țară", "stat", "ani", "an", "anul",
        "lună", "oră", "loc", "mare", "om", "declarat", "spus", "afirmat", "spune",
        "declara", "face", "putea", "trebui", "potrivit", "conform", "foto", "video",
        "sursa", "citeste", "articol", "aici", "abonare", "newsletter", "parlament",
        "guvern", "presedinte", "președinte", "premier", "alegeri", "alegere", "electoral",
        "partid", "dan", "iohannis", "simion", "ciolacu", "georgescu", "lasconi","bolojan",
        "trump", "rusia", "ucraina", "moldova", "război", "militar", "european",
        "călin", "nicu", "nicușor", "george","georgescu", "aur", "acest", "aceasta", "aceste", "acel",
        "acces", "foarte", "mai", "mult", "doar", "e", "s", "lui", "unei", "unui", "într", "ie", "zelenski", "ucraina", "rusia", "românia", "ucrainean", "rus", "rusesc", "occidental", "nato"
    }
    stop_words_ro = stop_words_ro.union(custom_stop_words)

    return nlp, model, vectorizer, stop_words_ro


nlp, model, vectorizer, stop_words_ro = incarca_resurse()

def curatare_text_spacy(text):
    text = re.sub(r'Citește mai mult la:.*', '', text, flags=re.DOTALL)
    text = text.replace(
        "Informaţiile publicate pe site-ul Digi24.ro pot fi preluate, în conformitate cu legislația aplicabilă, doar în limita a 120 de caractere.",
        "")
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = str(text).lower()
    text = re.sub(r'[^a-zăâîșțşţ]+', ' ', text)
    doc = nlp(text)
    cuvinte_curate = [
        token.lemma_ for token in doc
        if token.text not in stop_words_ro
        and token.lemma_ not in stop_words_ro
        and not token.is_space
    ]
    return ' '.join(cuvinte_curate)


# --- INTERFAȚA WEB ---

@st.dialog("🔎 Despre Șerloc Ro")
def afiseaza_despre():
    st.write("**Șerloc Ro** a fost inspirat de tacticile agresive din mediul online – cum ar fi alertele false, reclamele înșelătoare și știrile senzaționaliste – care vizează adesea persoanele mai vulnerabile la noile tehnologii. Misiunea acestui asistent digital este de a oferi o **busolă** de încredere, ajutând utilizatorii să identifice textele manipulative al căror scop real este doar generarea de trafic sau profit.")
    st.divider()
    st.warning("**⚠️ Limitările Modelului**\n\nAplicația evaluează **stilul lingvistic** (senzaționalism, structura vocabularului) și nu **veridicitatea absolută a faptelor**.")

st.title("🕵️‍♂️ Șerloc RO")

if st.button("ℹ️ Despre aplicație și limitări", type="tertiary"):
    afiseaza_despre()

st.markdown(
    "**Aplicație demonstrativă pentru lucrarea de licență.** Sistemul folosește un model de Machine Learning (Logistic Regression) antrenat pe articole de presă din România.")

text_input = st.text_area("Verifică știrea:",
                          placeholder="Lipește aici textul articolului pe care vrei să îl analizezi...",
                          height=250)

if st.button("Analizează Textul", type="primary"):
    if len(text_input.strip()) < 50:
        st.warning("Te rog să introduci un text mai lung (minim o propoziție) pentru o analiză corectă.")
        st.session_state.arata_rezultate = False
    else:
        st.session_state.arata_rezultate = True
        st.session_state.feedback_dat = False

if st.session_state.arata_rezultate:
    with st.spinner('Analizăm tiparele lingvistice...'):
        text_curatat = curatare_text_spacy(text_input)
        text_vectorizat = vectorizer.transform([text_curatat])

        predictie = model.predict(text_vectorizat)[0]
        probabilitati = model.predict_proba(text_vectorizat)[0]

        st.markdown("---")
        st.subheader("Rezultatul Analizei:")

        col1, col2 = st.columns(2)

        with col1:
            if predictie == 0:
                st.error("⚠️ **STIL LINGVISTIC SUSPECT / SENZAȚIONALIST**")
                st.metric(label="Nivel de certitudine", value=f"{probabilitati[0]:.2%}")
            else:
                st.success("✅ **STIL JURNALISTIC STANDARD / NEUTRU**")
                st.metric(label="Nivel de certitudine", value=f"{probabilitati[1]:.2%}")


                st.markdown("---")
                st.subheader("📰 Verifică subiectul în surse oficiale")

                text_curat = re.sub(r'[^\w\s]', '', text_input)
                cuvinte_relevante = [cuv for cuv in text_curat.split() if len(cuv) > 3]
                fraza_cautare = " ".join(cuvinte_relevante[:5])

                st.markdown(f"Interoghez baza de date Google News pentru: **«{fraza_cautare}»**...")

                with st.spinner("Se preiau știrile oficiale..."):
                    try:
                        query_codificat = urllib.parse.quote(fraza_cautare)
                        url_google_rss = f"https://news.google.com/rss/search?q={query_codificat}&hl=ro&gl=RO&ceid=RO:ro"

                        # "deghizare" într-un browser normal ca să fie 100% safe
                        req = urllib.request.Request(url_google_rss, headers={'User-Agent': 'Mozilla/5.0'})

                        # citire și decodare XML-ul primit de la Google
                        with urllib.request.urlopen(req) as response:
                            xml_data = response.read()

                        root = ET.fromstring(xml_data)

                        # căutare toate știrile găsite și selectare top 3
                        stiri_gasite = root.findall('.//item')[:3]

                        if stiri_gasite:
                            for stire in stiri_gasite:
                                titlu = stire.find('title').text
                                link = stire.find('link').text
                                data_pub = stire.find('pubDate').text
                                st.markdown(f"🔹 **[{titlu}]({link})**")
                                # afișare data publicării tăind partea cu fusul orar pentru a arăta mai curat
                                st.caption(f"🗓️ Publicat la: {data_pub[:-4]}")
                        else:
                            st.warning(
                                "⚠️ Google News nu a găsit nicio știre oficială care să conțină aceste cuvinte. Indicator de **Fake News**!")

                    except Exception as e:
                        st.info("⚠️ Nu am putut interoga Google News în acest moment. Verifică conexiunea la internet.")

            # EXPLICABILITATE
        with col2:
            st.markdown("**Ce a influențat decizia?**")

            indici_cuvinte_gasite = text_vectorizat.nonzero()[1]
            nume_features = vectorizer.get_feature_names_out()
            coeficienti = model.coef_[0]

            cuvinte_importante = []
            for idx in indici_cuvinte_gasite:
                cuvant = nume_features[idx]
                coef = coeficienti[idx]
                cuvinte_importante.append({'Cuvânt': cuvant, 'Impact': coef})

            if cuvinte_importante:
                df_explicativ = pd.DataFrame(cuvinte_importante)
                df_explicativ['Absolut'] = df_explicativ['Impact'].abs()
                df_explicativ = df_explicativ.sort_values(by='Absolut', ascending=False).head(7)
                df_explicativ['Direcție'] = df_explicativ['Impact'].apply(
                    lambda x: 'Știre Reală' if x > 0 else 'Fake News'
                )

                grafic = alt.Chart(df_explicativ).mark_bar().encode(
                    x=alt.X('Impact:Q', title='Pondere în decizie (Coeficient)'),
                    y=alt.Y('Cuvânt:N', sort='-x', title=''),
                    color=alt.Color('Direcție:N',
                                    scale=alt.Scale(domain=['Știre Reală', 'Fake News'],
                                                    range=['#2e7d32', '#d32f2f']),
                                    legend=alt.Legend(title="Indică spre:")),
                    tooltip=['Cuvânt', 'Impact', 'Direcție']
                ).properties(height=350)

                st.altair_chart(grafic, width="stretch")
            else:
                st.info("Modelul nu a găsit cuvinte cheie specifice în acest text scurt.")



        st.markdown("---")

        if not st.session_state.feedback_dat:
            st.markdown("**Ajută modelul să învețe!** Cum ți s-a părut această analiză?")
            col_f1, col_f2, col_f3 = st.columns([0.4, 0.4, 0.2])

            with col_f1:
                st.button("👍 Corect", on_click=proceseaza_feedback, args=(text_input, predictie, "Corect"))

            with col_f2:
                st.button("👎 Greșit", on_click=proceseaza_feedback, args=(text_input, predictie, "Greșit"))

        else:
            st.success("✨ Mulțumim! Feedback-ul tău a fost înregistrat cu succes pentru acest text.")