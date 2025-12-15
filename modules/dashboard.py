import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- FONCTIONS UTILITAIRES ---

def format_euro(montant):
    """Petite fonction pour afficher propre : 1250.50 €"""
    return f"{montant:,.2f} €"

def get_meteo():
    # Météo Rennes (Latitude 48.11, Longitude -1.68)
    url = "https://api.open-meteo.com/v1/forecast?latitude=48.11&longitude=-1.68&current_weather=true"
    try:
        response = requests.get(url, timeout=2) # Timeout pour ne pas bloquer si internet rame
        data = response.json()
        temp = data['current_weather']['temperature']
        return temp
    except:
        return None

def get_finance_kpi():
    try:
        df = pd.read_excel("data/budget.xlsx")
        # On force le float pour éviter les bugs
        revenus = pd.to_numeric(df[df["Type"] == "Revenu"]["Montant"], errors='coerce').sum()
        depenses = pd.to_numeric(df[df["Type"] == "Dépense"]["Montant"], errors='coerce').sum() # Pas de .abs() ici car souvent noté en positif dans la colonne montant, à vérifier selon votre saisie
        # Si vous saisissez les dépenses en positif dans excel, il faut les soustraire
        # Si vous saisissez en négatif, on additionne.
        # Dans le doute, basons-nous sur la logique du module finance : Somme Revenus - Somme Absolue Dépenses
        depenses_abs = df[df["Type"] == "Dépense"]["Montant"].abs().sum()
        solde = revenus - depenses_abs
        return solde, depenses_abs
    except:
        return 0, 0

def get_prochaine_tache():
    try:
        df = pd.read_excel("data/taches.xlsx")
        df["Date_Limite"] = pd.to_datetime(df["Date_Limite"], errors='coerce')
        # On ne garde que ce qui n'est PAS fait
        df = df[df["Statut"] != "Fait"]
        # On trie par date
        df = df.sort_values("Date_Limite")
        
        if not df.empty:
            prochaine = df.iloc[0] # La première ligne
            nom = prochaine["Tache"]
            date = prochaine["Date_Limite"]
            if pd.notnull(date):
                jours_restants = (date - datetime.today()).days
                return nom, jours_restants
            return nom, None
        return None, None
    except:
        return None, None

def get_top_objectif():
    try:
        df = pd.read_excel("data/objectifs.xlsx")
        # On prend le premier objectif de la liste qui n'est pas fini
        df["Cible"] = pd.to_numeric(df["Cible"], errors='coerce').fillna(0)
        df["Actuel"] = pd.to_numeric(df["Actuel"], errors='coerce').fillna(0)
        
        # On cherche un objectif non terminé
        for index, row in df.iterrows():
            if row["Cible"] > 0 and row["Actuel"] < row["Cible"]:
                return row["Objectif"], row["Actuel"], row["Cible"]
        return None, 0, 0
    except:
        return None, 0, 0

# --- AFFICHAGE ---
def afficher_page():
    st.title("👋 Dashboard Principal")
    current_date = datetime.today().strftime('%d/%m/%Y')
    st.caption(f"Aujourd'hui, nous sommes le {current_date}")
    
    st.markdown("---")

    # --- LIGNE 1 : KPI GLOBAUX ---
    col1, col2, col3, col4 = st.columns(4)

    # 1. Météo
    temp = get_meteo()
    col1.metric("Météo (Rennes)", f"{temp} °C" if temp else "-- °C")

    # 2. Finances
    solde, depenses_mois = get_finance_kpi()
    # On affiche propre avec format_euro
    col2.metric("💰 Solde Dispo", format_euro(solde), f"-{format_euro(depenses_mois)} sorties")

    # 3. Focus Tâche
    tache_nom, jours = get_prochaine_tache()
    if tache_nom:
        delta_str = f"{jours} jours restants" if jours is not None else "Pas de date"
        col3.metric("🔥 Priorité", tache_nom[:15]+"..." if len(tache_nom)>15 else tache_nom, delta_str)
    else:
        col3.metric("🔥 Priorité", "Rien à faire", "Tranquille !")

    # 4. Voiture (Exemple d'intégration rapide)
    try:
        df_voiture = pd.read_excel("data/voiture.xlsx")
        km_last = df_voiture["Kilometrage"].max()
        col4.metric("🚗 Kilométrage", f"{km_last:,.0f} km")
    except:
        col4.metric("🚗 Kilométrage", "--")

    st.markdown("---")

    # --- LIGNE 2 : ACCÈS RAPIDE & ACTIONS ---
    c_gauche, c_droite = st.columns([2, 1])

    with c_gauche:
        st.subheader("🚀 Suivi des Objectifs")
        # On affiche le top objectif en gros
        obj_nom, obj_actuel, obj_cible = get_top_objectif()
        
        if obj_nom:
            st.write(f"**Objectif principal : {obj_nom}**")
            prog = obj_actuel / obj_cible
            st.progress(prog)
            st.caption(f"{format_euro(obj_actuel)} sur {format_euro(obj_cible)} atteints ({prog*100:.1f}%)")
        else:
            st.info("Aucun objectif financier en cours. Allez dans l'onglet Finance pour en créer un !")

        # On pourrait ajouter ici un résumé rapide du dernier plein d'essence ou note de sport
        st.write("")
        st.info("💡 **Conseil du jour :** Pensez à vérifier vos niveaux (huile/pneus) avant le prochain long trajet.")

    with c_droite:
        st.subheader("⚡ Capture Rapide")
        
        # Formulaire Idée Rapide
        with st.form("quick_idea"):
            st.write("Une idée ? Une tâche ?")
            idea_title = st.text_input("Titre", placeholder="Ex: Acheter du pain")
            type_rapide = st.selectbox("Type", ["Idée", "A faire rapidement"])
            
            if st.form_submit_button("Ajouter 📥"):
                if idea_title:
                    try:
                        df_taches = pd.read_excel("data/taches.xlsx")
                        new_row = pd.DataFrame({
                            "Tache": [idea_title],
                            "Date_Limite": [datetime.today()],
                            "Statut": ["A faire"],
                            "Type": [type_rapide] # "Idée" ou "Devoir" selon votre choix
                        })
                        df_updated = pd.concat([df_taches, new_row], ignore_index=True)
                        df_updated.to_excel("data/taches.xlsx", index=False)
                        st.success("C'est noté !")
                    except:
                        st.error("Erreur fichier")