import os, pickle, json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
TOKEN_FILE = 'token.pickle'

def get_gmail_credentials():
    creds = None
    # 1) On recharge le token existant s’il y en a un
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as f:
            creds = pickle.load(f)

    # 2) Si pas de credentials valides, on rafraîchit ou on relance le flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # ici on lit la variable d'env contenant tout le JSON du credentials.json
            client_config = json.loads(os.environ['GOOGLE_CREDENTIALS'])
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            # en prod on ne peut pas faire run_local_server, 
            # mais Render expose un port, donc ça fonctionne
            creds = flow.run_local_server(port=8080, prompt='consent')

        # on sauvegarde pour les prochaines exécutions
        with open(TOKEN_FILE, 'wb') as f:
            pickle.dump(creds, f)

    return creds

def create_message(sender, to, subject, body):
    msg = MIMEMultipart()
    msg['to'], msg['from'], msg['subject'] = to, sender, subject
    msg.attach(MIMEText(body))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {'raw': raw}

def send_email_via_gmail(creds, to, subject, body):
    svc = build('gmail', 'v1', credentials=creds)
    msg = create_message('me', to, subject, body)
    svc.users().messages().send(userId='me', body=msg).execute()
