# auth.py

from flask import Blueprint, redirect, session, url_for, request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os

auth_bp = Blueprint('auth', __name__)

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://mail.google.com/"
]

def get_flow():
    return Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('auth.callback', _external=True)
    )

@auth_bp.route('/login')
def login():
    flow = get_flow()
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(auth_url)

@auth_bp.route('/callback')
def callback():
    flow = get_flow()
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return redirect(url_for('founder_form'))  # ✅ fixed

@auth_bp.route('/logout')
def logout():
    session.pop('credentials', None)
    return redirect(url_for('login'))  # ✅ fixed
