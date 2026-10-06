"""Official HTTP API adapters. Web account cookies are not used for inference."""
from dataclasses import dataclass, field
import re
import uuid
from pathlib import Path
from urllib.parse import quote
from .config import PROVIDERS, OPEN_SOURCE
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

def merged(messages):
    """Join consecutive same-role turns; several APIs require alternating roles."""
    result = []
    for m in messages:
        if result and result[-1]["role"] == m["role"]:
            result[-1] = {"role": m["role"], "content": result[-1]["content"] + "\n\n" + m["content"]}
        else: result.append({"role": m["role"], "content": m["content"]})
    return result

def base_url(settings, provider):
    """Endpoint root for open-source servers, without a trailing slash."""
    if provider == "ollama": return settings.ollama_url.rstrip("/")
    if provider == "compatible": return settings.compatible_url.rstrip("/")
    return ""

class ProviderClient:
    def __init__(self, settings, secrets):
        self.settings, self.secrets = settings, secrets
    def ready(self, provider=None):
        p = provider or self.settings.provider
        if p in OPEN_SOURCE: return bool(base_url(self.settings, p) and self.settings.model(p))
        return bool(self.secrets.get(p) and (p == "perplexity" or self.settings.model(p)))
    def chat(self, messages, system):
        p = self.settings.provider
        key, model = self.secrets.get(p), self.settings.model(p)
        messages = merged(messages)
        if p in OPEN_SOURCE: return self.open_source_chat(p, key, model, messages, system)
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

    def open_source_chat(self, p, key, model, messages, system):
        root = base_url(self.settings, p)
        if not root: raise NetworkError("Enter the open-source server address in Settings first.")
        if not model: raise NetworkError("Enter or fetch a model name in Settings first.")
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        body = {"model": model, "messages": [{"role":"system","content":system}, *messages], "stream": False}
        # Ollama is restricted to this computer, so plain HTTP is acceptable there.
        data = json_request(root + PROVIDERS[p][1], body, headers, timeout=180, loopback_http=p == "ollama")
        if p == "ollama": text = (data.get("message") or {}).get("content", "")
        else: text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        if not isinstance(text, str) or not text.strip(): raise NetworkError("No text answer returned by the open-source model.")
        return Answer(text.strip())

    def list_models(self, provider=None, key=None):
        """Model IDs the account or server offers, so users need not guess names."""
        p = provider or self.settings.provider
        key = key or self.secrets.get(p)
        if p in OPEN_SOURCE:
            root = base_url(self.settings, p)
            if not root: raise NetworkError("Enter the open-source server address first.")
            headers = {"Authorization": f"Bearer {key}"} if key else {}
            if p == "ollama":
                data = json_request(root + "/api/tags", headers=headers, timeout=10, loopback_http=True)
                names = [m.get("name") for m in data.get("models", []) if isinstance(m, dict)]
            else:
                data = json_request(root + "/models", headers=headers, timeout=15)
                names = [m.get("id") for m in data.get("data", []) if isinstance(m, dict)]
        else:
            if not key: raise NetworkError("Enter your API key first to list models.")
            if p == "openai":
                data = json_request("https://api.openai.com/v1/models", headers={"Authorization":f"Bearer {key}"}, timeout=15)
                names = [m.get("id") for m in data.get("data", []) if isinstance(m, dict)]
            elif p == "anthropic":
                data = json_request("https://api.anthropic.com/v1/models?limit=100", headers={"x-api-key":key,"anthropic-version":"2023-06-01"}, timeout=15)
                names = [m.get("id") for m in data.get("data", []) if isinstance(m, dict)]
            elif p == "gemini":
                data = json_request("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", headers={"x-goog-api-key":key}, timeout=15)
                names = [str(m.get("name", "")).removeprefix("models/") for m in data.get("models", []) if isinstance(m, dict) and "generateContent" in m.get("supportedGenerationMethods", [])]
            elif p == "deepseek":
                data = json_request("https://api.deepseek.com/models", headers={"Authorization":f"Bearer {key}"}, timeout=15)
                names = [m.get("id") for m in data.get("data", []) if isinstance(m, dict)]
            else: raise NetworkError("Perplexity uses presets; a model ID is not required.")
        names = sorted({n for n in names if isinstance(n, str) and 0 < len(n) <= 120 and not any(ord(c) < 32 for c in n)})
        if not names: raise NetworkError("No models were found. Install or enable a model first.")
        return names[:200]

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
