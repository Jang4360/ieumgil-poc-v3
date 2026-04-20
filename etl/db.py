import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "ieumgil"),
        user=os.getenv("POSTGRES_USER", "ieumgil"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
    )
