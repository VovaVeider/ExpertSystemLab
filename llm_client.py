import json
import os
from pathlib import Path

import requests

from prompts import build_user_prompt


ENV_FILE = Path(__file__).resolve().parent / ".env"


def load_env_file(path: Path = ENV_FILE):
    data = {}
    if not path.exists():
        return data

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


class OllamaClient:
    def __init__(self, url=None, model=None, api_key=None, timeout=120):
        env = load_env_file()
        self.url = url or os.getenv("OLLAMA_URL") or env.get("OLLAMA_URL") or "http://localhost:11434/api/chat"
        self.model = model or os.getenv("OLLAMA_MODEL") or env.get("OLLAMA_MODEL") or "llama3.2"
        self.api_key = api_key if api_key is not None else os.getenv("OLLAMA_API_KEY") or env.get("OLLAMA_API_KEY")
        self.timeout = timeout

    def send_expert_request(self, rules, input_data, system_prompt):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": build_user_prompt(rules, input_data)},
            ],
            "stream": False,
        }

        response = requests.post(
            self.url,
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return self.extract_content(response.json())

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    @staticmethod
    def extract_content(data):
        if isinstance(data, dict):
            if "message" in data and isinstance(data["message"], dict):
                return data["message"].get(
                    "content",
                    json.dumps(data, ensure_ascii=False, indent=2),
                )
            if "response" in data:
                return data["response"]
        return json.dumps(data, ensure_ascii=False, indent=2)
