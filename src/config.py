import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PORT: str
    DATABASE_URL: str

def getSettings():
    settings = Settings()
    settings.PORT = os.getenv("PORT", default="missing_env_var")
    settings.DATABASE_URL = os.getenv("DATABASE_URL", default="missing_env_var")
    return settings

if __name__ == "__main__":
    pass
    settings = getSettings()
    print(settings.DATABASE_URL)
