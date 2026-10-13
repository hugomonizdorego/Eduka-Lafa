"""Signing LAFA in to an AI, so LAFA Desktop and the Virtual Assistant get smart.

* OpenRouter: real browser sign-in (OAuth PKCE). LAFA opens openrouter.ai, the
  user logs in (Google, GitHub or e-mail) and approves; openrouter.ai returns a
  one-time code to http://localhost:3000 on this computer, and LAFA exchanges
  it for a key. Free models (ending in ":free") are chosen automatically.
* Gemini: Google gives a free API key in AI Studio (aistudio.google.com/apikey,
  signed in with a Google account). LAFA opens the page, the user copies the
  key, LAFA checks it and picks a Gemini Flash model.
* LAFA model: with Ollama on this computer, LAFA creates its own model
  ("lafa") from an open model and LAFA's personality (no internet needed after
  the download).

Keys are kept in the system keyring when one is available, otherwise only for
this session. Consumer web logins (gemini.google.com, chatgpt.com…) are used in
the AI Hub's web tabs only; LAFA never reads their cookies or tokens.
"""
import base64
import hashlib
import http.server
import secrets as _secrets
import shutil
import socketserver
import subprocess
import threading
import urllib.parse
from pathlib import Path

from .net import json_request, NetworkError

OPENROUTER_AUTH = "https://openrouter.ai/auth"
OPENROUTER_KEYS = "https://openrouter.ai/api/v1/auth/keys"
OPENROUTER_MODELS = "https://openrouter.ai/api/v1/models"
GEMINI_KEY_PAGE = "https://aistudio.google.com/apikey"
CALLBACK_PORT = 3000

def pkce_pair():
    verifier = base64.urlsafe_b64encode(_secrets.token_bytes(48)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge

def openrouter_url(port, challenge):
    callback = f"http://localhost:{port}/callback"
    return OPENROUTER_AUTH + "?" + urllib.parse.urlencode({"callback_url": callback, "code_challenge": challenge, "code_challenge_method": "S256"})

PAGE = """<!doctype html><meta charset="utf-8"><title>LAFA</title>
<body style="font-family:sans-serif;background:#e9f8f1;color:#124;display:grid;place-items:center;height:90vh">
<div style="background:#fff;padding:32px 40px;border-radius:18px;box-shadow:0 6px 24px #0002;text-align:center">
<h1>🐊 LAFA</h1><p>{text}</p></div></body>"""

class CallbackServer:
    """One-shot loopback server that receives ?code= from the browser."""
    def __init__(self, port=CALLBACK_PORT, timeout=300):
        self.code = None; self.error = None; self.event = threading.Event(); self.timeout = timeout
        outer = self
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                parts = urllib.parse.urlsplit(self.path); query = urllib.parse.parse_qs(parts.query)
                ok = parts.path == "/callback" and query.get("code")
                if ok: outer.code = query["code"][0][:512]
                else: outer.error = "No sign-in code was returned."
                body = PAGE.format(text="Signed in. You can close this tab and go back to LAFA." if ok else "Sign-in was cancelled.").encode()
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
                outer.event.set()
            def log_message(self, *args): pass
        class Server(socketserver.TCPServer):
            allow_reuse_address = True
        try: self.server = Server(("127.0.0.1", port), Handler)
        except OSError: self.server = Server(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
    def wait(self):
        thread = threading.Thread(target=self.server.serve_forever, daemon=True); thread.start()
        try:
            if not self.event.wait(self.timeout): raise NetworkError("Sign-in timed out. Try again.")
        finally:
            self.server.shutdown(); self.server.server_close()
        if not self.code: raise NetworkError(self.error or "Sign-in was cancelled.")
        return self.code

def openrouter_exchange(code, verifier):
    data = json_request(OPENROUTER_KEYS, {"code": code, "code_verifier": verifier, "code_challenge_method": "S256"}, timeout=30)
    key = data.get("key") if isinstance(data, dict) else None
    if not isinstance(key, str) or not key.startswith("sk-") or len(key) > 400: raise NetworkError("OpenRouter did not return a key.")
    return key

def openrouter_free_models():
    data = json_request(OPENROUTER_MODELS, timeout=20)
    names = [m.get("id") for m in data.get("data", []) if isinstance(m, dict) and isinstance(m.get("id"), str)]
    free = [n for n in names if n.endswith(":free") and len(n) <= 120]
    # Larger multilingual models first: they handle Tetun, Indonesian and Portuguese better.
    prefer = ("gemini", "llama-3.3", "deepseek", "qwen", "gemma", "mistral", "llama")
    free.sort(key=lambda n: next((i for i, p in enumerate(prefer) if p in n), len(prefer)))
    return free

def openrouter_signin(open_url, port=CALLBACK_PORT):
    """Run the whole browser sign-in; returns (key, model). Blocks (worker thread)."""
    verifier, challenge = pkce_pair()
    server = CallbackServer(port)
    open_url(openrouter_url(server.port, challenge))
    code = server.wait()
    key = openrouter_exchange(code, verifier)
    try: free = openrouter_free_models()
    except NetworkError: free = []
    return key, (free[0] if free else "openrouter/auto")

def gemini_connect(key):
    """Check a Gemini API key and choose a Flash model; returns the model ID."""
    key = key.strip()
    if not key or len(key) > 200 or any(c.isspace() for c in key): raise NetworkError("Paste the whole Gemini API key.")
    data = json_request("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", headers={"x-goog-api-key": key}, timeout=20)
    names = [str(m.get("name", "")).removeprefix("models/") for m in data.get("models", []) if isinstance(m, dict) and "generateContent" in m.get("supportedGenerationMethods", [])]
    if not names: raise NetworkError("This key has no Gemini models.")
    flash = sorted((n for n in names if "flash" in n and "lite" not in n and "exp" not in n and "preview" not in n), reverse=True)
    return (flash or sorted(names, reverse=True))[0]

# ------------------------------------------------------------ LAFA model (Ollama)
BASE_MODEL = "gemma3:4b"      # multilingual, small enough for school computers

def modelfile(base=BASE_MODEL):
    from .agent import SYSTEM_PERSONA
    persona = SYSTEM_PERSONA.replace('"""', "'''")
    return f'FROM {base}\nPARAMETER temperature 0.6\nPARAMETER num_ctx 8192\nSYSTEM """{persona}"""\n'

def ollama_available():
    return shutil.which("ollama") is not None

def create_lafa_model(base=BASE_MODEL, progress=lambda line: None, folder=None):
    """`ollama pull <base>` then `ollama create lafa`; returns the model name."""
    if not ollama_available(): raise NetworkError("Ollama is not installed. See ollama.com (free, open source).")
    folder = Path(folder or Path.home() / ".local/share/lafa"); folder.mkdir(parents=True, exist_ok=True)
    path = folder / "Modelfile"; path.write_text(modelfile(base), encoding="utf-8")
    for command in (["ollama", "pull", base], ["ollama", "create", "lafa", "-f", str(path)]):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
        for line in process.stdout: progress(line.strip()[-120:])
        if process.wait() != 0: raise NetworkError(f"{' '.join(command[:2])} failed.")
    return "lafa"
