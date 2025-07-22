import requests
import os
import re
from dotenv import load_dotenv
import spacy
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from langchain.retrievers import TimeWeightedVectorStoreRetriever
# from langchain.retrievers.vectorstore import VectorStoreRetriever

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class TaskMemory:
    def __init__(self, collection_name="tasks"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(collection_name)
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def add_task(self, task_id, text):
        embedding = self.embedder.encode(text).tolist()
        self.collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[str(task_id)]
        )

    def search(self, query, n_results=5):
        embedding = self.embedder.encode(query).tolist()
        results = self.collection.query(query_embeddings=[embedding], n_results=n_results)
        return results

class RAGRetriever:
    def __init__(self, memory: TaskMemory):
        # Use the same ChromaDB collection as TaskMemory
        from langchain.vectorstores import Chroma
        from langchain.embeddings import HuggingFaceEmbeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = Chroma(
            collection_name=memory.collection.name,
            embedding_function=self.embeddings,
            persist_directory=None  # in-memory for now
        )
        self.retriever = TimeWeightedVectorStoreRetriever(vectorstore=self.vectorstore)

    def retrieve(self, query, k=5):
        return self.retriever.get_relevant_documents(query, k=k)

class TaskAgent:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=256, chunk_overlap=32)
        self.memory = TaskMemory()
        self.rag = RAGRetriever(self.memory)

    def generate_agent_response(self, tasks: list[str], message: str = ""):
        try:
            task_list = "\n".join([f"- {task}" for task in tasks])
            prompt = f"""You are a task assistant. The user has the following tasks:\n{task_list}\n\nUser message: \"{message}\"\n\nReply with a helpful, concise recommendation.\n"""
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            resp = requests.post(url, headers=headers, json=data)
            json_data = resp.json()
            candidates = json_data.get("candidates", [])
            if not candidates:
                raise Exception("No candidates returned.")
            return candidates[0].get("content", {}).get("parts", [])[0].get("text", "").strip()
        except Exception as e:
            return "Based on your tasks, I suggest starting with the most urgent one. Let me know if you need help prioritizing!"

    def decompose_task(self, task_title: str):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            data = {"contents": [{"parts": [{"text": f"Break the following task into 3–5 subtasks:\n\n'{task_title}'"}]}]}
            resp = requests.post(url, headers=headers, json=data)
            json_data = resp.json()
            candidates = json_data.get("candidates", [])
            if not candidates:
                raise Exception("No candidates returned.")
            text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
            lines = [re.sub(r"^\d+\.\s+|\*\*|__", "", line.strip()) for line in text.split("\n") if line.strip()]
            return lines
        except Exception as e:
            return [f"Understand scope of '{task_title}'", "Break into manageable steps", "Assign responsibilities", "Set milestones"]

    def get_task_suggestions(self, user_input: str):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": f"Based on this input: '{user_input}', suggest 3 useful tasks to be more productive."}]}]}
        try:
            resp = requests.post(url, headers=headers, json=data)
            json_data = resp.json()
            print("[DEBUG Gemini Response]", json_data)
            candidates = json_data.get("candidates", [])
            if not candidates:
                print("Gemini API returned no candidates in get_task_suggestions. Response:", json_data)
                # Fallback: try to extract something from the response
                if "promptFeedback" in json_data:
                    return [json_data["promptFeedback"].get("blockReason", "No suggestions received.")]
                return ["No suggestions received."]
            text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
            # Parse and clean up the suggestions
            suggestions = [line.strip("-*• \n") for line in text.split("\n") if line.strip()]
            if not suggestions:
                return ["No suggestions parsed from Gemini response."]
            return suggestions
        except Exception as e:
            print("Error in get_task_suggestions:", e)
            return ["Failed to get Gemini response."]

    def get_email_analysis(self, email_text: str):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": f"Summarize the following email for a user. Include the main topics, requests, and any important information. Be clear and helpful.\n\nEmail:\n{email_text}"}]}]}
        try:
            resp = requests.post(url, headers=headers, json=data)
            json_data = resp.json()
            print("[DEBUG Gemini Email Analysis Response]", json_data)
            candidates = json_data.get("candidates", [])
            if not candidates:
                print("Gemini API returned no candidates in get_email_analysis. Response:", json_data)
                # Fallback: try to extract something from the response
                if "promptFeedback" in json_data:
                    return json_data["promptFeedback"].get("blockReason", "No analysis available.")
                return "No analysis available."
            text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
            if not text.strip():
                return "No analysis parsed from Gemini response."
            return text.strip()
        except Exception as e:
            print("Error in get_email_analysis:", e)
            return "Failed to get Gemini analysis."

    def parse_task_details(self, text: str):
        doc = self.nlp(text)
        dates = [ent.text for ent in doc.ents if ent.label_ in ("DATE", "TIME")]
        people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        # Simple subtasks extraction: look for lines starting with - or * or numbers
        subtasks = []
        for line in text.splitlines():
            if re.match(r"^\s*[-*\d+]", line):
                subtasks.append(line.strip("-* ").strip())
        # Use LangChain text splitter for further chunking if needed
        chunks = self.text_splitter.split_text(text)
        return {
            "dates": dates,
            "people": people,
            "subtasks": subtasks,
            "chunks": chunks
        }

    def add_task_to_memory(self, task_id, text):
        self.memory.add_task(task_id, text)

    def search_tasks(self, query, n_results=5):
        return self.memory.search(query, n_results)

    def retrieve_context(self, query, k=5):
        return self.rag.retrieve(query, k) 