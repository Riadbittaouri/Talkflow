# mainapp/gmail_auth.py

import os
import pickle
import base64

from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Scopes requis pour envoyer des emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# En prod, ces chemins sont montés par Render :
TOKEN_FILE    = '/etc/secrets/token.pickle'
CLIENT_SECRET = '/etc/secrets/credentials.json'

def get_gmail_credentials():
    """
    Charge le token OAuth stocké dans /etc/secrets/token.pickle.
    Si le token est expiré mais contient un refresh_token, il est automatiquement rafraîchi
    et le fichier /etc/secrets/token.pickle est mis à jour.
    Sinon, une exception est levée. (Pas de run_console() en prod.)
    """
    creds = None

    # 1) Charger le token existant depuis TOKEN_FILE
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as f:
            creds = pickle.load(f)
    else:
        raise FileNotFoundError(f"Le fichier token n'a pas été trouvé : {TOKEN_FILE}")

    # 2) Si token expiré et possibilité de rafraîchir → on rafraîchit
    if creds and creds.expired and hasattr(creds, 'refresh_token') and creds.refresh_token:
        creds.refresh(Request())
        # Mise à jour du token sur le disque
        with open(TOKEN_FILE, 'wb') as f:
            pickle.dump(creds, f)
    elif not creds.valid:
        # Soit token invalide, soit pas de refresh_token : on ne peut pas continuer
        raise RuntimeError(
            "Le token OAuth n'est plus valide et ne peut pas être rafraîchi. "
            "Veuillez régénérer token.pickle et redéployer."
        )

    return creds


def create_message(sender: str, to: str, subject: str, body: str) -> dict:
    """
    Crée un objet Gmail API "raw" pour l'email à envoyer.
    """
    msg = MIMEMultipart()
    msg['to'], msg['from'], msg['subject'] = to, sender, subject
    msg.attach(MIMEText(body))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {'raw': raw}


def send_email_via_gmail(creds, to: str, subject: str, body: str):
    """
    Envoie l'email via l'API Gmail en utilisant les credentials fournis.
    """
    service = build('gmail', 'v1', credentials=creds)
    msg = create_message('me', to, subject, body)
    service.users().messages().send(userId='me', body=msg).execute()
