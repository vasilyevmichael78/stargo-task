from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    llm_provider: str = "ollama"
    llm_timeout_seconds: float = Field(default=180, gt=0, le=300)
    llm_max_retries: int = Field(default=1, ge=0, le=1)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_think: bool | None = None
    ollama_num_ctx: int = Field(default=8192, ge=2048, le=32768)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    agent_a_system_prompt_path: str = "prompts/extraction_system.txt"
    agent_b_system_prompt_path: str = "prompts/risk_graph_system.txt"
    agent_repair_system_prompt_path: str = "prompts/repair_system.txt"
    risk_context_path: str = "policies/risk_context.json"
    database_path: str = "data/mail_risk.sqlite3"
    seed_path: str = str(ROOT.parent / "mock_mailbox_data.json")
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    def path(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else ROOT / path

    @property
    def model(self):
        return self.groq_model if self.llm_provider == "groq" else self.ollama_model
