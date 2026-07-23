import psycopg2

from shared.config import settings


def get_connection():
    return psycopg2.connect(settings.DATABASE_URL)
