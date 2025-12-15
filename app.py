import streamlit as st
# Imports de vos modules
import modules.dashboard as dash
import modules.finances as fin
import modules.taches as tac
import modules.sante as san
import modules.voiture as car
# Import du NOUVEAU module style
import modules.styles as style

# Configuration de la page (DOIT RESTER EN PREMIER)
st.set_page_config(page_title="Mon Life OS", page_icon="🚀", layout="wide")

# --- 🎨 ACTIVATION DU DESIGN ---
style.apply_custom_style()
# -----------------------------


# --- SIDEBAR ---
with st.sidebar:
    st.title("🎛️ Navigation")
    page = st.radio("Aller vers :", ["Tableau de bord", "Finances 💰", "Voiture 🚗", "Tâches & Projets 📚", "Santé & Suivi 🏃"])

# --- ROUTAGE (Le Switch) ---

if page == "Tableau de bord":
    # On délègue tout le travail au fichier dashboard.py
    dash.afficher_page()
    
    # Vous pourrez ajouter d'autres résumés ici

elif page == "Finances 💰":
    # On appelle la fonction du fichier modules/finances.py
    fin.afficher_page()

elif page == "Tâches & Projets 📚":
    # On appelle la fonction du fichier modules/taches.py
    tac.afficher_page()

elif page == "Santé & Suivi 🏃":
    # On appelle la fonction du fichier modules/sante.py
    san.afficher_page()
    
elif page == "Voiture 🚗":
    car.afficher_page()