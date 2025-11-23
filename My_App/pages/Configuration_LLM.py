import streamlit as st
import os

st.set_page_config(page_title="Configuration LLM", layout="wide")

# --------------------------------------------------------------------
# Chargement CSS
# --------------------------------------------------------------------
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --------------------------------------------------------------------
# HEADER FIGMA
# --------------------------------------------------------------------
st.markdown("""
<h1 class="page-title">⚙️ Configuration du Modèle LLM</h1>
<p class="page-subtitle">Gérez ici tous les paramètres liés à l’IA utilisée pour analyser et répondre aux tweets.</p>
""", unsafe_allow_html=True)

st.write("---")

# ====================================================================
#  SECTION 1 — CHOIX DU MODÈLE
# ====================================================================
st.markdown("""
<div class="section-title">🧠 Modèle utilisé</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("<label class='label'>Fournisseur</label>", unsafe_allow_html=True)
    provider = st.selectbox("Fournisseur", ["Mistral AI", "OpenAI", "Anthropic"], label_visibility="collapsed")

with col2:
    st.markdown("<label class='label'>Modèle</label>", unsafe_allow_html=True)
    model = st.selectbox(
        "Modèle",
        [
            "mistral-small",
            "mistral-medium",
            "mistral-large",
            "openai-gpt4o",
            "claude-3-haiku"
        ],
        label_visibility="collapsed"
    )

st.write("---")

# ====================================================================
#  SECTION 2 — CLÉ API
# ====================================================================
st.markdown("""
<div class="section-title">🔐 Configuration API</div>
""", unsafe_allow_html=True)

st.markdown("<label class='label'>Clé API</label>", unsafe_allow_html=True)
api_key = st.text_input("Saisir clé API", type="password", label_visibility="collapsed")

if api_key:
    st.success("Clé API enregistrée !")

st.write("---")

# ====================================================================
#  SECTION 3 — PARAMÈTRES GÉNÉRATION
# ====================================================================
st.markdown("""
<div class="section-title">🎛 Paramètres du modèle</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<label class='label'>Température</label>", unsafe_allow_html=True)
    temperature = st.slider("Température", 0.0, 1.5, 0.7, 0.1, label_visibility="collapsed")

with col2:
    st.markdown("<label class='label'>Top P</label>", unsafe_allow_html=True)
    top_p = st.slider("Top P", 0.1, 1.0, 0.9, 0.1, label_visibility="collapsed")

with col3:
    st.markdown("<label class='label'>Max Tokens</label>", unsafe_allow_html=True)
    max_tokens = st.number_input("Max Tokens", min_value=50, max_value=4000, value=350, label_visibility="collapsed")

st.write("---")

# ====================================================================
#  SECTION 4 — PROMPT SYSTEM
# ====================================================================
st.markdown("""
<div class="section-title">📄 Prompt système</div>
<p class="section-desc">Le prompt système contrôle la manière dont l’IA doit répondre aux clients.</p>
""", unsafe_allow_html=True)

default_prompt = """Tu es l’assistant officiel du SAV Free. 
Tu analyses les tweets, comprends l’émotion et génères une réponse courte, professionnelle et empathique."""

prompt_system = st.text_area("Prompt système", default_prompt, height=180, label_visibility="collapsed")

st.write("---")

# ====================================================================
#  SECTION 5 — TEST DU MODÈLE (LIVE PREVIEW)
# ====================================================================
st.markdown("""
<div class="section-title">🧪 Tester le modèle</div>
<p class="section-desc">Entrez ci-dessous un tweet pour voir la réponse générée avec les paramètres actuels.</p>
""", unsafe_allow_html=True)

input_tweet = st.text_area("Saisir un tweet", placeholder="Exemple : 'Bonjour Free, ma fibre ne fonctionne plus depuis ce matin.'", height=120, label_visibility="collapsed")

if st.button("🚀 Générer une réponse"):
    if not api_key:
        st.error("Veuillez renseigner une clé API.")
    else:
        with st.spinner("Génération en cours..."):
            # Simulation (à remplacer par appel réel API)
            st.success("Réponse générée :")
            st.info("Bonjour, navré pour la situation 😕. Pouvez-vous vérifier si le voyant LOS clignote sur votre box ? Nous restons disponibles pour vous aider !")

st.write("---")

# ====================================================================
#  SECTION 6 — RÉCAPITULATIF
# ====================================================================
st.markdown("""
<div class="section-title">📌 Récapitulatif</div>
""", unsafe_allow_html=True)

with st.expander("Voir les paramètres actuels"):
    st.json({
        "provider": provider,
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "api_key_defined": bool(api_key),
        "prompt_system": prompt_system[:100] + "..."
    })
