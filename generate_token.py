#!/usr/bin/env python3
# generate_token.py

import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow

# 1. Chemin vers votre credentials.json local (rédigez-le proprement, sans backslash qui poserait problème)
CLIENT_SECRET_FILE = "C:/Users/samir/Downloads/Talkflow/mainapp/credentials.json"
# ← Ajustez-le si nécessaire : vérifiez que le fichier credentials.json existe bien à cet emplacement.

# 2. Scopes nécessaires
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def main():
    """
    Ce script ouvre un navigateur pour autoriser votre compte Gmail,
    puis génère un fichier token.pickle localement.
    """
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"❌ Erreur : le fichier credentials.json n'a pas été trouvé ici : {CLIENT_SECRET_FILE}")
        return

    # 1) Préparer le flow OAuth à partir du JSON téléchargé depuis Google Cloud Console
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        SCOPES
    )

    # 2) Lancer un petit serveur local pour capter le code d'autorisation
    creds = flow.run_local_server(port=8080)

    # 3) Sauvegarder le token dans token.pickle, dans le même dossier que ce script
    with open("token.pickle", "wb") as token_file:
        pickle.dump(creds, token_file)
        print("✅  token.pickle généré avec succès dans le dossier courant.")

if __name__ == "__main__":
    main()
