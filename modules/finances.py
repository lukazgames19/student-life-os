import streamlit as st
import pandas as pd
import plotly.express as px

# Chemins des fichiers
FILE_BUDGET = "data/budget.xlsx"
FILE_GOALS = "data/objectifs.xlsx"

# --- CHARGEMENT ---
def load_budget():
    try:
        df = pd.read_excel(FILE_BUDGET)
        df["Compte"] = df["Compte"].astype(str).replace("nan", "Inconnu")
        df["Catégorie"] = df["Catégorie"].fillna("Autre")
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df = df.sort_values(by="Date", ascending=True).reset_index(drop=True)
        df["Montant"] = df["Montant"].astype(float)
        return df
    except FileNotFoundError:
        return None

def load_goals():
    try:
        df = pd.read_excel(FILE_GOALS)
        # Nettoyage des chiffres (évite le bug des espaces ou texte)
        df["Cible"] = pd.to_numeric(df["Cible"], errors='coerce').fillna(0)
        df["Actuel"] = pd.to_numeric(df["Actuel"], errors='coerce').fillna(0)
        
        # Gestion du Type (Épargne vs Dette)
        if "Type" not in df.columns:
            df["Type"] = "Épargne" # Par défaut, tout est épargne si la colonne n'existe pas
            
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Objectif", "Cible", "Actuel", "Date_Limite", "Type"])

# --- SAUVEGARDE ---
def save_budget(df):
    try:
        df.to_excel(FILE_BUDGET, index=False)
        st.success("✅ Budget mis à jour !")
    except Exception as e:
        st.error(f"Erreur : {e}")

def save_goals(df):
    try:
        df.to_excel(FILE_GOALS, index=False)
        st.toast("✅ Objectifs mis à jour !", icon="🎯")
    except Exception as e:
        st.error(f"Erreur : {e}")

# --- AFFICHAGE ---
def afficher_page():
    st.title("💸 Finances & Patrimoine")
    
    df_budget = load_budget()
    df_goals = load_goals()
    
    if df_budget is not None:
        tab_visu, tab_epargne, tab_edit = st.tabs(["📊 Analyse Budget", "🏦 Épargne vs Dettes", "📝 Journal & Édition"])
        
        # === ONGLET 1 : ANALYSE BUDGET ===
        with tab_visu:
            liste_comptes = df_budget["Compte"].unique()
            selection = st.multiselect("Filtrer par compte", liste_comptes, default=liste_comptes)
            df_filtre = df_budget[df_budget["Compte"].isin(selection)]
            
            rev = df_filtre[df_filtre["Type"] == "Revenu"]["Montant"].sum()
            dep = df_filtre[df_filtre["Type"] == "Dépense"]["Montant"].abs().sum()
            solde = rev - dep
            
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Solde Période", f"{solde:,.2f} €")
            c2.metric("📥 Revenus", f"{rev:,.2f} €")
            c3.metric("📤 Dépenses", f"{dep:,.2f} €")
            
            st.divider()
            
            dep_data = df_filtre[df_filtre["Type"] == "Dépense"].copy()
            if not dep_data.empty:
                dep_data["Montant"] = dep_data["Montant"].abs()
                fig = px.pie(dep_data, values='Montant', names='Catégorie', title='Répartition des Dépenses', hole=0.3)
                st.plotly_chart(fig, use_container_width=True)

        # === ONGLET 2 : ÉPARGNE VS DETTES (Séparation claire) ===
        with tab_epargne:
            # Séparation des données
            df_epargne = df_goals[df_goals["Type"] == "Épargne (Actif)"]
            df_dette = df_goals[df_goals["Type"] == "Remboursement (Passif)"]

            # --- PARTIE 1 : ÉPARGNE (Ce que je possède) ---
            st.subheader("💰 Mon Épargne (Actifs)")
            st.caption("Argent disponible ou bloqué qui m'appartient.")
            
            total_dispo = df_epargne["Actuel"].sum()
            st.metric("Total Épargné", f"{total_dispo:,.2f} €")
            
            for index, row in df_epargne.iterrows():
                if row["Cible"] > 0:
                    prog = min(row["Actuel"] / row["Cible"], 1.0)
                else:
                    prog = 0
                st.write(f"**{row['Objectif']}** ({row['Actuel']}€ / {row['Cible']}€)")
                st.progress(prog)
            
            st.divider()

            # --- PARTIE 2 : DETTES & PROJETS (Ce que je dois payer) ---
            st.subheader("📉 Dettes & Financements (Passifs)")
            st.caption("Prêts étudiants, achats à venir... Argent à sortir.")
            
            if not df_dette.empty:
                for index, row in df_dette.iterrows():
                    if row["Cible"] > 0:
                        prog = min(row["Actuel"] / row["Cible"], 1.0)
                    else:
                        prog = 0
                    # On change la formulation pour bien différencier
                    st.write(f"**{row['Objectif']}** (Payé : {row['Actuel']}€ sur {row['Cible']}€)")
                    st.progress(prog)
            else:
                st.info("Aucune dette ou financement en cours. Bravo ! 👏")

            st.markdown("---")
            
            # --- TABLEAU DE GESTION ---
            st.write("### 🔨 Gérer mes cagnottes et dettes")
            st.info("💡 Utilisez la colonne **Type** pour classer vos lignes : 'Épargne' (Haut) ou 'Remboursement' (Bas).")
            
            edited_goals = st.data_editor(
                df_goals, 
                num_rows="dynamic",
                use_container_width=True,
                key="editor_goals_split",
                column_config={
                    "Type": st.column_config.SelectboxColumn(
                        "Type",
                        options=["Épargne (Actif)", "Remboursement (Passif)"],
                        required=True
                    ),
                    "Cible": st.column_config.NumberColumn("Objectif Total (€)", format="%d €"),
                    "Actuel": st.column_config.NumberColumn("Déjà mis/payé (€)", format="%d €"),
                    "Date_Limite": st.column_config.DateColumn(format="DD/MM/YYYY")
                }
            )
            if st.button("💾 Sauvegarder Objectifs"):
                save_goals(edited_goals)
                st.rerun()

        # === ONGLET 3 : ÉDITION GLOBALE ===
        with tab_edit:
            st.subheader("📝 Journal des Transactions (Budget)")
            col_conf_budget = {
                "Montant": st.column_config.NumberColumn(step=0.01, format="%.2f €"),
                "Type": st.column_config.SelectboxColumn(options=["Revenu", "Dépense", "Virement Interne"], required=True),
                "Date": st.column_config.DateColumn(format="DD/MM/YYYY"),
            }
            
            df_budget_edit = st.data_editor(
                df_budget, 
                num_rows="dynamic", 
                column_config=col_conf_budget, 
                use_container_width=True, 
                key="editor_budget_main"
            )
            
            if st.button("💾 Sauvegarder le Budget"):
                save_budget(df_budget_edit)
                st.rerun()

    else:
        st.warning("⚠️ Fichier 'budget.xlsx' introuvable.")