# mainapp/gmail_auth.py
import os, pickle, json, base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SCOPES        = ['https://www.googleapis.com/auth/gmail.send']
TOKEN_FILE    = 'token.pickle'
CLIENT_SECRET = os.environ.get('GOOGLE_CREDENTIALS_FILE', '/etc/secrets/credentials.json')

def get_gmail_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET, SCOPES
            )
            creds = flow.run_local_server(port=8080, prompt='consent')
        with open(TOKEN_FILE, 'wb') as f:
            pickle.dump(creds, f)

    return creds

def create_message(sender: str, to: str, subject: str, body: str) -> dict:
    msg = MIMEMultipart()
    msg['to'], msg['from'], msg['subject'] = to, sender, subject
    msg.attach(MIMEText(body))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {'raw': raw}

def send_email_via_gmail(creds, to: str, subject: str, body: str):
    service = build('gmail', 'v1', credentials=creds)
    msg = create_message('me', to, subject, body)
    service.users().messages().send(userId='me', body=msg).execute()
