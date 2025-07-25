from __future__ import print_function
import os.path
import pickle
import google.auth.transport.requests
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying SCOPES, delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

from google.oauth2.credentials import Credentials

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# ✅ Add this at the bottom
if __name__ == '__main__':
    service = authenticate_gmail()
    print("✅ Gmail authenticated successfully!")
