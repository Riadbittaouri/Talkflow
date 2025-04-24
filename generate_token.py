import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CLIENT_SECRET_FILE = os.path.join('mainapp', 'credentials.json')
TOKEN_FILE         = 'token.pickle'

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        SCOPES,
    )

    # Cette méthode ouvre le navigateur et récupère automatiquement le code
    creds = flow.run_local_server(port=8080, prompt='consent')

    with open(TOKEN_FILE, 'wb') as f:
        pickle.dump(creds, f)

    print(f"\n✅  `{TOKEN_FILE}` généré avec succès !")

if __name__ == '__main__':
    main()
