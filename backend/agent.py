import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_agent_response(tasks: list[str], message: str = ""):
    try:
        task_list = "\n".join([f"- {task}" for task in tasks])
        prompt = f"""You are a task assistant. The user has the following tasks:
{task_list}

User message: "{message}"

Reply with a helpful, concise recommendation on what they should do next and why.
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        resp = requests.post(url, headers=headers, json=data)
        json_data = resp.json()
        print("[DEBUG Agent Response]", json_data)

        candidates = json_data.get("candidates", [])
        if not candidates:
            raise Exception("No candidates returned.")

        return candidates[0].get("content", {}).get("parts", [])[0].get("text", "").strip()

    except Exception as e:
        print("[Fallback Agent Response]", e)
        return "Based on your tasks, I suggest starting with the most urgent one. Let me know if you need help prioritizing!"


def decompose_task(task_title: str):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{
                    "text": f"Break the following task into 3–5 subtasks:\n\n'{task_title}'"
                }]
            }]
        }

        resp = requests.post(url, headers=headers, json=data)
        json_data = resp.json()
        print("[DEBUG Decompose Response]", json_data)

        # ✅ Assign candidates properly before using it
        candidates = json_data.get("candidates", [])
        if not candidates:
            raise Exception("No candidates returned.")

        # ✅ Get and clean response text
        text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
        lines = [
            re.sub(r"^\d+\.\s+|\*\*|__", "", line.strip())
            for line in text.split("\n") if line.strip()
        ]
        return lines

    except Exception as e:
        print("[Fallback Subtasks]", e)
        return [
            f"Understand scope of '{task_title}'",
            "Break into manageable steps",
            "Assign responsibilities",
            "Set milestones"
        ]
    
    
def get_task_suggestions(user_input: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{
                "text": f"Based on this input: '{user_input}', suggest 3 useful tasks to be more productive."
            }]
        }]
    }

    resp = requests.post(url, headers=headers, json=data)

    try:
        json_data = resp.json()
        print("[DEBUG Gemini Response]", json_data)

        candidates = json_data.get("candidates", [])
        if not candidates:
            return ["No suggestions received."]

        text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
        return [line.strip() for line in text.split("\n") if line.strip()]
    except Exception as e:
        print("[ERROR parsing Gemini response]", e)
        return ["Failed to get Gemini response."]
