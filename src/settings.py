import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    @property
    def qwen_config(self):
        api_key = os.getenv("QWEN_API_KEY")
        base_url = os.getenv("QWEN_BASE_URL")
        return {"api_key": api_key, "base_url": base_url}

    @property
    def deepseek_config(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL")
        return {"api_key": api_key, "base_url": base_url}


settings = Settings()