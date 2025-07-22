from backend.gmail_auth import authenticate_gmail
import base64
import email

def get_recent_emails(max_results=5):
    service = authenticate_gmail()
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
    messages = results.get('messages', [])

    emails = []
    if not messages:
        print("No messages found.")
        return emails

    for msg in messages:
        message = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = message['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "(Unknown Sender)")

        # Extract email body
        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode()
        else:
            data = message['payload']['body']['data']
            body = base64.urlsafe_b64decode(data).decode()

        emails.append({
            'subject': subject,
            'from': sender,
            'body': body
        })

    return emails

if __name__ == "__main__":
    recent_emails = get_recent_emails()
    for email in recent_emails:
        print(f"📧 From: {email['from']} | Subject: {email['subject']}")
        print(f"📝 Body: {email['body']}\n")
