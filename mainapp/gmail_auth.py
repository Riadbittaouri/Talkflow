import os, pickle, json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES        = ['https://www.googleapis.com/auth/gmail.send']
TOKEN_FILE    = 'token.pickle'
CLIENT_SECRET = '/etc/secrets/credentials.json'

def get_gmail_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # pas de client_config en JSON dans ENV : on lit directement le secret file
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET,
                SCOPES,
            )
            creds = flow.run_local_server(port=8080, prompt='consent')

        with open(TOKEN_FILE, 'wb') as f:
            pickle.dump(creds, f)

    return creds
