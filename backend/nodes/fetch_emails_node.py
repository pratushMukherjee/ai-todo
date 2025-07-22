from backend.agents.email_agent import EmailAgent
email_agent = EmailAgent()

def fetch_emails_node(state):
    emails = email_agent.get_recent_emails(5)
    return {**state, "emails": emails, "step": "parse_email", "email_idx": 0} 