import os

class Settings:
    ENV = os.getenv("ENV", "prod")
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")
    VECTOR_DB_PATH = "/data/vectors"
    MAX_TOKENS_PER_MIN = 50000

settings = Settings()
