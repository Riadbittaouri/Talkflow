# generate_refresh_token.py

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CLIENT_SECRET_FILE = 'mainapp/credentials.json'   # Chemin vers votre JSON Desktop App

def main():
    # Crée le "flow" OAuth à partir du JSON Desktop App
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)

    # Ici, on demande d'ouvrir un serveur local sur le port 8080
    # L'utilisateur devra coller manuellement l'URL générée dans son navigateur.
    # À la fin, Google redirigera vers http://localhost:8080/?code=XXX
    creds = flow.run_local_server(host='localhost', port=8080, prompt='consent')

    # Une fois l'utilisateur connecté et ayant autorisé, on récupère le refresh token
    print("\n→ Copiez ceci dans vos Env Vars Render (sans les guillemets) :")
    print(f"GMAIL_CLIENT_ID={creds.client_id}")
    print(f"GMAIL_CLIENT_SECRET={creds.client_secret}")
    print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
    print("--------------------------------------------------")

if __name__ == '__main__':
    main()
