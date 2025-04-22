import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Scope for sending mail via Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_credentials():
    """
    Perform OAuth2 flow (first time) and return valid Gmail API credentials.
    Saves/loads tokens in token.pickle.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'mainapp/credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def create_message(sender: str, to: str, subject: str, body: str) -> dict:
    """
    Build a MIME email and base64‑encode it for the Gmail API.
    """
    message = MIMEMultipart()
    message['to']      = to
    message['from']    = sender
    message['subject'] = subject
    message.attach(MIMEText(body))
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_email_via_gmail(creds, to: str, subject: str, body: str):
    """
    Send a message via the Gmail API using the given credentials.
    """
    service = build('gmail', 'v1', credentials=creds)
    msg = create_message('me', to, subject, body)
    service.users().messages().send(userId='me', body=msg).execute()
