import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://tunelift:tunelift@localhost:5432/tunelift",
)

engine = create_engine(DATABASE_URL)


def test_connection():
    with engine.connect() as connection:
        print("Connected to TuneLift PostgreSQL database.")


if __name__ == "__main__":
    test_connection()
