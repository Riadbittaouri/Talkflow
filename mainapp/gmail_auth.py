# mainapp/gmail_auth.py

import os
import base64
import logging

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# On récupère ici les 3 variables d'environnement définies dans Render
CLIENT_ID     = os.environ.get('GMAIL_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GMAIL_CLIENT_SECRET')
REFRESH_TOKEN = os.environ.get('GMAIL_REFRESH_TOKEN')

logger = logging.getLogger(__name__)

def get_gmail_credentials():
    # Vérifier que tout est bien configuré
    if not CLIENT_ID or not CLIENT_SECRET or not REFRESH_TOKEN:
        raise RuntimeError("Il manque GMAIL_CLIENT_ID, CLIENT_SECRET ou REFRESH_TOKEN")

    # Créer un objet Credentials en mémoire, à partir du refresh token
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES
    )
    # Forcer un rafraîchissement pour obtenir un access_token valide
    creds.refresh(Request())
    return creds

def create_message(sender: str, to: str, subject: str, body: str) -> dict:
    msg = MIMEMultipart()
    msg['to'], msg['from'], msg['subject'] = to, sender, subject
    msg.attach(MIMEText(body))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {'raw': raw}

def send_email_via_gmail(to: str, subject: str, body: str):
    creds = get_gmail_credentials()
    service = build('gmail', 'v1', credentials=creds)
    message = create_message('me', to, subject, body)
    service.users().messages().send(userId='me', body=message).execute()
