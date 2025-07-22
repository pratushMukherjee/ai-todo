from backend import gmail_reader

class EmailAgent:
    def get_recent_emails(self, max_results=5):
        return gmail_reader.get_recent_emails(max_results) 