import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- CONFIGURATION ---
# Mettez ici l'ID du dossier Drive (c'est la fin de l'URL quand vous êtes dans le dossier)
# ex: drive.google.com/drive/u/0/folders/1A2B3C4D5E6F... -> ID = 1A2B3C4D5E6F...
FOLDER_ID = '1YQDvzh6YRlPu636roKO2YqCK81PFWNv_'
CREDENTIALS_FILE = 'credentials.json'
FILES_TO_BACKUP = [
    'data/budget.xlsx',
    'data/taches.xlsx',
    'data/voiture.xlsx', 
    'data/suivi.xlsx',
    'data/objectifs.xlsx'
]

def authenticate():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=creds)

def upload_files():
    service = authenticate()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    print(f"🔄 Démarrage de la sauvegarde du {date_str}...")

    for file_path in FILES_TO_BACKUP:
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            # On ajoute la date au nom du fichier pour garder un historique
            target_name = f"BACKUP_{date_str}_{file_name}"
            
            file_metadata = {
                'name': target_name,
                'parents': [FOLDER_ID]
            }
            media = MediaFileUpload(file_path, resumable=True)
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            print(f"✅ Fichier sauvegardé : {target_name} (ID: {file.get('id')})")
        else:
            print(f"⚠️ Fichier introuvable : {file_path}")

if __name__ == '__main__':
    upload_files()