from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    """Bot configuration loaded from environment variables."""

    bot_token: str = ""
    lms_api_base_url: str = ""
    lms_api_key: str = ""
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = "coder-model"

    class Config:
        env_file = ".env.bot.secret"
        env_file_encoding = "utf-8"


config = BotConfig()
