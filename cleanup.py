"""Transcript cleanup via a local Ollama LLM. Model name comes ONLY from config."""
import requests


class Cleaner:
    def __init__(self, cfg):
        self.cfg = cfg
        self.enabled = bool(cfg.get("enabled", True))
        self.model = cfg["model"]
        self.base_url = cfg.get("base_url", "http://localhost:11434").rstrip("/")
        self.min_words = int(cfg.get("min_words_for_cleanup", 10))
        if self.enabled and not self._model_available():
            print(f"Model {self.model} not installed — run: ollama pull {self.model}")
            print("Falling back to raw transcripts (cleanup disabled).")
            self.enabled = False

    def _model_available(self):
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=3)
            names = [m["name"] for m in r.json().get("models", [])]
            return any(n == self.model or n.split(":")[0] == self.model for n in names)
        except requests.RequestException:
            print(f"Ollama not reachable at {self.base_url} — cleanup disabled.")
            return False

    def clean(self, text):
        if not self.enabled or not text or len(text.split()) < self.min_words:
            return text
        try:
            prompt = (
                "Clean this transcript: remove filler words (um, uh, ah, like, you know), "
                "fix punctuation and capitalization, fix small grammar errors. "
                "Return ONLY the cleaned text, nothing else. No introductions, no explanations.\n\n"
                f"Transcript: {text}\n\nCleaned:"
            )
            r = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "system": "You are a transcript cleaner. Output ONLY the cleaned text. Never add headers, introductions, or explanations. Just the cleaned text.",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.0, "stop": ["\n\n", "Here is", "Cleaned text:"]},
                },
                timeout=30,
            )
            cleaned = r.json().get("response", "").strip()
            
            # Remove common prefixes that models add
            prefixes_to_remove = [
                "Here is the cleaned text:",
                "Here's the cleaned text:",
                "Cleaned text:",
                "Cleaned transcript:",
                "Here you go:",
            ]
            for prefix in prefixes_to_remove:
                if cleaned.lower().startswith(prefix.lower()):
                    cleaned = cleaned[len(prefix):].strip()
            
            return cleaned or text
        except requests.RequestException as e:
            print(f"Cleanup failed ({e}); using raw transcript.")
            return text