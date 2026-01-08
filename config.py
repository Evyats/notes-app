import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PORT: str
    DB_IP: str
    SOME_ENV_VAR: str

def getSettings():
    settings = Settings()
    settings.PORT = os.getenv("PORT", default="missing_env_var")
    settings.DB_IP = os.getenv("DB_IP", default="missing_env_var")
    settings.SOME_ENV_VAR = os.getenv("SOME_ENV_VAR", default="missing_env_var")
    return settings

if __name__ == "__main__":
    pass
    settings = getSettings()
    print(settings.DB_IP)
