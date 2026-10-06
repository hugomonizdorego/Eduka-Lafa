"""Official HTTP API adapters. Web account cookies are not used for inference."""
from dataclasses import dataclass, field
import re
import uuid
from pathlib import Path
from urllib.parse import quote
from .config import PROVIDERS
from .net import json_request, request, NetworkError

@dataclass
class Answer:
    text: str
    sources: list = field(default_factory=list)

def responses_answer(data):
    pieces, sources = [], []
    for item in data.get("output", []):
        if item.get("type") == "search_results":
            for r in item.get("results", []):
                if r.get("url"): sources.append((r.get("title", r["url"]), r["url"]))
        for c in item.get("content", []):
            if c.get("type") == "output_text": pieces.append(c.get("text", ""))
            for a in c.get("annotations", []):
                if a.get("type") == "url_citation" and a.get("url"):
                    sources.append((a.get("title", a["url"]), a["url"]))
    return Answer("\n".join(pieces).strip(), list(dict.fromkeys(sources)))

class ProviderClient:
    def __init__(self, settings, secrets):
        self.settings, self.secrets = settings, secrets
    def ready(self, provider=None):
        p = provider or self.settings.provider
        return bool(self.secrets.get(p) and (p == "perplexity" or self.settings.model(p)))
    def chat(self, messages, system):
        p = self.settings.provider
        key, model = self.secrets.get(p), self.settings.model(p)
        if not key: raise NetworkError("Set your API key in Settings first.")
        if p != "perplexity" and not model: raise NetworkError("Enter a model ID supported by your account in Settings.")
        endpoint = PROVIDERS[p][1]
        if p == "openai":
            data = json_request(endpoint, {"model":model,"instructions":system,"input":messages,"store":False}, {"Authorization":f"Bearer {key}"})
            answer = responses_answer(data)
        elif p == "perplexity":
            body = {"preset": self.settings.preset, "input":[{"role":"system","content":system}, *messages]}
            data = json_request(endpoint, body, {"Authorization":f"Bearer {key}"})
            answer = responses_answer(data)
        elif p == "gemini":
            if not re.fullmatch(r"[A-Za-z0-9._-]+", model): raise NetworkError("Invalid Gemini model ID.")
            contents = [{"role":"model" if m["role"]=="assistant" else "user", "parts":[{"text":m["content"]}]} for m in messages]
            data = json_request(f"{endpoint}/models/{quote(model)}:generateContent", {"contents":contents,"systemInstruction":{"parts":[{"text":system}]}}, {"x-goog-api-key":key})
            answer = Answer("\n".join(part.get("text", "") for c in data.get("candidates", [])[:1] for part in c.get("content", {}).get("parts", []) if not part.get("thought")))
            for c in data.get("candidates", [])[:1]:
                for chunk in c.get("groundingMetadata", {}).get("groundingChunks", []):
                    web = chunk.get("web", {})
                    if web.get("uri"): answer.sources.append((web.get("title", web["uri"]), web["uri"]))
        elif p == "anthropic":
            data = json_request(endpoint, {"model":model,"max_tokens":2048,"system":system,"messages":messages}, {"x-api-key":key,"anthropic-version":"2023-06-01"})
            answer = Answer("\n".join(c.get("text", "") for c in data.get("content", []) if c.get("type")=="text"))
        else:
            data = json_request(endpoint, {"model":model,"messages":[{"role":"system","content":system}, *messages],"stream":False}, {"Authorization":f"Bearer {key}"})
            answer = Answer(data.get("choices", [{}])[0].get("message", {}).get("content", "") or "")
        if not answer.text: raise NetworkError("No text answer returned. The model may have refused or used an unsupported output type.")
        return answer

    def transcribe(self, path):
        key = self.secrets.get("openai")
        if not key: raise NetworkError("Voice input requires an OpenAI API key, even with another chat provider.")
        path = Path(path)
        if path.stat().st_size > 10_000_000: raise NetworkError("Recording is too large.")
        boundary = "lafa-" + uuid.uuid4().hex
        fields = []
        for name, value in [("model", self.settings.transcription_model)]:
            fields.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
        fields.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="recording.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode()+path.read_bytes()+b"\r\n")
        fields.append(f"--{boundary}--\r\n".encode())
        import json
        raw = request("https://api.openai.com/v1/audio/transcriptions", b"".join(fields), {"Authorization":f"Bearer {key}", "Content-Type":f"multipart/form-data; boundary={boundary}"})
        try: text = json.loads(raw).get("text", "").strip()
        except ValueError: raise NetworkError("Invalid transcription response.") from None
        if not text: raise NetworkError("No speech detected. Try again.")
        return text
