# 🎓 Student Life OS

Un Dashboard personnel complet pour gérer sa vie étudiante, ses finances et ses projets. Développé en Python avec Streamlit, hébergé sous Docker.

![Dashboard Preview](https://gemini.google.com/share/f6b7e566530a)

## ✨ Fonctionnalités

- **💸 Finances 360° :** Suivi des comptes, tri automatique, distinction Épargne (Actif) vs Dettes (Passif).
- **🚗 Module Auto :** Suivi kilométrique, calcul réel de la consommation (L/100km) et carnet d'entretien.
- **🧠 Second Cerveau :** Gestion des tâches, dates limites et capture rapide d'idées.
- **❤️ Santé & Habitudes :** Suivi du sommeil et des séances de sport.
- **☁️ Cloud Backup :** Sauvegarde automatique cryptée vers Google Drive chaque semaine.

## 🛠️ Installation

1. Clonez le repo :
   ```bash
   git clone [https://github.com/lukazgames19/student-life-os.git](https://github.com/lukazgames19/student-life-os.git)
   
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt

3. Lancez l'application :
   ```bash
   streamlit run app.py
   
🐳 Déploiement (Docker / CasaOS)
Le projet contient un Dockerfile optimisé pour CasaOS.

Importez le dossier.

Mappez le volume /app/data pour conserver vos fichiers Excel.
(Si vous voulez faire des modification et que votre docker reste à jours rajouter /app/NOM_DU_DOSSIER_OU_DU_FICHIER_QUI_EST_MODIFIÉ)

Créé par lukazgames19
